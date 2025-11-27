from global_variables import CARD_METADATA_DF, PRICE_HISTORY_DF
import pandas as pd
import numpy as np

import logging
logger = logging.getLogger(__name__)

def calculate_top_movers(name:str=None, set_name:str=None, rarity:str=None, days:int=1, top_n=10, ascending:bool=True)-> dict:
    """
    Create a table showing the top price movers for cards.

    Args:
        name (str, optional): Filter by card name. Defaults to None. If None, select all.
                              Can contain a substring to match multiple cards.
        set_name (str or list, optional): Filter by set name(s). Defaults to None.
        rarity (str or list, optional): Filter by rarity/rarities. Defaults to None.
        days (int, optional): Number of days to consider for price movement. Defaults to 30.
        top_n (int, optional): Number of top movers to return. Defaults to 10.
        ascending (bool, optional): Whether to sort ascending (lowest movers first). Defaults to True.

    Returns:
        dict: A dictionary containing the name of card, set name, current price, price change and percentage change.
    """

    COLS = ['name', 'setName', 'current_price', 'price_change', 'pct_change']
    name = name.strip() if name else None
    price_history_df = PRICE_HISTORY_DF.copy()
    price_history_df = price_history_df.set_index('date')
    price_history_df = price_history_df[price_history_df['condition']=='Near Mint']
    if days == -1:
        days = (price_history_df.index.max() - price_history_df.index.min()).days

    meta_df = CARD_METADATA_DF.copy()
    
    if name:
        meta_df = meta_df[meta_df['name'].str.contains(name, case=False)]

    if set_name:
        if isinstance(set_name, list):
            meta_df = meta_df[meta_df['setName'].isin(set_name)]
        else:
            meta_df = meta_df[meta_df['setName']==set_name]

    if rarity:
        if isinstance(rarity, list):
            meta_df = meta_df[meta_df['rarity'].isin(rarity)]
        else:
            meta_df = meta_df[meta_df['rarity']==rarity]

    card_ids = meta_df['tcgPlayerId'].unique()

    df = price_history_df[price_history_df['tcgPlayerId'].isin(card_ids)]

 # Ensure datetime index
    df.index = pd.to_datetime(df.index)

    # 3. Compute dates
    max_date = df.index.max()
    past_date = max_date - pd.Timedelta(days=days)

    # 4. Latest price per card
    latest = (
        df.sort_values(['tcgPlayerId', df.index.name])
          .groupby('tcgPlayerId')
          .tail(1)[['tcgPlayerId', 'market']]
          .rename(columns={'market': 'current_price', 'setName': 'set_name'})
    )

    # 5. Price N days ago
    past = (
        df[df.index <= past_date]
          .sort_values(['tcgPlayerId', df.index.name])
          .groupby('tcgPlayerId')
          .tail(1)[['tcgPlayerId', 'market']]
          .rename(columns={'market': 'past_price', 'setName': 'set_name'})
    )

    # 6. Merge with metadata
    out = meta_df.merge(latest, on='tcgPlayerId', how='left')
    out = out.merge(past, on='tcgPlayerId', how='left')

    # 7. Calculate changes
    out['price_change'] = out['current_price'] - out['past_price']
    out['pct_change'] = out['price_change'] / out['past_price'] * 100

    # Handle missing
    out = out.replace([np.inf, -np.inf], np.nan)
    out[['past_price', 'price_change', 'pct_change']] = (
        out[['past_price', 'price_change', 'pct_change']].fillna("0")
    )

    # 8. Sort
    out = out.sort_values(
        by='pct_change',
        ascending=ascending,
        key=lambda c: pd.to_numeric(c, errors='coerce')
    )


    out["current_price"] = out["current_price"].map(lambda x: f"$ {float(x):,.2f}" if pd.notnull(x) else "")
    out["price_change"] = out["price_change"].map(lambda x: f"$ {float(x):+,.2f}" if pd.notnull(x) else "")
    out["pct_change"] = out["pct_change"].map(lambda x: f"{float(x):+.2f}%" if pd.notnull(x) else "")

    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    logger.debug(out[COLS].head(2).to_dict('records'))
    return out[COLS].head(top_n).to_dict('records')

def get_latest_price(card_id, df):
    today = pd.Timestamp.today().normalize()
    card_df = df[df["tcgPlayerId"] == card_id]
    if today in card_df.index:
        return card_df.loc[today, "market"]

    # 2 — else find the most recent available date BEFORE today
    earlier = card_df[card_df.index <= today]

    if earlier.empty:
        return None

    latest_row = earlier.sort_index().tail(1)
    return latest_row["market"].iloc[0]

def calculate_holdings_price_change(data: list[dict]):
    price_history_df = PRICE_HISTORY_DF.copy()
    price_history_df = price_history_df.set_index('date')
    price_history_df = price_history_df[price_history_df['condition'] == 'Near Mint']

    for card in data:
        card_df = price_history_df[price_history_df["tcgPlayerId"] == card['tcgPlayerId']]
        current_price = get_latest_price(card['tcgPlayerId'], card_df)

        logger.debug(f"current_price: {current_price}")
        if current_price is not None:
            price_change = current_price - card['buy_price']
            pct_change = (price_change / card['buy_price']) * 100
            card['current_price'] = f"$ {current_price:,.2f}"
            card['price_change'] = f"$ {price_change:,.2f}"
            card['pct_change'] = f"{pct_change:,.2f}%"
        else:
            card['current_price'] = 0
            card['price_change'] = 0
            card['pct_change'] = "0.00%"

        card['buy_price'] = f"$ {card['buy_price']:,.2f}"

    return data