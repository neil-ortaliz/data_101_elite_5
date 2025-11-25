from utils import load_data

PRICE_HISTORY_DF = load_data("price_history.csv", parse_dates=['date']).set_index('date')
CARD_METADATA_DF = load_data("cards_metadata_table.csv")