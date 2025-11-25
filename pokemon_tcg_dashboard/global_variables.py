from utils import load_data
from utils.card_data import CardDataFetcher
import pandas as pd

PRICE_HISTORY_DF = load_data("price_history.csv", parse_dates=['date'])
CARD_METADATA_DF = load_data("cards_metadata_table.csv")
EBAY_METADATA_DF = load_data("ebay_price_history.csv", parse_dates=["date"])
EBAY_METADATA_DF["date"] = EBAY_METADATA_DF["date"].dt.date

PRICE_HISTORY_DF["date"] = pd.to_datetime(PRICE_HISTORY_DF["date"], errors="coerce").dt.tz_localize(None)
EBAY_METADATA_DF["date"] = pd.to_datetime(EBAY_METADATA_DF["date"], errors="coerce").dt.tz_localize(None)

CARD_DATA_FETCHER = CardDataFetcher(CARD_METADATA_DF, PRICE_HISTORY_DF, EBAY_METADATA_DF)