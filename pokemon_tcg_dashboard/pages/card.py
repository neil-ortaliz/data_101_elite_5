import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
#from utils import get_card_metadata
from components import ban_card_container, graph_container, tab_card_container
from components.card_ui import create_card_header, create_action_buttons

from global_variables import CARD_DATA_FETCHER

#dash.register_page(__name__, path_template="/card/<report_id>")

dash.register_page(__name__, path_template="/card/<card_id>",
                    #title="Card View", 
                    #name="Card View",
                    )

import logging
logger = logging.getLogger(__name__)

def layout(card_id=None, **kwargs):
    
    card_gen_content = html.Div([
        html.Div(id="card-header-container"),  # This will be populated by callback
        html.Hr(),
        dbc.Row([
            html.Div([graph_container(fig="price charts here", title="Price History")])
        ])
    ])

    return html.Div([
        dcc.Location(id="url"),
        dcc.Location(id="redirect-404", refresh=True),
        dcc.Store(id="card-data-store"),  # Store for card data
        card_gen_content,
    ])


@callback(
    Output("card-header-container", "children"),
    Output("card-data-store", "data"),
    Output("redirect-404", "pathname"),
    Input("url", "pathname"),
)
def update_card_page(pathname):
    print(pathname)
    card_number = pathname.split("/")[-1]
    #print(f"card_number: {card_number}")
    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_number)
    logger.debug(f"card_metadata retrieved: {card_metadata}")
    if card_metadata is None:
        # GO TO 404 PAGE
        #return html.H3("Card Not Found"), None
        return dash.no_update, dash.no_update, "/page-not-found"
    
    else:
        # Prepare data for create_card_header
        card_data = {
            "name": card_metadata['name'],
            "set": card_metadata['setName'],
            "rarity": card_metadata['rarity'],
            "card_number": card_metadata['cardNumber'],
            "image_url": card_metadata['imageUrl'],
            "current_price": card_metadata['prices.market'],  
            "psa10_price": "$120.00",   # TODO: Get from Member 2
            "ungraded_price": "$38.50", # TODO: Get from Member 2
            "total_listings": 234       # TODO: Get from Member 2
        }

        # Return both header and action buttons
        card_content = html.Div([
            create_card_header(card_data),
            create_action_buttons()
        ])

        
        return card_content, card_data, dash.no_update
    