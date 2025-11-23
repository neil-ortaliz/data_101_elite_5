import dash
from dash import html, dcc
import logging

import dash_bootstrap_components as dbc

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
    id="select",
    options=[
        {"label": "24 Hours", "value": "1"},
        {"label": "7 Days", "value": "7"},
        {"label": "1 Month", "value": "30"},
        {"label": "3 Months", "value": "90"},
        {"label": "1 Year", "value": "365"},
    ],
)

logger.debug("Market select component created with %d options", len(select.options))

ban_row = create_market_overview_metrics()
logger.debug("Market overview metrics created: %s", type(ban_row))

layout = html.Div([
    create_market_filters(),
    select,
    html.Br(),
    dbc.Stack([
            ban_row,
            #html.Div([
            #    dcc.Graph(
            #        id="set-performance-chart",
            #        figure=market_view_set_performance_bar_chart()
            #    )
            #    #graph_container(, title="Top Price Movers")
            #    #market_view_set_performance_bar_chart()
            #]),
            dbc.Row([
                html.H4("Top Price Movers", className="mb-3"),
                #create_top_movers_table(),
                graph_container(fig=create_top_sets_table(), title="Top Price Movers", fig_id="top-movers-table-fig")
            ])
        ],
        gap=2),
    
])

logger.info("Market page layout constructed")