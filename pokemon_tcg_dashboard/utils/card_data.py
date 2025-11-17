import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CardDataFetcher:
    """Handles fetching and structuring individual card data"""

    def __init__(self, card_metadata_df, price_history_df, ebay_prices_df):
        """
        Initialize fetcher

        Args:
            card_metadata_df: DataFrame with card details
            price_history_df: DataFrame with price history (must include 'id', 'date', 'market', 'condition')
            ebay_prices_df: DataFrame with PSA graded prices (must include 'id', 'date', 'grade', 'average')
        """
        required_meta_cols = {'id', 'name', 'setName', 'rarity'}
        required_price_cols = {'id', 'date', 'market', 'condition'}
        required_ebay_cols = {'id', 'date', 'grade', 'average'}

        if not required_meta_cols.issubset(card_metadata_df.columns):
            raise ValueError(f"card_metadata_df missing required columns: {required_meta_cols}")
        if not required_price_cols.issubset(price_history_df.columns):
            raise ValueError(f"price_history_df missing required columns: {required_price_cols}")
        if not required_ebay_cols.issubset(ebay_prices_df.columns):
            raise ValueError(f"ebay_prices_df missing required columns: {required_ebay_cols}")

        self.card_metadata = card_metadata_df.copy()
        self.price_history = price_history_df.copy()
        self.ebay_prices = ebay_prices_df.copy()

        # Ensure date is clean datetime
        self.price_history['date'] = (
            pd.to_datetime(self.price_history['date'], errors='coerce')
              .dt.tz_localize(None)
        )

        self.ebay_prices['date'] = (
            pd.to_datetime(self.price_history['date'], errors='coerce')
              .dt.tz_localize(None)
        )

        # Cache dictionary
        self._cache = {}

    def get_card_by_id(self, card_id, use_cache=True, days=None, psa='psa9'):
        """Get all data for a specific card

        Args:
            card_id: Card identifier
            use_cache: Whether to return cached data if available
            days: Number of days of price history to retrieve (None = all-time)
            psa: PSA grade to use for pricing (e.g., 'psa9', 'psa10')

        Returns:
            dict with card data
        """

        cache_key = (card_id, days, psa)  # Include `psa` in cache key
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Get card metadata
        card_info = self.card_metadata[self.card_metadata['id'] == card_id]
        if len(card_info) == 0:
            return None
        card_info = card_info.iloc[0]

        # Get prices
        current_price = self.get_current_market_price(card_id, days=days)
        psa_price = self.get_psa_price(card_id, psa)
        ungraded_price = self.get_ungraded_price(card_id, days=days)

        # Get listings count
        total_listings = self.count_active_listings(card_id, days=days)

        # Get price history
        price_history = self.get_price_history(card_id, days=days)

        card_data = {
            'card_id': card_id,
            'name': card_info['name'],
            'set': card_info.get('setName', card_info.get('set', 'N/A')),
            'rarity': card_info['rarity'],
            'card_number': card_info.get('cardNumber', 'N/A'),
            'image_url': card_info.get('imageUrl', ''),
            'current_price': current_price,
            'psa_grade': psa,          # Show which PSA grade was used
            'psa_price': psa_price,
            'ungraded_price': ungraded_price,
            'total_listings': total_listings,
            'price_history': price_history
        }

        # Cache the result
        self._cache[cache_key] = card_data
        return card_data

    def get_current_market_price(self, card_id, days=7):
        """Get current market price (average of recent listings)"""

        cutoff_date = None if days is None else datetime.now() - timedelta(days=days)
        recent_prices = self.price_history[self.price_history['id'] == card_id]
        if cutoff_date:
            recent_prices = recent_prices[recent_prices['date'] >= cutoff_date]

        if len(recent_prices) == 0:
            return "$0.00"

        avg_price = recent_prices['market'].mean()
        return f"${avg_price:.2f}"

    def get_psa_price(self, card_id, grade):
        """
        Get the price for a specific PSA grade.

        Args:
            card_id: Card identifier
            grade: PSA grade as string, e.g., 'psa8', 'psa9', 'psa 10'

        Returns:
            str: Price formatted as '$XX.XX', or 'N/A' if no data
        """
        # Normalize grade string
        grade_norm = grade.lower().replace(" ", "")
        psa_data = self.ebay_prices[self.ebay_prices['id'] == card_id]
        psa_data = psa_data[psa_data['grade'].str.lower().str.replace(" ", "") == grade_norm]

        if len(psa_data) == 0:
            return "N/A"

        # Take the latest price by date
        latest_price = psa_data.sort_values('date').iloc[-1]['average']
        return f"${latest_price:.2f}"

    def get_ungraded_price(self, card_id, days=30):
        """Get ungraded (Near Mint) price"""

        ungraded_data = self.price_history[(self.price_history['id'] == card_id) & (self.price_history['condition'] == 'Near Mint')]
        if len(ungraded_data) == 0:
            return "$0.00"

        cutoff_date = None if days is None else datetime.now() - timedelta(days=days)
        recent = ungraded_data if cutoff_date is None else ungraded_data[ungraded_data['date'] >= cutoff_date]
        avg_price = recent['market'].mean() if len(recent) > 0 else ungraded_data['market'].mean()
        return f"${avg_price:.2f}"

    def count_active_listings(self, card_id, days=7):
        """Count active listings for card (based on unique dates in price history)"""

        cutoff_date = None if days is None else datetime.now() - timedelta(days=days)
        listings = self.price_history[self.price_history['id'] == card_id]
        if cutoff_date:
            listings = listings[listings['date'] >= cutoff_date]
        # Use number of unique dates as a proxy for listings
        return listings['date'].nunique()

    def get_price_history(self, card_id, days=None):
        """Get price history for charting"""

        cutoff_date = None if days is None else datetime.now() - timedelta(days=days)
        history = self.price_history[self.price_history['id'] == card_id]
        if cutoff_date:
            history = history[history['date'] >= cutoff_date]
        history = history.sort_values('date')

        if len(history) == 0:
            return []

        daily_avg = history.groupby('date')['market'].mean().reset_index()
        return [
            {'date': row['date'].strftime('%Y-%m-%d'), 'price': float(row['market'])}
            for _, row in daily_avg.iterrows()
        ]
    
    def aggregate_prices(self, card_id, condition='any', grade=None, days=None):
        """Aggregate prices from multiple sources with weighting"""

        # Select dataset
        if grade:
            # eBay PSA grades
            grade_norm = grade.lower().replace(" ", "")
            data = self.ebay_prices[self.ebay_prices['id'] == card_id]
            data = data[data['grade'].str.lower().str.replace(" ", "") == grade_norm]
            price_col = 'average'
        else:
            # Ungraded price history
            data = self.price_history[self.price_history['id'] == card_id]
            if condition != 'any':
                data = data[data['condition'] == condition]
            price_col = 'market'

        if len(data) == 0:
            return {
                'average_price': 0,
                'median_price': 0,
                'min_price': 0,
                'max_price': 0,
                'confidence': 'none',
                'sample_size': 0
            }

        # Filter by days
        if days is not None:
            cutoff = datetime.now() - timedelta(days=days)
            recent_data = data[data['date'] >= cutoff]
            if len(recent_data) == 0:
                recent_data = data
        else:
            recent_data = data

        prices = recent_data[price_col]

        # Remove outliers using IQR
        Q1 = prices.quantile(0.25)
        Q3 = prices.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        filtered_prices = prices[(prices >= lower) & (prices <= upper)]
        if len(filtered_prices) == 0:
            filtered_prices = prices

        # Statistics
        avg_price = filtered_prices.mean()
        median_price = filtered_prices.median()
        min_price = filtered_prices.min()
        max_price = filtered_prices.max()
        sample_size = len(filtered_prices)

        # Confidence
        spread = max_price - min_price
        rel_spread = (spread / avg_price) * 100 if avg_price > 0 else 100
        if sample_size >= 20 and rel_spread < 20:
            confidence = 'high'
        elif sample_size >= 10 and rel_spread < 40:
            confidence = 'medium'
        else:
            confidence = 'low'

        return {
            'average_price': float(avg_price),
            'median_price': float(median_price),
            'min_price': float(min_price),
            'max_price': float(max_price),
            'confidence': confidence,
            'sample_size': sample_size
        }

    def get_price_comparison(self, card_id, days=None):
        """Compare prices across grades and conditions"""

        return {
            'ungraded_nm': self.aggregate_prices(card_id, condition='Near Mint', days=days),
            'psa_8': self.aggregate_prices(card_id, grade='psa8', days=days),
            'psa_9': self.aggregate_prices(card_id, grade='psa9', days=days),
            'psa_10': self.aggregate_prices(card_id, grade='psa 10', days=days)
        }

#Testing Zone
if __name__ == "__main__":
    #Get all CSV files (I added the flattened CSV files)
    price_history_df = pd.read_csv('pokemon_tcg_dashboard/data/price_history.csv', parse_dates=['date'])
    card_metadata_df = pd.read_csv('pokemon_tcg_dashboard/data/cards_metadata_table.csv')
    ebay_price_history_df = pd.read_csv('pokemon_tcg_dashboard/data/ebay_price_history.csv', parse_dates=['date'])

    fetcher = CardDataFetcher(card_metadata_df, price_history_df, ebay_price_history_df)

    card_data = fetcher.get_card_by_id(card_id = '68af6bbbd14a00763202573c', days = 7, psa = 'psa10')

    price_comparison = fetcher.get_price_comparison(card_id = '68af6bbbd14a00763202573c', days = 7)
    
    print(card_data)

    print('\n')

    print(price_comparison)