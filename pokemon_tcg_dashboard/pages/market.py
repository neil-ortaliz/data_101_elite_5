import dash
from dash import html, dcc

import dash_bootstrap_components as dbc

from components import ban_card_container, graph_container
from components.market_ui import create_market_overview_metrics, create_market_filters, create_top_movers_table
from components.charts import market_view_set_performance_bar_chart

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

ban_row = create_market_overview_metrics()

layout = html.Div([
    create_market_filters(),
    select,
    html.Br(),
    dbc.Stack([
            ban_row,
            html.Div([
                dcc.Graph(
                    id="set-performance-chart",
                    figure=market_view_set_performance_bar_chart()
                )
                #graph_container(, title="Top Price Movers")
                #market_view_set_performance_bar_chart()
            ]),
            html.Div([
                html.H4("Top Price Movers", className="mb-3"),
                create_top_movers_table()
            ])
        ],
        gap=2),
    
])