from utils import load_data, get_set_price_history
from utils.card_data import CardDataFetcher

PRICE_HISTORY_DF = load_data("price_history.csv", parse_dates=['date']).set_index('date')
CARD_METADATA_DF = load_data("cards_metadata_table.csv")
EBAY_METADATA_DF = load_data("ebay_price_history.csv", parse_dates=["date"]).set_index('date')

CARD_DATA_FETCHER = CardDataFetcher(CARD_METADATA_DF, PRICE_HISTORY_DF, EBAY_METADATA_DF)

SET_PRICE_HISTORY_DFS = get_set_price_history()