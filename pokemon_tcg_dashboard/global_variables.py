from utils import load_data, get_set_price_history
from utils.card_data import CardDataFetcher
import pandas as pd

PRICE_HISTORY_DF = load_data("price_history.csv", parse_dates=['date'])
CARD_METADATA_DF = load_data("cards_metadata_table.csv")
EBAY_METADATA_DF = load_data("ebay_price_history.csv", parse_dates=["date"])
MAP_LOCATIONS_DF = load_data("pokemon_tcg_stores.csv")
RELEASE_DATE_DF = load_data("set_release_date.csv", parse_dates=["release_date"])

MAP_LOCATIONS_DF.reset_index(inplace=True)
RELEASE_DATE_DF.reset_index(inplace=True)

EBAY_METADATA_DF["date"] = EBAY_METADATA_DF["date"].dt.date
RELEASE_DATE_DF["release_date"] = RELEASE_DATE_DF["release_date"].dt.date

PRICE_HISTORY_DF["date"] = pd.to_datetime(PRICE_HISTORY_DF["date"], errors="coerce").dt.tz_localize(None)
EBAY_METADATA_DF["date"] = pd.to_datetime(EBAY_METADATA_DF["date"], errors="coerce").dt.tz_localize(None)
RELEASE_DATE_DF["release_date"] = pd.to_datetime(RELEASE_DATE_DF["release_date"], errors="coerce").dt.tz_localize(None)

CARD_DATA_FETCHER = CardDataFetcher(CARD_METADATA_DF, PRICE_HISTORY_DF, EBAY_METADATA_DF)

SET_PRICE_HISTORY_DFS = get_set_price_history()
SET_OPTIONS = sorted(CARD_METADATA_DF["setName"].dropna().unique())
RARITY_OPTIONS = sorted(CARD_METADATA_DF["rarity"].dropna().unique())

FALLBACK_IMAGE = "/assets/no_image_available.jpg"