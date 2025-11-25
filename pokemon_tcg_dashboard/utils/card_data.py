from __future__ import annotations 
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, TypedDict


class PricePoint(TypedDict):
    date: str
    price: float

class CardData(TypedDict):
    card_id: str
    name: str
    set: str
    rarity: str
    card_number: str
    image_url: str
    current_price: str
    psa_grade: str
    psa_price: str
    ungraded_price: str
    total_listings: int
    price_history: List[PricePoint]
    condition: str

class AggregatedPrices(TypedDict):
    average_price: float
    median_price: float
    min_price: float
    max_price: float
    confidence: str
    sample_size: int


# ==========================================================
# CardDataFetcher CLASS (All Numerical Returns Formatted)
# ==========================================================

class CardDataFetcher:
    """Handles fetching and structuring individual card data with formatted price outputs."""

    def __init__(
        self,
        card_metadata_df: pd.DataFrame,
        price_history_df: pd.DataFrame,
        ebay_prices_df: pd.DataFrame
    ) -> None:

        required_meta_cols = {'id', 'name', 'setName', 'rarity'}
        required_price_cols = {'id', 'date', 'market', 'condition'}
        required_ebay_cols = {'id', 'date', 'grade', 'average'}

        if not required_meta_cols.issubset(card_metadata_df.columns):
            raise ValueError(f"card_metadata_df missing required columns: {required_meta_cols}")
        if not required_price_cols.issubset(price_history_df.columns):
            raise ValueError(f"price_history_df missing required columns: {required_price_cols}")
        if not required_ebay_cols.issubset(ebay_prices_df.columns):
            raise ValueError(f"ebay_prices_df missing required columns: {required_ebay_cols}")

        self.card_metadata: pd.DataFrame = card_metadata_df.copy()
        self.price_history: pd.DataFrame = price_history_df.copy()
        self.ebay_prices: pd.DataFrame = ebay_prices_df.copy()

        self.price_history["date"] = pd.to_datetime(self.price_history["date"], errors="coerce").dt.tz_localize(None)
        self.ebay_prices["date"] = pd.to_datetime(self.ebay_prices["date"], errors="coerce").dt.tz_localize(None)

        self._cache: Dict[Tuple[Any, ...], CardData] = {}

    # -------------------- HELPER --------------------
    def format_value(self, value: float, sign: str = "") -> str:
        if abs(value) >= 1_000_000:
            return f"{sign}${abs(value)/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"{sign}${abs(value)/1_000:.1f}K"
        else:
            return f"{sign}${abs(value):.2f}"

    # ==========================================================
    # Main Card Retrieval
    # ==========================================================
    def get_card_by_id(
        self,
        card_id: str,
        use_cache: bool = True,
        days: Optional[int] = None,
        psa: str = "psa9",
        condition: str = "any"
    ) -> Optional[CardData]:

        cache_key = (card_id, days, psa, condition)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        card_info_df = self.card_metadata[self.card_metadata["tcgPlayerId"] == card_id]
        if card_info_df.empty:
            return None

        card_info = card_info_df.iloc[0]

        current_price = self.get_current_market_price(card_id, days=days, condition=condition)
        psa_price = self.get_psa_price(card_id, psa, days=days)
        ungraded_price = self.get_ungraded_price(card_id, days=days, condition=condition)
        total_listings = self.count_active_listings(card_id, days=days, condition=condition)
        price_history = self.get_price_history(card_id, days=days, condition=condition)

        card_data: CardData = {
            "card_id": card_id,
            "name": card_info["name"],
            "set": card_info.get("setName", card_info.get("set", "N/A")),
            "rarity": card_info["rarity"],
            "card_number": card_info.get("cardNumber", "N/A"),
            "image_url": card_info.get("imageUrl", ""),
            "current_price": current_price,
            "psa_grade": psa,
            "psa_price": psa_price,
            "ungraded_price": ungraded_price,
            "total_listings": total_listings,
            "price_history": price_history,
            "condition": condition
        }

        self._cache[cache_key] = card_data
        return card_data

    # ==========================================================
    # Price Functions (Formatted)
    # ==========================================================
    def get_current_market_price(
        self,
        card_id: str,
        days: Optional[int] = 7,
        condition: str = "any"
    ) -> str:
        cutoff = None if days is None else datetime.now() - timedelta(days=days)
        df = self.price_history[self.price_history["id"] == card_id]
        if condition != "any":
            df = df[df["condition"] == condition]
        if cutoff:
            df = df[df["date"] >= cutoff]
        if df.empty:
            return self.format_value(0.0)
        avg_price = float(df["market"].mean())
        return self.format_value(avg_price)

    def get_psa_price(
        self,
        card_id: str,
        grade: str,
        days: Optional[int] = None
    ) -> str:
        grade_norm = grade.replace(" ", "").lower()
        df = self.ebay_prices[self.ebay_prices["id"] == card_id]
        df = df[df["grade"].str.replace(" ", "").str.lower() == grade_norm]
        if df.empty:
            return "N/A"
        if days is not None:
            cutoff = datetime.now() - timedelta(days=days)
            df_recent = df[df["date"] >= cutoff]
            if not df_recent.empty:
                df = df_recent
        latest = float(df.sort_values("date").iloc[-1]["average"])
        return self.format_value(latest)

    def get_ungraded_price(
        self,
        card_id: str,
        days: Optional[int] = 30,
        condition: str = "Near Mint"
    ) -> str:
        df = self.price_history[self.price_history["id"] == card_id]
        if condition != "any":
            df = df[df["condition"] == condition]
        if df.empty:
            return self.format_value(0.0)
        cutoff = None if days is None else datetime.now() - timedelta(days=days)
        recent = df if cutoff is None else df[df["date"] >= cutoff]
        if recent.empty:
            recent = df
        avg_price = float(recent["market"].mean())
        return self.format_value(avg_price)

    # ==========================================================
    # Listings & History
    # ==========================================================
    def count_active_listings(
        self,
        card_id: str,
        days: Optional[int] = 7,
        condition: str = "any"
    ) -> int:
        cutoff = None if days is None else datetime.now() - timedelta(days=days)
        df = self.price_history[self.price_history["id"] == card_id]
        if condition != "any":
            df = df[df["condition"] == condition]
        if cutoff:
            df = df[df["date"] >= cutoff]
        return int(df["date"].nunique())

    def get_price_history(
        self,
        card_id: str,
        days: Optional[int] = None,
        condition: str = "any"
    ) -> List[PricePoint]:
        cutoff = None if days is None else datetime.now() - timedelta(days=days)
        df = self.price_history[self.price_history["id"] == card_id]
        if condition != "any":
            df = df[df["condition"] == condition]
        if cutoff:
            df = df[df["date"] >= cutoff]
        if df.empty:
            return []
        daily_avg = df.groupby("date")["market"].mean().reset_index()
        return [
            {"date": d.strftime("%Y-%m-%d"), "price": float(self.format_value(p).replace('$','').replace('K','000').replace('M','000000'))}
            for d, p in zip(daily_avg["date"], daily_avg["market"])
        ]

    # ==========================================================
    # Aggregation (Formatted)
    # ==========================================================
    def aggregate_prices(
        self,
        card_id: str,
        condition: str = "any",
        grade: Optional[str] = None,
        days: Optional[int] = None
    ) -> AggregatedPrices:
        if grade:
            grade_norm = grade.replace(" ", "").lower()
            df = self.ebay_prices[self.ebay_prices["id"] == card_id]
            df = df[df["grade"].str.replace(" ", "").str.lower() == grade_norm]
            price_col = "average"
        else:
            df = self.price_history[self.price_history["id"] == card_id]
            if condition != "any":
                df = df[df["condition"] == condition]
            price_col = "market"
        if df.empty:
            return {
                "average_price": self.format_value(0.0),
                "median_price": self.format_value(0.0),
                "min_price": self.format_value(0.0),
                "max_price": self.format_value(0.0),
                "confidence": "none",
                "sample_size": 0,
            }
        if days is not None:
            cutoff = datetime.now() - timedelta(days=days)
            recent = df[df["date"] >= cutoff]
            if recent.empty:
                recent = df
        else:
            recent = df
        prices = recent[price_col]
        Q1 = prices.quantile(0.25)
        Q3 = prices.quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        filtered = prices[(prices >= lower) & (prices <= upper)]
        if filtered.empty:
            filtered = prices
        avg_price = float(filtered.mean())
        med_price = float(filtered.median())
        min_price = float(filtered.min())
        max_price = float(filtered.max())
        n = len(filtered)
        spread = max_price - min_price
        rel_spread = (spread / avg_price * 100) if avg_price > 0 else 100
        if n >= 20 and rel_spread < 20:
            confidence = "high"
        elif n >= 10 and rel_spread < 40:
            confidence = "medium"
        else:
            confidence = "low"
        return {
            "average_price": self.format_value(avg_price),
            "median_price": self.format_value(med_price),
            "min_price": self.format_value(min_price),
            "max_price": self.format_value(max_price),
            "confidence": confidence,
            "sample_size": n,
        }

    def get_price_comparison(
        self,
        card_id: str,
        days: Optional[int] = None
    ) -> Dict[str, AggregatedPrices]:
        return {
            "ungraded_nm": self.aggregate_prices(card_id, condition="Near Mint", days=days),
            "psa_8": self.aggregate_prices(card_id, grade="psa8", days=days),
            "psa_9": self.aggregate_prices(card_id, grade="psa9", days=days),
            "psa_10": self.aggregate_prices(card_id, grade="psa10", days=days)
        }

# ==========================================================
# __main__
# ==========================================================

if __name__ == "__main__":

    price_history_df: pd.DataFrame = pd.read_csv(
        "pokemon_tcg_dashboard/data/price_history.csv",
        parse_dates=["date"]
    )

    card_metadata_df: pd.DataFrame = pd.read_csv(
        "pokemon_tcg_dashboard/data/cards_metadata_table.csv"
    )

    ebay_price_history_df: pd.DataFrame = pd.read_csv(
        "pokemon_tcg_dashboard/data/ebay_price_history.csv",
        parse_dates=["date"]
    )

    fetcher = CardDataFetcher(card_metadata_df, price_history_df, ebay_price_history_df)

    test_card_id: str = "68af6bbbd14a00763202573c"
    test_days: int = 7
    test_psa_grade: str = "psa10"
    test_condition: str = "Near Mint"

    card_data: Optional[CardData] = fetcher.get_card_by_id(
        card_id=test_card_id,
        days=test_days,
        psa=test_psa_grade,
        condition=test_condition
    )

    price_comparison: Dict[str, AggregatedPrices] = fetcher.get_price_comparison(
        card_id=test_card_id,
        days=test_days
    )

    print("\n=== CARD DATA ===")
    print(card_data)

    print("\n=== PRICE COMPARISON ===")
    print(price_comparison)
