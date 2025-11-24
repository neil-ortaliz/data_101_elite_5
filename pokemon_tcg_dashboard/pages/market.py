import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import logging

import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components import ban_card_container, graph_container
from components.market_ui import create_market_overview_metrics, create_market_filters, create_top_movers_table
from components.charts import market_view_set_performance_bar_chart, create_top_sets_table

# Initialize module logger; application can configure handlers/levels.
logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/",
                    title="Market", 
                    name="Market",
                    order=1)

select = dbc.Select(
    id="select-market",
    options=[
        {"label": "24 Hours", "value": 1},
        {"label": "7 Days", "value": 7},
        {"label": "1 Month", "value": 30},
        {"label": "3 Months", "value": 90},
        {"label": "1 Year", "value": 365},
        {"label": "All Time", "value": -1},
    ],
    value=30
)


ban_row = html.Div(
    create_market_overview_metrics(days=-1),
    id="market-overview-metrics-row")

layout = html.Div([
    create_market_filters(),
    select,
    html.Br(),
    dbc.Stack([
            ban_row,
            dbc.Row([
                graph_container(fig=go.Figure(), title="Set Performance Overview"),
            ]),
            dbc.Row([
                #html.H4("Top Price Movers", className="mb-3"),
                #create_top_movers_table(),
                graph_container(fig=go.Figure(), title="Top Price Movers", fig_id="top-movers-table-fig", container_id="top-movers-table-container")
            ],
            id="top-movers-row")
        ],
        gap=2),
    
])

#logger.info("Market page layout constructed")

@callback(
    Output("top-movers-table-fig", "figure"),
    Output("market-overview-metrics-row", "children"),
    Input("select-market", "value")
)
def update_graphs(days):
    days= int(days)
    fig=create_top_sets_table(days=days)
    ban_row = create_market_overview_metrics(days=days)
    print(type(ban_row))
    return fig, ban_row