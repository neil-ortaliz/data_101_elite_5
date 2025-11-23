import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
from utils import load_data

import logging
logger = logging.getLogger(__name__)

class PortfolioCalculator:
    """Handles all portfolio-level calculations for card portfolios."""

    def __init__(self, 
                 portfolio_df: pd.DataFrame, 
                 price_history_df: pd.DataFrame=None, 
                 card_metadata_df: pd.DataFrame=None) -> None:
        """
        Initialize the calculator.

        Args:
            portfolio_df (pd.DataFrame): Current portfolio with columns ['id'].
            price_history_df (pd.DataFrame): Price history with columns ['id', 'date', 'market'].
            card_metadata_df (pd.DataFrame): Metadata with ['id', 'set', 'rarity'].
        """
        if portfolio_df is None:
            self.portfolio = pd.DataFrame(columns=['id'])
        else:    
            self.portfolio = portfolio_df.copy()
        

        if price_history_df is None:
            price_history_df = load_data("price_history.csv")
        if card_metadata_df is None:
            card_metadata_df = load_data("cards_metadata_table.csv")

        self.price_history = price_history_df.copy()   
        self.card_metadata = card_metadata_df.copy()

        self.price_history = self.price_history.merge(
            self.card_metadata[['id', 'tcgPlayerId']],
            on='id',
            how='left'
        )

        logger.debug(self.price_history.head())
        # Ensure date is clean datetime
        self.price_history['date'] = (
            pd.to_datetime(self.price_history['date'], errors='coerce')
              .dt.tz_localize(None)
        )

        logger.debug(f"self.portfolio \n {self.portfolio}")

    # -------------------------------------------------------------
    # PRICE LOOKUPS
    # -------------------------------------------------------------
    def get_current_prices(self) -> Dict[Any, float]:
        """Return the most recent market price for each card in the portfolio."""
        latest_prices = (
            self.price_history
            .sort_values("date")
            .groupby("tcgPlayerId", as_index=False)
            .last()
        )
        current_prices = latest_prices.set_index("tcgPlayerId")["market"].to_dict()
        return current_prices

    # -------------------------------------------------------------
    # PORTFOLIO VALUE METRICS
    # -------------------------------------------------------------
    def calculate_total_portfolio_value(self) -> Dict[str, Union[float, str]]:
        """Calculate total current value of portfolio (1 unit per card)."""
        current_prices = self.get_current_prices()
        #logger.debug(f"===========current_prices=========== \n {current_prices.keys()}")
        total_value = sum(
            current_prices.get(row["id"], 0)
            for _, row in self.portfolio.iterrows()
        )
        logger.debug(f"total_value {total_value}")
        return {"value": total_value, "formatted": f"${total_value:,.2f}"}

    def calculate_card_count(self) -> Dict[str, Union[int, str]]:
        """Calculate total card count and unique card count."""
        total_quantity = len(self.portfolio)
        unique_cards = self.portfolio['id'].nunique()
        return {"count": int(total_quantity), "unique_cards": unique_cards, "formatted": f"{int(total_quantity):,} cards"}

    def calculate_average_card_value(self) -> Dict[str, Union[float, str]]:
        """Average market value per card."""
        total_value = self.calculate_total_portfolio_value()["value"]
        count = self.calculate_card_count()["count"]
        avg_value = total_value / count if count > 0 else 0
        return {"value": avg_value, "formatted": f"${avg_value:.2f}"}

    def get_all_portfolio_metrics(self) -> Dict[str, Any]:
        """Return all portfolio metrics at once."""
        return {
            "total_value": self.calculate_total_portfolio_value(),
            "gain_loss": self.calculate_total_gain_loss(baseline_date="2025-01-01"),
            "card_count": self.calculate_card_count(),
            "average_value": self.calculate_average_card_value()
        }

    def calculate_total_gain_loss(self, baseline_date: Union[str, pd.Timestamp]) -> Dict[str, Union[float, str]]:
        """Calculate gain/loss between baseline_date and the most recent date."""
        baseline_prices = (
            self.price_history[self.price_history["date"] == baseline_date]
            .set_index("id")["market"]
            .to_dict()
        )
        current_prices = self.get_current_prices()
        baseline_value = sum(baseline_prices.get(cid, 0) for cid in self.portfolio["id"])
        current_value = sum(current_prices.get(cid, 0) for cid in self.portfolio["id"])
        gain_loss = current_value - baseline_value
        pct = (gain_loss / baseline_value * 100) if baseline_value > 0 else 0
        return {
            "baseline_value": baseline_value,
            "current_value": current_value,
            "gain_loss": gain_loss,
            "gain_loss_pct": pct,
            "formatted": f"{'+' if gain_loss >= 0 else '-'}${abs(gain_loss):,.2f}"
        }

    def compare_to_benchmark(self, benchmark_return_pct: float, baseline_date: Union[str, pd.Timestamp]) -> Dict[str, float]:
        """Compare portfolio gain/loss to an external benchmark."""
        portfolio_gain = self.calculate_total_gain_loss(baseline_date)['gain_loss_pct']
        difference = portfolio_gain - benchmark_return_pct
        return {
            'portfolio_return_pct': portfolio_gain,
            'benchmark_return_pct': benchmark_return_pct,
            'difference_pct': difference
        }

    # -------------------------------------------------------------
    # RISK METRICS
    # -------------------------------------------------------------
    def calculate_diversity_score(self) -> Dict[str, Any]:
        """Portfolio diversity based on set and rarity."""
        if self.card_metadata.empty or self.portfolio.empty:
            return {'score': 0, 'level': 'low', 'description': 'No data to calculate diversity.'}

        portfolio_with_meta = self.portfolio.merge(
            self.card_metadata[['id', 'setId', 'rarity']],
            on='id',
            how='left'
        )
        total_cards = len(portfolio_with_meta)
        if total_cards == 0:
            return {'score': 0, 'level': 'low', 'description': 'No cards in portfolio.'}

        unique_sets = portfolio_with_meta['setId'].nunique()
        unique_rarities = portfolio_with_meta['rarity'].nunique()

        set_shares = portfolio_with_meta.groupby('setId')['id'].count() / total_cards
        herfindahl = (set_shares ** 2).sum()

        diversity_score = (1 - herfindahl) * 100
        diversity_score *= (1 + (unique_sets / 10)) * (1 + (unique_rarities / 5))
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
        """Portfolio volatility based on price returns."""
        if self.portfolio.empty:
            return {'volatility': 0, 'level': 'low', 'description': 'No portfolio to calculate volatility.'}

        portfolio_cards = self.portfolio['id'].unique()
        portfolio_prices = self.price_history[self.price_history['id'].isin(portfolio_cards)]
        volatilities = []

        for card_id in portfolio_cards:
            card_prices = portfolio_prices[portfolio_prices['id'] == card_id].sort_values('date')
            if len(card_prices) >= 2:
                card_prices = card_prices.copy()
                card_prices['returns'] = card_prices['market'].pct_change()
                std_dev = card_prices['returns'].std()
                if not np.isnan(std_dev):
                    volatilities.append(std_dev)

        if not volatilities:
            return {'volatility': 0, 'level': 'low', 'description': 'Insufficient data to calculate volatility.'}

        avg_volatility = np.mean(volatilities) * 100

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
        """Concentration risk based on largest positions (1 card = 1 unit)."""
        if self.portfolio.empty:
            return {'exposure': 0, 'level': 'low', 'description': 'No market exposure.'}

        current_prices = self.get_current_prices()
        df = self.portfolio.copy()
        df['card_value'] = df['id'].apply(lambda cid: current_prices.get(cid, 0))
        total_value = df['card_value'].sum()

        if total_value == 0:
            return {'exposure': 0, 'level': 'low', 'description': 'No market exposure.'}

        max_position_pct = (df['card_value'].max() / total_value) * 100
        top_3_pct = (df.nlargest(3, 'card_value')['card_value'].sum() / total_value) * 100

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
        """Return all risk metrics for the portfolio."""
        return {
            'diversity': self.calculate_diversity_score(),
            'volatility': self.calculate_volatility_rating(),
            'exposure': self.calculate_market_exposure()
        }


# -------------------------------------------------------------
# Testing Zone
# -------------------------------------------------------------
if __name__ == "__main__":
    price_history_df: pd.DataFrame = pd.read_csv('pokemon_tcg_dashboard/data/price_history.csv', parse_dates=['date'])
    card_metadata_df: pd.DataFrame = pd.read_csv('pokemon_tcg_dashboard/data/cards_metadata_table.csv')
    portfolio_df: pd.DataFrame = pd.read_csv('pokemon_tcg_dashboard/data/portfolio_sample_id_only.csv')

    calc: PortfolioCalculator = PortfolioCalculator(portfolio_df, price_history_df, card_metadata_df)

    print("Current Prices:", calc.get_current_prices())
    print("Total Portfolio Value:", calc.calculate_total_portfolio_value())
    print("Card Count:", calc.calculate_card_count())
    print("Average Card Value:", calc.calculate_average_card_value())
    print("Gain/Loss since 2025-10-02:", calc.calculate_total_gain_loss(baseline_date='2025-10-02'))
    print("Diversity Score:", calc.calculate_diversity_score())
    print("Volatility Rating:", calc.calculate_volatility_rating())
    print("Market Exposure:", calc.calculate_market_exposure())
    print("All Risk Metrics:", calc.get_all_risk_metrics())

    benchmark_result: Dict[str, float] = calc.compare_to_benchmark(benchmark_return_pct=10, baseline_date='2025-10-02')
    print("Compare to Benchmark:", benchmark_result)
