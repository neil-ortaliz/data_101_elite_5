from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent     # project root
DATA_DIR = BASE_DIR / "data"

def load_data(filename: str) -> pd.DataFrame:
    """Load data from a CSV file into a pandas DataFrame."""
    return pd.read_csv(DATA_DIR / filename)

def get_image_urls(filename: str="cards_metadata_table.csv") -> pd.DataFrame:
    metadata_df = load_data(filename)
    return metadata_df[['tcgPlayerId','setName','name', 'rarity','imageUrl']]