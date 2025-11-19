# Task 1 - Set-level Data Aggregation

import pandas as pd
import numpy as np
from typing import Optional

def aggregate_set_data(
    card_data: pd.DataFrame,
    price_history: pd.DataFrame,
    *,
    card_id_col: str = "card_id",
    price_col: str = "price",
    date_col: str = "date",
    set_col: str = "set_name",
    treat_missing_as_zero: bool = False,
    include_priced_counts: bool = False
) -> pd.DataFrame:
    """
    Aggregate card-level data to set-level statistics.

    Parameters
    ----------
    card_data : pd.DataFrame
        Expected to contain card identifier and set name (columns names flexible).
    price_history : pd.DataFrame
        Expected to contain card identifier, date, and a numeric price column.
    card_id_col : str, optional
        Column name for card id in both tables (default 'card_id').
    price_col : str, optional
        Column name in price_history that contains the numeric price (default 'price').
    date_col : str, optional
        Column name in price_history that contains timestamp (default 'date').
    set_col : str, optional
        Column name in card_data for set name (default 'set_name').
    treat_missing_as_zero : bool, optional
        If True: missing latest prices are treated as 0 when computing total_value.
        If False (default): missing latest prices are excluded from total_value.
    include_priced_counts : bool, optional
        If True, the returned DataFrame will include 'priced_count' and 'unpriced_count'.

    Returns
    -------
    pd.DataFrame
        Columns (always present): ['set_name', 'total_value', 'avg_price', 'card_count', 'last_updated']
        Optionally includes 'priced_count' and 'unpriced_count' when include_priced_counts=True.

    Behavior notes
    --------------
    - Latest price per card is chosen by the maximum `date_col` value.
    - avg_price is computed over available (non-null) latest prices.
    - card_count counts unique card ids per set (cards with no price still count).
    - Handles missing prices gracefully (see treat_missing_as_zero).
    """
  
    cards = card_data.copy()
    ph = price_history.copy()

    # card id column:
    if card_id_col not in cards.columns:
        # try common alternatives
        for alt in ["id", "cardId", "card_id"]:
            if alt in cards.columns:
                card_id_col = alt
                break
    if card_id_col not in ph.columns:
        for alt in ["id", "cardId", "card_id"]:
            if alt in ph.columns:
                card_id_col = alt
                break

    # set column:
    if set_col not in cards.columns:
        for alt in ["setName", "set_name", "setId", "set"]:
            if alt in cards.columns:
                set_col = alt
                break
    if set_col not in cards.columns:
        raise KeyError(
            f"Could not find a set column in card_data. Tried defaults and alternatives; last tried '{set_col}'."
        )

    # date col:
    if date_col not in ph.columns:
        for alt in ["date", "created_at", "timestamp"]:
            if alt in ph.columns:
                date_col = alt
                break
    if date_col not in ph.columns:
        raise KeyError(f"price_history must contain a date column; tried '{date_col}' and common alternatives.")

    # price col:
    if price_col not in ph.columns:
        # try a few common names
        for alt in ["market", "avgPrice", "avg_price", "lastPrice", "trendPrice"]:
            if alt in ph.columns:
                price_col = alt
                break
    if price_col not in ph.columns:
        raise KeyError(f"price_history must contain a numeric price column; tried '{price_col}' and alternatives.")

    # Parse dates into datetime (coerce invalid -> NaT)
    ph[date_col] = pd.to_datetime(ph[date_col], errors="coerce")

    # Drop rows with missing card id in price history
    ph = ph[ph[card_id_col].notna()].copy()

    # For each card_id, pick the index of the row with latest date
    ph_with_dates = ph.dropna(subset=[date_col])
    if not ph_with_dates.empty:
        idx = ph_with_dates.groupby(card_id_col)[date_col].idxmax()
        latest = ph.loc[idx].set_index(card_id_col)
    else:
        # No valid dated price rows; create empty dataframe with card_id index
        latest = pd.DataFrame(columns=ph.columns).set_index(card_id_col)

    # Ensure price column is numeric
    latest[price_col] = pd.to_numeric(latest[price_col], errors="coerce")

    # Merge latest price onto cards (left join so every card counts)
    merged = cards.merge(
        latest[[price_col]] if price_col in latest.columns else latest,
        how="left",
        left_on=card_id_col,
        right_index=True
    )

    # unify column name for downstream operations
    merged = merged.rename(columns={price_col: "latest_price", set_col: "set_name"})

    # Aggregations
    def total_agg(series: pd.Series) -> float:
        if treat_missing_as_zero:
            return float(series.fillna(0).sum())
        else:
            return float(series.dropna().sum())

    grouped = merged.groupby("set_name")

    agg = grouped.agg(
        total_value = ("latest_price", total_agg),
        avg_price   = ("latest_price", "mean"),      # pandas mean ignores NaN
        card_count  = (card_id_col, "nunique")
    ).reset_index()

    # avg_price on groups with no priced cards will be NaN; that's expected and correct.
    agg['last_updated'] = pd.Timestamp.now()

    # Optionally include counts of priced/unpriced cards
    if include_priced_counts:
        counts = grouped["latest_price"].apply(lambda s: s.notna().sum()).rename("priced_count")
        agg = agg.merge(counts.reset_index(), on="set_name", how="left")
        agg["unpriced_count"] = agg["card_count"] - agg["priced_count"]
        # Reorder to keep structure clear
        agg = agg[[
            "set_name", "total_value", "avg_price", "card_count",
            "priced_count", "unpriced_count", "last_updated"
        ]]
    else:
        # Keep exactly acceptance-criteria columns in this order
        agg = agg[["set_name", "total_value", "avg_price", "card_count", "last_updated"]]

    return agg

# Task 2 - Set Statistics Calculation

import pandas as pd
import numpy as np
from math import sqrt
from typing import Dict, Any, List

def _parse_time_range(now: pd.Timestamp, time_range: str) -> pd.Timestamp:
    """
    Convert a simple string like '1W','1M','3M','6M','1Y','ALL' into a cutoff Timestamp.
    'ALL' returns a very early date so no rows are filtered out.
    """
    tr = time_range.upper() if isinstance(time_range, str) else "1M"
    if tr == "ALL":
        return pd.Timestamp("1970-01-01")
    if tr.endswith("W"):
        weeks = int(tr[:-1])
        return now - pd.Timedelta(weeks=weeks)
    if tr.endswith("M"):
        months = int(tr[:-1])
        return now - pd.DateOffset(months=months)
    if tr.endswith("Y"):
        years = int(tr[:-1])
        return now - pd.DateOffset(years=years)
    # fallback to 1 month
    return now - pd.DateOffset(months=1)

def calculate_set_statistics(
    set_name: str,
    price_history: pd.DataFrame,
    time_range: str = "1M",
    *,
    card_id_col: str = "card_id",
    date_col: str = "date",
    price_col: str = "price",
    set_col: str = "set_name",
    top_n: int = 3
) -> Dict[str, Any]:
    """
    Calculate advanced statistics for a Pokemon set.

    Returns dictionary:
      {
        'value_change_pct': float or None,
        'volatility': float or None,           # annualized volatility in percent
        'top_cards': list[dict],               # each dict: {'card_id', 'first', 'last', 'change_pct'}
        'health_score': float,                 # 0-100
        'trend': str,                          # e.g. 'Strong Up', 'Slight Up', 'Flat', ...
        'daily_values': pd.Series (date-indexed) # optional time series of set value (can be dropped)
      }
    Notes / assumptions:
    - Dates are normalized to day resolution.
    - For the set-level daily value series we carry forward last known price per card,
      which produces a realistic portfolio valuation across days with sparse records.
    """
    if set_col not in price_history.columns:
        raise KeyError(f"price_history missing set column '{set_col}'")

    # make a local copy
    ph = price_history.copy()

    # normalize column names / parse dates
    if date_col not in ph.columns:
        raise KeyError(f"price_history missing date column '{date_col}'")
    ph[date_col] = pd.to_datetime(ph[date_col], errors="coerce")
    ph = ph[ph[date_col].notna()].copy()  # drop rows w/ invalid date

    # filter to the set
    set_df = ph[ph[set_col] == set_name].copy()
    if set_df.empty:
        # return sensible empty result
        return {
            "value_change_pct": None,
            "volatility": None,
            "top_cards": [],
            "health_score": 0.0,
            "trend": "No Data",
            "daily_values": pd.Series(dtype=float)
        }

    # parse cutoff from time_range
    now = pd.Timestamp.now()
    cutoff = _parse_time_range(now, time_range)
    window_df = set_df[set_df[date_col] >= cutoff].copy()
    if window_df.empty:
        # if nothing in window, fall back to using all available data for set
        window_df = set_df.copy()

    # normalize to date (day resolution)
    window_df["day"] = window_df[date_col].dt.normalize()

    # Build a daily time series of set valuation:
    # 1) get last observed price per (day, card) -> pivot to table (rows days, cols card_id)
    # 2) reindex to full day range and forward-fill per card (carry last known price)
    # 3) sum across cards to get daily total value
    grouped_last_per_day = (
        window_df.sort_values(date_col)
                 .groupby(["day", card_id_col])[price_col]
                 .last()
                 .unstack(level=-1)  # columns become card IDs
    )

    # full date index from earliest day in window to latest
    full_idx = pd.date_range(start=grouped_last_per_day.index.min(),
                             end=grouped_last_per_day.index.max(),
                             freq="D")
    grouped_last_per_day = grouped_last_per_day.reindex(full_idx)

    # forward-fill each card's last known price across days (so a card's last price carries forward)
    grouped_ffill = grouped_last_per_day.ffill(axis=0).fillna(0.0)  # treat no-known-price as 0

    # daily total value (float series)
    daily_values = grouped_ffill.sum(axis=1).rename("set_total_value")

    # Clean: if less than 2 days of data, volatility / returns won't be computable; handle gracefully
    if len(daily_values) < 2 or daily_values.isna().all():
        value_change_pct = None
        volatility_pct_annualized = None
    else:
        first_value = float(daily_values.iloc[0])
        last_value = float(daily_values.iloc[-1])
        value_change_pct = None if first_value == 0 else ((last_value - first_value) / first_value) * 100.0

        # daily returns
        daily_returns = daily_values.pct_change().dropna()
        # volatility (annualized) in percent: std(daily_returns) * sqrt(252) * 100
        vol_daily = float(daily_returns.std(ddof=0)) if not daily_returns.empty else 0.0
        volatility_pct_annualized = vol_daily * sqrt(252) * 100.0

    # TOP CARDS: compute first & last price per card in the window (based on chronological earliest and latest rows)
    card_agg = window_df.sort_values(date_col).groupby(card_id_col)[price_col].agg(['first', 'last'])
    if not card_agg.empty:
        # safety: coerce numeric
        card_agg['first'] = pd.to_numeric(card_agg['first'], errors='coerce')
        card_agg['last'] = pd.to_numeric(card_agg['last'], errors='coerce')

        # compute relative change, handle first==0 or NaN
        def _safe_change(row):
            f = row['first']
            l = row['last']
            if pd.isna(f) and pd.isna(l):
                return np.nan
            if pd.isna(f) or f == 0:
                # if first is zero or missing, use absolute change normalized by max(abs(last),1)
                denom = max(abs(l) if not pd.isna(l) else 0.0, 1.0)
                return ((l - (f if not pd.isna(f) else 0.0)) / denom) * 100.0
            return ((l - f) / f) * 100.0

        card_agg['change_pct'] = card_agg.apply(_safe_change, axis=1).astype(float)
        top_cards_df = card_agg.sort_values('change_pct', ascending=False).head(top_n)
        # create list of dicts for clarity
        top_cards = [
            {
                "card_id": idx,
                "first": float(row['first']) if not pd.isna(row['first']) else None,
                "last": float(row['last']) if not pd.isna(row['last']) else None,
                "change_pct": float(row['change_pct']) if not pd.isna(row['change_pct']) else None
            }
            for idx, row in top_cards_df.iterrows()
        ]
    else:
        top_cards = []

    # Health score: combine three components into 0-100
    #  - trend_score (0..40): linear mapping where +10% => 40 points; negative or zero => 0
    #  - volatility_score (0..30): 0 vol =>30, 100%+ vol =>0
    #  - value_score (0..30): last_value scaled so high-value sets get higher score; cap at 30
    last_value_for_score = float(daily_values.iloc[-1]) if (len(daily_values) > 0 and not daily_values.isna().all()) else 0.0

    # trend_score
    if value_change_pct is None:
        trend_score = 0.0
    else:
        trend_score = max(0.0, min(40.0, (value_change_pct / 10.0) * 40.0))  # 10% => 40 pts; negatives -> 0

    # volatility_score
    if volatility_pct_annualized is None:
        volatility_score = 0.0
    else:
        volatility_score = max(0.0, min(30.0, 30.0 * (1.0 - (volatility_pct_annualized / 100.0))))
        # if vol=0 ->30; vol=100 ->0

    # value_score: scale last_value by a "meaningful" scale and cap at 30.
    # choose scale = 1000 (i.e., 1000 total value => 30 points). Adjust as needed for your domain.
    value_scale = 1000.0
    if last_value_for_score <= 0:
        value_score = 0.0
    else:
        value_score = min(30.0, (last_value_for_score / value_scale) * 30.0)

    health_score = trend_score + volatility_score + value_score
    # clamp 0..100
    health_score = float(max(0.0, min(100.0, health_score)))

    # Trend classification (sensible buckets)
    if value_change_pct is None:
        trend = "No Data"
    else:
        if value_change_pct >= 10.0:
            trend = "Strong Up"
        elif value_change_pct >= 2.0:
            trend = "Slight Up"
        elif -2.0 < value_change_pct < 2.0:
            trend = "Flat"
        elif value_change_pct <= -10.0:
            trend = "Strong Down"
        else:
            trend = "Slight Down"

    # Pack results
    result = {
        "value_change_pct": float(value_change_pct) if value_change_pct is not None else None,
        "volatility": float(volatility_pct_annualized) if volatility_pct_annualized is not None else None,
        "top_cards": top_cards,
        "health_score": health_score,
        "trend": trend,
        "daily_values": daily_values  # caller can drop or inspect this series
    }
    return result