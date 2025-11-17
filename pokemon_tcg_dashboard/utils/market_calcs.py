import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import lru_cache


class MarketCalculator:
    """Handles all market-level calculations"""

    def __init__(self, price_history_df, card_metadata_df):
        self.price_history = price_history_df.copy()
        self.card_metadata = card_metadata_df.copy()

        # Ensure date is clean datetime
        self.price_history['date'] = (
            pd.to_datetime(self.price_history['date'], errors='coerce')
              .dt.tz_localize(None)
        )

    # ---------------------------------------------------------
    # TOTAL MARKET VALUE
    # ---------------------------------------------------------
    @lru_cache(maxsize=32)
    def calculate_total_market_value(self):
        """Latest total market value"""
        try:
            latest_prices = self.price_history.sort_values('date').groupby('id').last()
            total_value = latest_prices['market'].sum()
        except Exception:
            total_value = 0

        # Formatting
        if total_value >= 1_000_000:
            formatted = f"${total_value / 1_000_000:.1f}M"
        elif total_value >= 1_000:
            formatted = f"${total_value / 1_000:.1f}K"
        else:
            formatted = f"${total_value:.2f}"

        return {'value': total_value, 'formatted': formatted}

    # ---------------------------------------------------------
    # N-DAY OR ALL-TIME MARKET CHANGE
    # ---------------------------------------------------------
    def calculate_change(self, days=None):
        """
        Calculate market change.
        days=None means all-time.
        """

        df = self.price_history.sort_values("date")

        try:
            # Latest price
            latest = df.groupby('id').last()['market']

            if days is None:
                # Use earliest available price
                past = df.groupby('id').first()['market']
            else:
                comparison_date = df['date'].max() - timedelta(days=days)
                past = (
                    df[df['date'] <= comparison_date]
                      .sort_values("date")
                      .groupby('id')
                      .last()['market']
                )

            # Align card IDs
            common = latest.index.intersection(past.index)

            latest_total = latest[common].sum()
            past_total = past[common].sum()

            if past_total <= 0:
                raise ValueError("Invalid past market value")

            change_value = latest_total - past_total
            change_pct = (change_value / past_total) * 100

            sign = "+" if change_value >= 0 else ""
            formatted_pct = f"{sign}{change_pct:.1f}%"

            if abs(change_value) >= 1_000_000:
                formatted_value = f"{sign}${abs(change_value)/1_000_000:.1f}M"
            elif abs(change_value) >= 1_000:
                formatted_value = f"{sign}${abs(change_value)/1_000:.1f}K"
            else:
                formatted_value = f"{sign}${abs(change_value):.2f}"

        except Exception:
            return {
                'change_pct': 0,
                'change_value': 0,
                'formatted_pct': '0.0%',
                'formatted_value': '$0'
            }

        return {
            'change_pct': change_pct,
            'change_value': change_value,
            'formatted_pct': formatted_pct,
            'formatted_value': formatted_value
        }

    # ---------------------------------------------------------
    # BEST PERFORMING SET (N-DAY OR ALL-TIME)
    # ---------------------------------------------------------
    def calculate_best_performing_set(self, days=None):
        """
        Best performing set over N days or all-time.
        days=None means all-time.
        """

        df = self.price_history.sort_values("date")

        try:
            if days is None:
                recent = df
            else:
                cutoff = df['date'].max() - timedelta(days=days)
                recent = df[df['date'] >= cutoff]

            prices_with_sets = recent.merge(
                self.card_metadata[['id', 'setName']],
                on='id',
                how='left'
            )

            prices_with_sets.dropna(subset=['setName'], inplace=True)

            performances = []

            for set_name in prices_with_sets['setName'].unique():
                set_data = prices_with_sets[prices_with_sets['setName'] == set_name]

                earliest = set_data.groupby('id').first()['market']
                latest = set_data.groupby('id').last()['market']

                if len(earliest) == 0 or earliest.sum() <= 0:
                    continue

                change = ((latest.sum() - earliest.sum()) / earliest.sum()) * 100
                performances.append({'set': set_name, 'change_pct': change})

            if not performances:
                return {'set_name': 'N/A', 'change_pct': 0, 'formatted': 'N/A'}

            best = max(performances, key=lambda x: x['change_pct'])

            return {
                'set_name': best['set'],
                'change_pct': best['change_pct'],
                'formatted': f"{best['set']} (+{best['change_pct']:.1f}%)"
            }

        except Exception:
            return {'set_name': 'N/A', 'change_pct': 0, 'formatted': 'N/A'}

    # ---------------------------------------------------------
    # ACTIVE LISTINGS (N-DAY OR ALL-TIME)
    # ---------------------------------------------------------
    def count_active_listings(self, days=None):
        """
        Count active listings.
        days=None means all-time.
        """

        try:
            if days is None:
                active = self.price_history
            else:
                cutoff = self.price_history['date'].max() - timedelta(days=days)
                active = self.price_history[self.price_history['date'] >= cutoff]

            if active.empty:
                return {'count': 0, 'formatted': '0'}

            latest = (
                active.sort_values('date')
                      .groupby('id')
                      .last()
            )

            count = latest['volume'].sum()

        except Exception:
            count = 0

        return {'count': count, 'formatted': f"{count:,}"}

    # ---------------------------------------------------------
    # TOP MOVERS (N-DAY OR ALL-TIME)
    # ---------------------------------------------------------
    def calculate_top_movers(self, period='1d', n=20, min_volume=None):
        """
        period supports: '1d', '7d', '15d', '30d', 'all'
        """

        # Convert period → days / None
        if period == 'all':
            days = None
        else:
            days = int(period.replace("d", ""))

        if self.price_history.empty:
            return {'gainers': [], 'losers': []}

        df = self.price_history.sort_values('date')

        # Filter for period
        if days is None:
            period_data = df.copy()
        else:
            cutoff = df['date'].max() - timedelta(days=days)
            period_data = df[df['date'] >= cutoff]

        if period_data.empty:
            return {'gainers': [], 'losers': []}

        changes = []

        for card_id in period_data['id'].unique():
            card_data = period_data[period_data['id'] == card_id].sort_values('date')

            if len(card_data) < 2:
                continue

            start_price = card_data.iloc[0]['market']
            end_price = card_data.iloc[-1]['market']

            if start_price <= 0:
                continue

            if min_volume is not None and 'volume' in card_data.columns:
                if card_data['volume'].sum() < min_volume:
                    continue

            change_pct = ((end_price - start_price) / start_price) * 100
            change_value = end_price - start_price

            meta = self.card_metadata[self.card_metadata['id'] == card_id]
            if not meta.empty:
                name = meta.iloc[0]['name']
                set_name = meta.iloc[0]['setName']
            else:
                name = str(card_id)
                set_name = "Unknown"

            changes.append({
                'card_id': card_id,
                'name': name,
                'set': set_name,
                'current_price': end_price,
                'change_pct': change_pct,
                'change_value': change_value,
                'change_pct_formatted': f"{'+' if change_pct >= 0 else ''}{change_pct:.1f}%",
                'change_value_formatted': f"{'+' if change_value >= 0 else ''}${change_value:.2f}"
            })

        if not changes:
            return {'gainers': [], 'losers': []}

        df_changes = pd.DataFrame(changes)

        # Handle ties cleanly
        cutoff_gain = df_changes['change_pct'].nlargest(n).min()
        cutoff_loss = df_changes['change_pct'].nsmallest(n).max()

        gainers = df_changes[df_changes['change_pct'] >= cutoff_gain].sort_values('change_pct', ascending=False).to_dict('records')
        losers  = df_changes[df_changes['change_pct'] <= cutoff_loss].sort_values('change_pct', ascending=True).to_dict('records')

        return {'gainers': gainers, 'losers': losers}

    def get_all_market_metrics(self):
        """Return all major market metrics across all time windows."""

        return {
            'total_market_value': self.calculate_total_market_value(),

            # Market Change
            'market_change': {
                '1d':  self.calculate_change(days=1),
                '7d':  self.calculate_change(days=7),
                '15d': self.calculate_change(days=15),
                '30d': self.calculate_change(days=30),
                'all': self.calculate_change(days=None),
            },

            # Best Performing Sets
            'best_performing_set': {
                '1d':  self.calculate_best_performing_set(days=1),
                '7d':  self.calculate_best_performing_set(days=7),
                '15d': self.calculate_best_performing_set(days=15),
                '30d': self.calculate_best_performing_set(days=30),
                'all': self.calculate_best_performing_set(days=None),
            },

            # Active Listings
            'active_listings': {
                '1d':  self.count_active_listings(days=1),
                '7d':  self.count_active_listings(days=7),
                '15d': self.count_active_listings(days=15),
                '30d': self.count_active_listings(days=30),
                'all': self.count_active_listings(days=None),
            }
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
    market_change = market_calc.calculate_change(days = 1)

    #Test best performing set
    best_perf_set = market_calc.calculate_best_performing_set(days=30)
    
    #Test active listings
    active_listings = market_calc.count_active_listings(days = 7)

    #Test all
    all_func = market_calc.get_all_market_metrics()

    #Test top movers
    top_movers = market_calc.calculate_top_movers(period='7d', n=10)

    print(tot_market_val)
    print(market_change)
    print(best_perf_set)
    print(active_listings)

    print(all_func)
    print(top_movers)