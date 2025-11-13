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
        self.price_history['date'] = pd.to_datetime(self.price_history['date'])

    @lru_cache(maxsize=32)
    def calculate_total_market_value(self):
        """
        Calculate total market value of all tracked cards
        Returns:
            dict: {
                'value': float,
                'formatted': str (e.g., "$45.2M")
            }
        """
        # Get most recent price for each card
        latest_prices = self.price_history.sort_values('date').groupby('id').last()

        # Sum all prices
        total_value = latest_prices['market'].sum()

        # Format for display
        if total_value >= 1_000_000:
            formatted = f"${total_value / 1_000_000:.1f}M"
        elif total_value >= 1_000:
            formatted = f"${total_value / 1_000:.1f}K"
        else:
            formatted = f"${total_value:.2f}"

        return {
            'value': total_value,
            'formatted': formatted
        }
    
    def calculate_24h_change(self):
        """
        Calculate 24-hour market change
        Returns:
        dict: {
        'change_pct': float,
        'change_value': float,
        'formatted_pct': str (e.g., "+1.8%"),
        'formatted_value': str (e.g., "+$812K")
        }
        """
        #today = datetime(2025, 10, 1) -- test data
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # Get prices from today and yesterday
        today_prices = self.price_history[self.price_history['date'].dt.date == today.date()].groupby('id')['market'].mean()
        yesterday_prices = self.price_history[self.price_history['date'].dt.date == yesterday.date()].groupby('id')['market'].mean()
        
        # Calculate change
        if len(yesterday_prices) == 0:
            return {'change_pct': 0, 'change_value': 0,
                    'formatted_pct': '0.0%', 'formatted_value': '$0'}
        
        # Align card IDs
        common_cards = today_prices.index.intersection(yesterday_prices.index)
        today_total = today_prices[common_cards].sum()
        yesterday_total = yesterday_prices[common_cards].sum()

        change_value = today_total - yesterday_total
        change_pct = (change_value / yesterday_total) * 100 if yesterday_total > 0 else 0
        
        # Format
        sign = "+" if change_value >= 0 else ""
        formatted_pct = f"{sign}{change_pct:.1f}%"
        
        if abs(change_value) >= 1_000_000:
            formatted_value = f"{sign}${abs(change_value)/1_000_000:.1f}M"
        elif abs(change_value) >= 1_000:
            formatted_value = f"{sign}${abs(change_value)/1_000:.1f}K"
        else:
            formatted_value = f"{sign}${abs(change_value):.2f}"
        return {
            'change_pct': change_pct,
            'change_value': change_value,
            'formatted_pct': formatted_pct,
            'formatted_value': formatted_value
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

    print(tot_market_val)
    print(market_change)