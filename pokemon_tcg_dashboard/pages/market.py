import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import logging

import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components import ban_card_container, graph_container, create_set_line_chart, table_container
from components.market_ui import create_market_overview_metrics, create_market_filters, create_top_movers_table
from components.charts import market_view_set_performance_bar_chart, create_top_sets_table

from utils import calculate_top_movers

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
    dbc.Stack(
        [
            ban_row,
            dbc.Row([create_market_filters()]),
            dbc.Row([select]),
            dbc.Row([
                graph_container(
                    fig=create_set_line_chart(),
                    fig_id="set-performance-list",
                    title="Set Performance Overview"
                ),
            ]),
            dbc.Row([
                # html.H4("Top Price Movers", className="mb-3"),
                # create_top_movers_table(),
                table_container(
                    table="",
                    title="Top Price Movers (Set)",
                    #fig_id="top-movers-table-fig",
                    container_id="top-movers-table-fig"
                )
            ], id="top-movers-row"),
            dbc.Row([
                table_container(
                    table="",
                    title="Top Price Movers (Cards)",
                    #class_name="top-movers-card-table-fig",
                    container_id="top-movers-card-table-fig"
                )
            ])
        ],
    )
])

#logger.info("Market page layout constructed")

@callback(
    Output("market-overview-metrics-row", "children"),
    Input("select-market", "value")
)
def update_market_overview_metrics(days):
    logger.debug(f"Updating market overview metrics")
    days= int(days)
    ban_row = create_market_overview_metrics(days=days)
    return ban_row

@callback(
    Output("set-performance-list", "figure"),
    Input("select-market", "value"),
    Input("market-set-select", "value")
)
def update_set_performance_chart(days, set_names):
    logger.debug(f"Trigger: {ctx.triggered_id}")
    days= int(days)
    fig = create_set_line_chart(set_names=set_names, days=days)
    return fig

@callback(
    Output("top-movers-card-table-fig", "children"),
    Input("select-market", "value"),
    Input("market-set-select", "value"),
    Input("market-search-input", "value"),
    Input("market-rarity-select", "value")
)
def update_graphs(days, set_names, search_name, rarities):
    logger.debug(f"Trigger: {ctx.triggered_id}")
    days= int(days)
    top_movers_table = create_top_movers_table(calculate_top_movers(name=search_name,
                                               set_name=set_names,
                                               rarity=rarities,
                                               days=days,
                                               top_n=10,
                                               ascending=False))
    return top_movers_table


@callback(
    Output("top-movers-table-fig", "children"),
    Input("select-market", "value"),
    Input("market-set-select", "value"),
)
def update_top_movers_table(days, set_names):
    logger.debug("Updating top movers table....")
    days= int(days)
    fig=create_top_sets_table(days=days, set_names=set_names)
    return fig