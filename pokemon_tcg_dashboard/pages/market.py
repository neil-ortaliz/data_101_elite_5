import dash
from dash import html, dcc

import dash_bootstrap_components as dbc

from components import ban_card_container, graph_container
from components.market_ui import create_market_overview_metrics

dash.register_page(__name__, path="/",
                    title="Market", 
                    name="Market",
                    order=1)

select = dbc.Select(
    id="select",
    options=[
        {"label": "24 Hours", "value": "1"},
        {"label": "7 Days", "value": "2"},
        {"label": "1 Month", "value": "3"},
        {"label": "3 Months", "value": "4"},
        {"label": "1 Year", "value": "5"},
    ],
)

ban_row = create_market_overview_metrics()

layout = html.Div([
    select,
    html.Br(),
    dbc.Stack([
            ban_row,
            html.Div([
                graph_container(fig="market graph goes here", title="Top Price Movers")
            ])
        ],
        gap=2),
    
])