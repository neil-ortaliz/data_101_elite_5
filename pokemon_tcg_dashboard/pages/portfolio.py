import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd

import plotly.graph_objects as go
from utils import get_image_urls, calculate_holdings_price_change
from components import ban_card_container, graph_container, tab_card_container, table_container
from components.portfolio_ui import create_portfolio_summary_metrics, create_risk_indicators, create_holdings_table

from global_variables import PRICE_HISTORY_DF, CARD_METADATA_DF

import logging
logger = logging.getLogger(__name__)

dash.register_page(__name__, path="/portfolio",
                    title="Portfolio", 
                    name="Portfolio",
                    order=2)


select = dbc.Row([
    dbc.Select(
        id="select-portfolio",
        options=[
            {"label": "24 Hours", "value": "1"},
            {"label": "7 Days", "value": "7"},
            {"label": "30 Days", "value": "30"},
            {"label": "3 Months", "value": "90"},
            {"label": "1 Year", "value": "365"},
            {"label": "All Time", "value": "-1"},
        ],
        value="30"
    )
], class_name="mb-3")

ban_row = dbc.Row([
    dbc.Col([
        ban_card_container(fig=go.Figure(),title="Total Portfolio Value")
    ]),
    dbc.Col([
        ban_card_container(fig=go.Figure(),title="Original Cost Basis")
    ]),
    dbc.Col([
        ban_card_container(fig=go.Figure(),title="Unrealized Gain/Loss")
    ]),
    dbc.Col([
        ban_card_container(fig=go.Figure(), title="Value Change", header_id="ban-value-change")
    ]),
], class_name="g-3 mb-3")

graph_row = dbc.Row([
        dbc.Col([graph_container(fig=go.Figure(), title="Portfolio Performance Vs Market")]),
        dbc.Col([graph_container(fig=go.Figure(), title="Collection Breakdown by Set")]),
], class_name="g-3 mb-3")

grade_distribution_row = dbc.Row([
    dbc.Col([graph_container(fig=go.Figure(), title="⭐ Grade Distribution (Your Portfolio vs Market Average)")]),
], class_name="g-3 mb-3")

risk_row = dbc.Row([
    dbc.Col([graph_container(fig=go.Figure(), title="⚠️ Risk & Intelligence Metrics")]),
], class_name="g-3 mb-3")

holding_row = dbc.Row([
    dbc.Col([graph_container(fig=go.Figure(), title="📋 Holdings Details")]),
], class_name="g-3 mb-3")

owned_cards = html.Div(
            id="portfolio-image-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
                "gap": "16px"
            }
        )

portfolio = html.Div([
    html.Br(),
    select,
    html.Div(id="portfolio-metrics-row"),
    create_risk_indicators(),
    html.H3('Holdings Details', className="mt-4 mb-3"),
    table_container(create_holdings_table(), title="", container_id="holdings-table-container"),
])

tabs = dbc.Tabs(
    [
        dbc.Tab(tab_card_container(owned_cards), label="Owned Cards"),
        dbc.Tab(tab_card_container(portfolio), label="Portfolio")
    ]
)

layout = html.Div([
    dcc.Location(id="portfolio-url"),
    tabs
])

@callback(
    Output("portfolio-image-grid", "children"),
    Input("selected-cards", "data")
)
def show_portfolio(selected_ids):
    if not selected_ids:
        return html.Div("No selected cards for your portfolio")
    
    selected_ids_list = [item['tcgPlayerId'] for item in selected_ids]
    portfolio_df = get_image_urls(ids=selected_ids_list)
    #print(portfolio_df)

    cards = []
    for _, row in portfolio_df.iterrows():
        cards.append(
            dbc.Button(
                dbc.Card(
                    [dbc.CardImg(
                                src=row["imageUrl"], 
                                top=True,
                                class_name="card-image"),
                    dbc.CardImgOverlay(
                        dbc.CardBody(
                            dbc.Button("View Details", color="Link")
                        ),
                        class_name="hover-overlay"
                    ),
                    dbc.CardFooter([
                        html.H4(row["name"], className="card-text")])],
                    class_name="card-normal",
                    style={
                        "borderRadius": "8px"
                    }
                ),
                id={"type": "portfolio-card-button", "index": row["tcgPlayerId"]},
                style={"padding": 0, 
                    "border": "none",
                    "background": "none",
                    "maxWidth": "150px",
                    "maxHeight": "200px",
                    #"width": "100%",
                    "height": "auto",},
                href=f"/card/{row['tcgPlayerId']}",
            )
        )

    return cards

'''@callback(
    Output("ban-value-change", "children"),
    Input("select-portfolio", "value")
)
def update_gain_loss_title(timeframe):
    print(f"Selected timeframe: {timeframe}")
    return f"{timeframe}-Day Change"'''

@callback(
    Output("portfolio-metrics-row", "children"),
    Input("portfolio-url", "pathname"),
    State("selected-cards", "data"),
)
def update_portfolio_metrics(pathname, selected_cards):
    logger.debug(f"Pathname: {pathname}")
    logger.debug(f"Selected Cards: {selected_cards}")
    selected_cards_df = pd.DataFrame(data=selected_cards)
    portfolio_metrics = create_portfolio_summary_metrics(selected_cards=selected_cards_df)
    return portfolio_metrics


@callback(
    Output("holdings-table-container", "children"),
    Input("portfolio-url", "pathname"),
    State("selected-cards", "data"),
)
def update_portfolio_metrics(pathname, selected_cards):
    logger.debug(f"Pathname: {pathname}")
    logger.debug(f"Selected Cards: {selected_cards}")
    calc_holding_cards = calculate_holdings_price_change(selected_cards)
    logger.debug(f"Calculated Holdings Cards: {calc_holding_cards}")
    portfolio_metrics = create_holdings_table(data=selected_cards)

    return portfolio_metrics
