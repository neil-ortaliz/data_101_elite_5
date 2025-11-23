import glob
import pandas as pd
import logging

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent     # project root
DATA_DIR = BASE_DIR / "data"

# Initialize module logger; application can configure handlers/levels.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def load_data(filename: str) -> pd.DataFrame:
    """Load data from a CSV file into a pandas DataFrame."""
    logger.debug("Loading data file: %s", filename)
    return pd.read_csv(DATA_DIR / filename, index_col=0)

def get_image_urls(filename: str="cards_metadata_table.csv", ids: list = []) -> pd.DataFrame:
    metadata_df = load_data(filename)
    metadata_df = metadata_df[['tcgPlayerId','setName','name', 'rarity','imageUrl']]
    if ids:
        mask = metadata_df['tcgPlayerId'].isin(ids)
        logger.debug("Filtered metadata dataframe type: %s", type(metadata_df[mask]))
        return metadata_df[mask]
    else:
        return metadata_df
    
def get_card_metadata(card_id) -> pd.Series:
    logger.debug("Fetching metadata for card_id: %s", card_id)
    metadata_df = load_data("cards_metadata_table.csv")
    card_row = metadata_df[metadata_df['tcgPlayerId'] == int(card_id)]
    #print(card_row)
    #print(metadata_df.dtypes)
    return card_row.squeeze()

def get_set_price_history() -> pd.DataFrame:
    set_price_history_dir = DATA_DIR / "set_price_history"
    all_set_df = pd.DataFrame()
    
    #logger.debug(f"Loading set price history from dir {set_price_history_dir}")
    for set_df in set_price_history_dir.glob("*.csv"):
        logger.info(f"Loading set price history from: {set_df}", )
        #logger.debug(f"cols: {df.columns}")
        df = pd.read_csv(set_df, parse_dates=["date"])
        df = df.rename(columns={"Near Mint": "price"})
        all_set_df = pd.concat([all_set_df, df], ignore_index=True)
    
    #logger.debug(f"all_set_df cols: {all_set_df.columns}")
    all_set_df = all_set_df.set_index("date")
    logger.debug("Unique values in all_set_df")
    return all_set_df