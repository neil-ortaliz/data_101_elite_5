import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union


class PortfolioCalculator:
    """
    PortfolioCalculator handles metrics for card portfolios:
    - Value & performance metrics
    """

    def __init__(self, portfolio_df: pd.DataFrame, price_history_df: pd.DataFrame, card_metadata_df: pd.DataFrame) -> None:
        self.portfolio = portfolio_df.copy()
        self.price_history = price_history_df.copy()
        self.card_metadata = card_metadata_df.copy()

        # Clean portfolio
        if not self.portfolio.empty:
            self.portfolio["buy_date"] = pd.to_datetime(
                self.portfolio.get("buy_date"), errors="coerce"
            ).dt.tz_localize(None)
            self.portfolio["buy_price"] = pd.to_numeric(
                self.portfolio.get("buy_price"), errors="coerce"
            ).fillna(0)
            self.portfolio["quantity"] = pd.to_numeric(
                self.portfolio.get("quantity"), errors="coerce"
            ).fillna(0)

        # Clean price history
        if not self.price_history.empty:
            self.price_history["date"] = pd.to_datetime(
                self.price_history.get("date"), errors="coerce"
            ).dt.tz_localize(None)

    # -------------------- HELPER FUNCTIONS --------------------
    def format_value(self, value: float, sign: str = "") -> str:
        """Format number with $ and K/M suffixes."""
        if abs(value) >= 1_000_000:
            return f"{sign}${abs(value)/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"{sign}${abs(value)/1_000:.1f}K"
        else:
            return f"{sign}${abs(value):.2f}"

    # -------------------- VALUE METRICS --------------------
    def get_current_prices(self, days: Optional[int] = None) -> Dict[str, float]:
        if self.portfolio.empty or self.price_history.empty:
            return {}

        if days is None:
            latest_prices = (
                self.price_history
                .sort_values(["id", "date"], ascending=[True, False])
                .groupby("id")
                .first()
            )
        else:
            target_date = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
            prices_on_date = self.price_history[self.price_history["date"] == target_date]
            latest_prices = prices_on_date.set_index("id")

        portfolio_ids = set(self.portfolio["id"].unique())
        return latest_prices.loc[latest_prices.index.isin(portfolio_ids), "market"].fillna(0).to_dict()

    def calculate_total_portfolio_value(self, days: Optional[int] = None) -> Dict[str, Union[float, str]]:
        if self.portfolio.empty:
            return {
                "value": 0.0,
                "formatted": "$0.00",
                "past_value": 0.0,
                "past_formatted": "$0.00",
                "percent_change": 0.0,
                "percent_change_formatted": "0.0%"
            }
        
        current_prices = self.get_current_prices(days=None)  # always latest
        total_value = sum(current_prices.get(row["id"], 0) * row["quantity"] for _, row in self.portfolio.iterrows())
        
        if days is None:
            return {
                "value": total_value,
                "formatted": self.format_value(total_value),
                "past_value": 0.0,
                "past_formatted": "$0.00",
                "percent_change": 0.0,
                "percent_change_formatted": "0.0%"
            }
        
        past_prices = self.get_current_prices(days=days)
        past_value = sum(past_prices.get(row["id"], 0) * row["quantity"] for _, row in self.portfolio.iterrows())
        
        if past_value == 0:
            percent_change = 0.0
            percent_change_formatted = "0.0%"
        else:
            percent_change = (total_value - past_value) / past_value * 100
            sign = "+" if percent_change >= 0 else "-"
            percent_change_formatted = f"{sign}{abs(percent_change):.1f}%"
        
        return {
            "value": total_value,
            "formatted": self.format_value(total_value),
            "past_value": past_value,
            "past_formatted": self.format_value(past_value),
            "percent_change": percent_change,
            "percent_change_formatted": percent_change_formatted,
        }

    def calculate_total_gain_loss(self, days: Optional[int] = None) -> Dict[str, Any]:
        if self.portfolio.empty:
            return {
                "gain_loss_value": 0.0,
                "gain_loss_pct": 0.0,
                "formatted_value": "$0.00",
                "formatted_pct": "0.0%",
                "type": "neutral",
            }

        current_prices = self.get_current_prices(days=None)
        total_current = sum(current_prices.get(row["id"], 0) * row["quantity"] for _, row in self.portfolio.iterrows())

        if days is None:
            total_cost = sum(row["buy_price"] * row["quantity"] for _, row in self.portfolio.iterrows())
        else:
            past_prices = self.get_current_prices(days=days)
            if not past_prices:
                total_cost = sum(row["buy_price"] * row["quantity"] for _, row in self.portfolio.iterrows())
            else:
                total_cost = sum(past_prices.get(row["id"], row["buy_price"]) * row["quantity"] for _, row in self.portfolio.iterrows())

        gain_loss_value = total_current - total_cost
        gain_loss_pct = 0.0 if total_cost == 0 else (gain_loss_value / total_cost) * 100
        formatted_value = self.format_value(gain_loss_value, sign="+" if gain_loss_value>=0 else "-")
        formatted_pct = f"{gain_loss_pct:+.1f}%"
        type_ = "gain" if gain_loss_value > 0 else ("loss" if gain_loss_value < 0 else "neutral")

        return {
            "gain_loss_value": gain_loss_value,
            "gain_loss_pct": gain_loss_pct,
            "formatted_value": formatted_value,
            "formatted_pct": formatted_pct,
            "type": type_,
        }

    def calculate_card_count(self, days: Optional[int] = None) -> Dict[str, Union[int, str]]:
        if self.portfolio.empty:
            return {"count": 0, "unique_cards": 0, "formatted": "0 cards", "change": 0, "change_formatted": "+0 cards"}

        total_quantity = int(self.portfolio["quantity"].sum())
        unique_cards = len(self.portfolio)

        if days is None:
            return {"count": total_quantity, "unique_cards": unique_cards, "formatted": f"{total_quantity:,} cards", "change": 0, "change_formatted": "+0 cards"}

        cutoff_date = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
        past_portfolio = self.portfolio[self.portfolio["buy_date"] <= cutoff_date]
        past_total_quantity = int(past_portfolio["quantity"].sum())
        change = total_quantity - past_total_quantity
        sign = "+" if change >= 0 else "-"
        change_formatted = f"{sign}{abs(change):,} cards"

        return {"count": total_quantity, "unique_cards": unique_cards, "formatted": f"{total_quantity:,} cards", "change": change, "change_formatted": change_formatted}

    def calculate_average_card_value(self, days: Optional[int] = None) -> Dict[str, Union[float, str]]:
        counts = self.calculate_card_count(days=days)
        current_count = counts["count"]

        if current_count == 0:
            return {"value": 0.0, "formatted": "$0.00", "past_value": 0.0, "past_formatted": "$0.00", "change": 0.0, "change_formatted": "$0.00 (0.0%)"}

        total_value = self.calculate_total_portfolio_value(days=None)["value"]
        avg_current = total_value / current_count

        if days is None:
            return {"value": avg_current, "formatted": self.format_value(avg_current), "past_value": 0.0, "past_formatted": "$0.00", "change": 0.0, "change_formatted": "0.0%"}

        past_total_value = self.calculate_total_portfolio_value(days=days)["value"]
        past_count = counts["count"] - counts["change"]
        avg_past = 0 if past_count == 0 else past_total_value / past_count

        change = avg_current - avg_past
        percent_change = 0 if avg_past == 0 else (change / avg_past) * 100
        sign = "+" if percent_change >= 0 else "-"
        change_formatted = f"{sign}{abs(percent_change):.1f}%"

        return {"value": avg_current, "formatted": self.format_value(avg_current), "past_value": avg_past, "past_formatted": self.format_value(avg_past), "change": change, "change_formatted": change_formatted}

    # -------------------- PERFORMANCE METRICS --------------------
    def calculate_time_weighted_returns(self) -> Optional[float]:
        if self.portfolio.empty or self.price_history.empty:
            return None

        twr_list = []
        for card_id in self.portfolio["id"].unique():
            card_prices = self.price_history[self.price_history["id"] == card_id].sort_values("date")
            if len(card_prices) < 2:
                continue
            period_returns = card_prices["market"].pct_change().dropna()
            twr_list.append((1 + period_returns).prod() - 1)
        if not twr_list:
            return None
        return np.mean(twr_list) * 100

    def compare_to_benchmark(self, benchmark_series: pd.Series) -> Optional[Dict[str, float]]:
        if self.portfolio.empty or self.price_history.empty or benchmark_series.empty:
            return None

        pivot = self.price_history.pivot(index="date", columns="id", values="market")
        quantities = self.portfolio.set_index("id")["quantity"]
        portfolio_values = (pivot * quantities).sum(axis=1).sort_index()
        if len(portfolio_values) < 2:
            return None
        portfolio_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
        benchmark_return = (benchmark_series.iloc[-1] / benchmark_series.iloc[0] - 1) * 100
        excess_return = portfolio_return - benchmark_return
        return {"portfolio_return": portfolio_return, "benchmark_return": benchmark_return, "excess_return": excess_return}

    def calculate_gain_loss_per_card(self) -> pd.DataFrame:
        if self.portfolio.empty or self.price_history.empty:
            return pd.DataFrame()
        
        current_prices = self.get_current_prices()
        portfolio_copy = self.portfolio.copy()
        portfolio_copy = portfolio_copy.merge(self.card_metadata[['id', 'name', 'setName']], on='id', how='left')

        portfolio_copy['current_price'] = portfolio_copy['id'].map(current_prices)
        portfolio_copy['total_cost'] = portfolio_copy['buy_price'] * portfolio_copy['quantity']
        portfolio_copy['total_current_value'] = portfolio_copy['current_price'] * portfolio_copy['quantity']
        portfolio_copy['gain_loss_value'] = portfolio_copy['total_current_value'] - portfolio_copy['total_cost']
        portfolio_copy['gain_loss_pct'] = np.where(portfolio_copy['total_cost'] == 0, None, (portfolio_copy['gain_loss_value'] / portfolio_copy['total_cost']) * 100)
        portfolio_copy['type'] = portfolio_copy['gain_loss_value'].apply(lambda val: 'gain' if val > 0 else ('loss' if val < 0 else 'neutral'))

        return portfolio_copy[['name', 'setName', 'quantity', 'buy_price', 'current_price', 'gain_loss_value', 'gain_loss_pct', 'type']]

    # -------------------- RISK METRICS --------------------
    def calculate_diversity_score(self) -> Dict[str, Any]:
        if self.portfolio.empty or self.card_metadata.empty:
            return {'score': 0, 'level': 'low', 'description': 'No data available.'}
        
        portfolio_with_meta = self.portfolio.merge(self.card_metadata[['id', 'setId', 'rarity']], on='id', how='left')
        unique_sets = portfolio_with_meta['setId'].nunique()
        unique_rarities = portfolio_with_meta['rarity'].nunique()
        total_cards = portfolio_with_meta['quantity'].sum()

        if total_cards == 0:
            return {'score': 0, 'level': 'low', 'description': 'No cards in portfolio.'}
        
        set_shares = portfolio_with_meta.groupby('setId')['quantity'].sum() / total_cards
        herfindahl = (set_shares ** 2).sum()
        diversity_score = (1 - herfindahl) * 100
        diversity_score *= (1 + unique_sets / 10) * (1 + unique_rarities / 5)
        diversity_score = min(diversity_score, 100)

        if diversity_score >= 70:
            level = "high"
            description = "Your portfolio is well-diversified across multiple sets and rarities."
        elif diversity_score >= 40:
            level = "medium"
            description = "Moderate diversification. Consider adding cards from more sets."
        else:
            level = "low"
            description = "Low diversification. Your portfolio is concentrated in few sets."

        return {'score': diversity_score, 'level': level, 'description': description}

    def calculate_volatility_rating(self) -> Dict[str, Any]:
        if self.portfolio.empty or self.price_history.empty:
            return {'volatility': 0, 'level': 'low', 'description': 'No data available.'}
        
        portfolio_cards = self.portfolio['id'].unique()
        portfolio_prices = self.price_history[self.price_history['id'].isin(portfolio_cards)]
        volatilities = []

        for card_id in portfolio_cards:
            card_prices = portfolio_prices[portfolio_prices['id'] == card_id].sort_values('date')

            if len(card_prices) >= 2:
                card_prices['returns'] = card_prices['market'].pct_change()
                vol = card_prices['returns'].std()

                if vol is not None:
                    volatilities.append(vol)

        if not volatilities:
            return {'volatility': 0, 'level': 'low', 'description': 'Insufficient data to calculate volatility.'}
        
        avg_volatility = float(np.mean(volatilities) * 100)

        if avg_volatility < 5:
            level = "low"
            description = "Stable portfolio with minimal price fluctuations."
        elif avg_volatility < 15:
            level = "medium"
            description = "Moderate price fluctuations expected based on card types."
        else:
            level = "high"
            description = "High volatility. Expect significant price swings."

        return {'volatility': avg_volatility, 'level': level, 'description': description}
    
    def calculate_market_exposure(self) -> Dict[str, Any]:
        if self.portfolio.empty:
            return {'exposure': 0, 'level': 'low', 'description': 'No data available.'}
        
        current_prices = self.get_current_prices()

        self.portfolio['card_value'] = self.portfolio.apply(lambda row: current_prices.get(row['id'], 0) * row['quantity'], axis=1)
        total_value = self.portfolio['card_value'].sum()
        
        if total_value == 0:
            return {'exposure': 0, 'level': 'low', 'description': 'No market exposure.'}
        
        max_position_pct = float((self.portfolio['card_value'].max() / total_value) * 100)
        top_3_pct = float((self.portfolio.nlargest(3, 'card_value')['card_value'].sum() / total_value) * 100)

        if max_position_pct > 30 or top_3_pct > 60:
            level = "high"
            description = "High concentration in few cards. Consider diversifying."
        elif max_position_pct > 15 or top_3_pct > 40:
            level = "medium"
            description = "Moderate concentration. Monitor top holdings."
        else:
            level = "low"
            description = "Low concentration in any single card or set."

        return {'exposure': max_position_pct, 'level': level, 'description': description}

    def get_all_risk_metrics(self) -> Dict[str, Any]:

        return {
            'diversity': self.calculate_diversity_score(),
            'volatility': self.calculate_volatility_rating(),
            'exposure': self.calculate_market_exposure()
        }

    # -------------------- AGGREGATED METRICS --------------------
    def get_all_portfolio_metrics(self) -> Dict[str, Any]:
        
        return {
            "total_value": self.calculate_total_portfolio_value(),
            "gain_loss": self.calculate_total_gain_loss(),
            "card_count": self.calculate_card_count(),
            "average_value": self.calculate_average_card_value(),
            "time_weighted_return": self.calculate_time_weighted_returns()
        }

# -------------------------------------------------------------
# Testing Zone
# -------------------------------------------------------------
if __name__ == "__main__":
    import pandas as pd

    # Load CSVs
    price_history_df: pd.DataFrame = pd.read_csv('pokemon_tcg_dashboard/data/price_history.csv', parse_dates=['date'])
    card_metadata_df: pd.DataFrame = pd.read_csv('pokemon_tcg_dashboard/data/cards_metadata_table.csv')
    portfolio_df: pd.DataFrame = pd.read_csv('pokemon_tcg_dashboard/data/portfolio_sample_id_only.csv', parse_dates=['buy_date'])

    # Initialize calculator
    calc: PortfolioCalculator = PortfolioCalculator(portfolio_df, price_history_df, card_metadata_df)

    print("\n=== CURRENT PRICES ===")
    print(calc.get_current_prices(days = None))

    print("\n=== CURRENT PRICES (100 days ago) ===")
    print(calc.get_current_prices(days = 100))

    print("\n=== TOTAL PORTFOLIO VALUE ===")
    print(calc.calculate_total_portfolio_value(days = None))

    print("\n=== TOTAL PORTFOLIO VALUE (100 days ago) ===")
    print(calc.calculate_total_portfolio_value(days = 100))

    print("\n=== CARD COUNT ===")
    print(calc.calculate_card_count(days = None))

    print("\n=== CARD COUNT (7 days ago) ===")
    print(calc.calculate_card_count(days = 7))

    print("\n=== AVERAGE CARD VALUE ===")
    print(calc.calculate_average_card_value(days = None))

    print("\n=== AVERAGE CARD VALUE (7 days ago) ===")
    print(calc.calculate_average_card_value(days = 7))

    print("\n=== TOTAL GAIN/LOSS ===")
    print(calc.calculate_total_gain_loss(days = 0))

    print("\n=== TOTAL GAIN/LOSS (30 days ago) ===")
    print(calc.calculate_total_gain_loss(days = 30))

    print("\n=== TIME-WEIGHTED RETURN (TWR) ===")
    twr = calc.calculate_time_weighted_returns()
    print(f"{twr:.2f}%" if twr is not None else "N/A")

    print("\n=== DIVERSITY SCORE ===")
    print(calc.calculate_diversity_score())

    print("\n=== VOLATILITY RATING ===")
    print(calc.calculate_volatility_rating())

    print("\n=== MARKET EXPOSURE ===")
    print(calc.calculate_market_exposure())
    
    print("\n=== GAIN OR LOSS PER CARD ===")
    per_card_gains = calc.calculate_gain_loss_per_card()
    print(per_card_gains)