import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd

from global_variables import SET_PRICE_HISTORY_DFS

import logging
logger = logging.getLogger(__name__)

def create_set_line_chart(set_names:list[str]=None, days:int=-1):
    """
    Create a line chart for the given set names over the specified number of days.
    
    Args:
        set_names (list[str]): List of set names to include in the chart.
        days (int): Number of days to look back for the data. If -1, include all data"""
    


    sets_df = SET_PRICE_HISTORY_DFS.copy()
    if days > 0:
        sets_df = sets_df[sets_df.index >= (sets_df.index.max() - pd.Timedelta(days=days))]

    if set_names:
        if isinstance(set_names, str):
            set_names = [set_names]

        sets_df = sets_df[sets_df['set_name'].isin(set_names)]

    fig = go.Figure()
    
    # assuming your dataframes are stored in a list called `dfs`
    for set_name, group_df in sets_df.groupby('set_name'):
        #set_name = df['set_name'].iloc[0]  # constant per dataframe
        fig.add_trace(
            go.Scatter(
                x=group_df.index,
                y=group_df['price'],
                mode='lines',
                name=set_name
            )
        )

    fig.update_layout(
        title="Price History by Set",
        xaxis_title="Date",
        yaxis_title="Market Price",
        template="plotly_white"
    )

    return fig