from utils import load_data, get_set_price_history
from utils.card_data import CardDataFetcher
import pandas as pd

PRICE_HISTORY_DF = load_data("price_history.csv", parse_dates=['date'])
CARD_METADATA_DF = load_data("cards_metadata_table.csv")
EBAY_METADATA_DF = load_data("ebay_price_history.csv", parse_dates=["date"])
EBAY_METADATA_DF["date"] = EBAY_METADATA_DF["date"].dt.date

PRICE_HISTORY_DF["date"] = pd.to_datetime(PRICE_HISTORY_DF["date"], errors="coerce").dt.tz_localize(None)
EBAY_METADATA_DF["date"] = pd.to_datetime(EBAY_METADATA_DF["date"], errors="coerce").dt.tz_localize(None)

CARD_DATA_FETCHER = CardDataFetcher(CARD_METADATA_DF, PRICE_HISTORY_DF, EBAY_METADATA_DF)

SET_PRICE_HISTORY_DFS = get_set_price_history()
SET_OPTIONS = sorted(CARD_METADATA_DF["setName"].dropna().unique())
RARITY_OPTIONS = sorted(CARD_METADATA_DF["rarity"].dropna().unique())