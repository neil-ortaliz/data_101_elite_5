import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import logging

import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components import ban_card_container, graph_container, create_set_line_chart, table_container
from components.market_ui import create_market_overview_metrics, create_market_filters, create_top_movers_table, create_set_release_date_table
from components.charts import market_view_set_performance_bar_chart, create_top_sets_table
from utils.lgs_map import create_spatial_map
from global_variables import MAP_LOCATIONS_DF, RELEASE_DATE_DF, CARD_METADATA_DF
from global_variables import SET_OPTIONS

from utils import calculate_top_movers

# Initialize module logger; application can configure handlers/levels.
logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/",
                    title="Market", 
                    name="Market",
                    order=1)

market_set_filter = dbc.Row(
    [
        # Time range select
        dbc.Col(
            dbc.Select(
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
            ),
            width=6
        ),

        # Set filter dropdown
        dbc.Col(
            dcc.Dropdown(
                id="market-set-select",
                options=SET_OPTIONS,
                multi=True,
                placeholder="Filter by Set",
                clearable=False,
                style={"borderRadius": "5px"}
            ),
            width=6
        )
    ]
)

ban_row = html.Div(
    create_market_overview_metrics(days=-1),
    id="market-overview-metrics-row")

map_row = dbc.Row([
    dbc.Col([
        html.H4("Pokémon Store Locations", className="mb-3"),
        dcc.Graph(
            id="pokemon-store-map",
            figure=create_spatial_map(MAP_LOCATIONS_DF),
            style={'height': '500px', 'width': '100%'},
            config={'scrollZoom': True} 
        )
    ], width=7, style={'height': '500px', 'display': 'flex', 'flexDirection': 'column'}),

    dbc.Col([
        html.H4("Set Release Dates", className="mb-3"),
        html.Div(
            create_set_release_date_table(RELEASE_DATE_DF),
            style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'}
        )
    ], width=5, style={'display': 'flex', 'flexDirection': 'column', 'height': '100%'})
],
className="g-3",
style={'alignItems': 'stretch'})

layout = html.Div([
    dbc.Stack(
        [
            ban_row,
            dbc.Row([market_set_filter]),
            html.Hr(),
            dbc.Row([
                graph_container(
                    fig=create_set_line_chart(),
                    fig_id="set-performance-list",
                    title="Set Performance Overview"
                ),
            ]),
            html.Hr(),
            dbc.Row([
                # html.H4("Top Price Movers", className="mb-3"),
                # create_top_movers_table(),
                table_container(
                    table="",
                    title="Set Price Movements",
                    #fig_id="top-movers-table-fig",
                    container_id="top-movers-table-fig"
                )
            ], id="top-movers-row"),
            html.Hr(),
            dbc.Row([create_market_filters()]),
            html.Hr(),
            dbc.Row([
                table_container(
                    table="",
                    title="Top Price Movers (Cards)",
                    #class_name="top-movers-card-table-fig",
                    container_id="top-movers-card-table-fig"
                )
            ]),
            html.Hr(),
            map_row,
            html.Hr()
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
    if not set_names:
        set_names = None
        
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

    if not set_names:
        set_names = None
    if not search_name:
        search_name = None
    if not rarities:
        rarities = None

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

    if not set_names:
        set_names = None

    fig=create_top_sets_table(days=days, set_names=set_names)
    return fig


@callback(
    Output("market-set-select", "value"),
    Output("market-rarity-select", "value"),
    Output("market-search-input", "value"),
    Input("clear-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_all_filters(_):
    """Resets all filters instantly."""
    return None, None, ""


@callback(
    Output('main-url', 'pathname'),
    Input('top-movers-table', 'active_cell'),
    Input('top-movers-table', 'data'),
    prevent_initial_call=True
)
def display_click(active_cell, table_data):
    
    if active_cell:
        if active_cell['column_id'] == 'name':
            card_name = table_data[active_cell['row']][active_cell['column_id']]
            card_tcgplayerid = CARD_METADATA_DF.loc[CARD_METADATA_DF['name'] == card_name, "tcgPlayerId"].values[0]
            return f"card/{card_tcgplayerid}"
