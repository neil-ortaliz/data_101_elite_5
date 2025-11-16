import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import lru_cache


class MarketCalculator:
    """Handles all market-level calculations"""

    def __init__(self, price_history_df, card_metadata_df):
        """
        Initialize calculator with data
        Args:
            price_history_df: DataFrame with columns [card_id, date, price, source]
            card_metadata_df: DataFrame with columns [card_id, name, set, rarity]
        """
        self.price_history = price_history_df
        self.card_metadata = card_metadata_df

        # Ensure date column is datetime
        self.price_history['date'] = pd.to_datetime(self.price_history['date'], errors='coerce').dt.tz_localize(None)

        # Drop rows with missing essential data
        self.price_history.dropna(subset=['id', 'market', 'date', 'volume'], inplace=True)
        self.card_metadata.dropna(subset=['id', 'setName'], inplace=True)

    @lru_cache(maxsize=32)
    def calculate_total_market_value(self):
        """Calculate total market value of all tracked cards"""
        try:
            latest_prices = self.price_history.sort_values('date').groupby('id').last()
            total_value = latest_prices['market'].sum()
        except Exception:
            total_value = 0

        # Format nicely
        if total_value >= 1_000_000:
            formatted = f"${total_value / 1_000_000:.1f}M"
        elif total_value >= 1_000:
            formatted = f"${total_value / 1_000:.1f}K"
        else:
            formatted = f"${total_value:.2f}"

        return {'value': total_value, 'formatted': formatted}

    def calculate_24h_change(self):
        """Calculate 24-hour market change"""
        try:
            today = datetime.now()
            yesterday = today - timedelta(days=1)

            today_prices = self.price_history[self.price_history['date'].dt.date == today.date()] \
                .groupby('id')['market'].mean()
            yesterday_prices = self.price_history[self.price_history['date'].dt.date == yesterday.date()] \
                .groupby('id')['market'].mean()

            if yesterday_prices.empty:
                raise ValueError("No data for yesterday")

            # Align card IDs
            common_cards = today_prices.index.intersection(yesterday_prices.index)
            today_total = today_prices[common_cards].sum()
            yesterday_total = yesterday_prices[common_cards].sum()

            change_value = today_total - yesterday_total
            change_pct = (change_value / yesterday_total) * 100 if yesterday_total > 0 else 0

            sign = "+" if change_value >= 0 else ""
            formatted_pct = f"{sign}{change_pct:.1f}%"

            if abs(change_value) >= 1_000_000:
                formatted_value = f"{sign}${abs(change_value)/1_000_000:.1f}M"
            elif abs(change_value) >= 1_000:
                formatted_value = f"{sign}${abs(change_value)/1_000:.1f}K"
            else:
                formatted_value = f"{sign}${abs(change_value):.2f}"

        except Exception:
            return {'change_pct': 0, 'change_value': 0, 'formatted_pct': '0.0%', 'formatted_value': '$0'}

        return {
            'change_pct': change_pct,
            'change_value': change_value,
            'formatted_pct': formatted_pct,
            'formatted_value': formatted_value
        }

    def calculate_best_performing_set(self, days=7):
        """Identify best performing set over a specified time period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_prices = self.price_history[self.price_history['date'] >= cutoff_date]

            # Merge with card metadata to get set info
            prices_with_sets = recent_prices.merge(self.card_metadata[['id', 'setName']], on='id', how='left')
            prices_with_sets.dropna(subset=['setName'], inplace=True)

            set_performance = []

            for set_name in prices_with_sets['setName'].unique():
                set_data = prices_with_sets[prices_with_sets['setName'] == set_name]

                earliest = set_data.sort_values('date').groupby('id').first()['market']
                latest = set_data.sort_values('date').groupby('id').last()['market']

                if len(earliest) > 0 and earliest.sum() > 0:
                    change = ((latest.sum() - earliest.sum()) / earliest.sum()) * 100
                    set_performance.append({'set': set_name, 'change_pct': change})

            if not set_performance:
                return {'set_name': 'N/A', 'change_pct': 0, 'formatted': 'N/A'}

            best = max(set_performance, key=lambda x: x['change_pct'])
            return {'set_name': best['set'], 'change_pct': best['change_pct'],
                    'formatted': f"{best['set']} (+{best['change_pct']:.1f}%)"}

        except Exception:
            return {'set_name': 'N/A', 'change_pct': 0, 'formatted': 'N/A'}

    def count_active_listings(self):
        """Count total active listings across all sources (last 7 days)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            active = self.price_history[self.price_history['date'] >= cutoff_date]
            count = len(active.drop_duplicates(['id', 'volume']))
        except Exception:
            count = 0

        return {'count': count, 'formatted': f"{count:,}"}

    def get_all_market_metrics(self):
        """Return all market metrics at once"""
        return {
            'total_market_value': self.calculate_total_market_value(),
            'change_24h': self.calculate_24h_change(),
            'best_performing_set': self.calculate_best_performing_set(),
            'active_listings': self.count_active_listings()
        }
    
#Testing Zone
if __name__ == "__main__":
    #Get all CSV files (I added the flattened CSV files)
    price_history_df = pd.read_csv('pokemon_tcg_dashboard/data/price_history.csv', parse_dates=['date'])
    card_metadata_df = pd.read_csv('pokemon_tcg_dashboard/data/cards_metadata_table.csv')

    #Call class function
    market_calc = MarketCalculator(price_history_df, card_metadata_df)

    #Test Total Market Value 
    tot_market_val = market_calc.calculate_total_market_value()

    #Test 24h change
    market_change = market_calc.calculate_24h_change()

    #Test best performing set
    best_perf_set = market_calc.calculate_best_performing_set(days=30)
    
    #Test active listings
    active_listings = market_calc.count_active_listings()

    #Test all
    all_func = market_calc.get_all_market_metrics()

    print(tot_market_val)
    print(market_change)
    print(best_perf_set)
    print(active_listings)

    print(all_func)