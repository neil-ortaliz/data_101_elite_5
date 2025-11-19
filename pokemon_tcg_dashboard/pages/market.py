import dash
from dash import html, dcc

import dash_bootstrap_components as dbc

from components import ban_card_container, graph_container

dash.register_page(__name__, path="/",
                    title="Market", 
                    name="Market",
                    order=1)

select = dbc.Select(
    id="select",
    options=[
        {"label": "24 Hours", "value": "1"},
        {"label": "7 Days", "value": "7"},
        {"label": "1 Month", "value": "30"},
        {"label": "3 Months", "value": "90"},
        {"label": "1 Year", "value": "365"},
    ],
)

ban_row = dbc.Row([
            dbc.Col([
                ban_card_container(fig="total market view goes here",title="Total Market Value")
            ]),
            dbc.Col([
                ban_card_container(fig="change goes here",title="24h Change")
            ]),
            dbc.Col([
                ban_card_container(fig="best set goes here ",title="Best Set")
            ]),
            dbc.Col([
                ban_card_container(fig="active listings go here", title="Active Listings")
            ]),
            html.Div([
                graph_container(fig="market graph goes here", title="Market Performances")
            ])
        ], class_name="g-3 mb-3")

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