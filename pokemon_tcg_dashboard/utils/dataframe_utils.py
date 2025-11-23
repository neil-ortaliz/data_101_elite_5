import pandas as pd
from utils.loader import get_image_urls

import logging
logger = logging.getLogger(__name__)

def filter_dataframe_by_ids(
        df: pd.DataFrame, 
        id_list: list, 
        id_column: str = 'tcgPlayerId') -> pd.DataFrame:
    
    logger.info("Filtering DataFrame for Portfolio")
    df = get_image_urls()
    mask = df[id_column].isin(id_list)
    filtered_df = df[mask]
    return filtered_df