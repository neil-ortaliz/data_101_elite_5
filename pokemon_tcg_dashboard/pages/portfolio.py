import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd

import plotly.graph_objects as go
from utils import get_image_urls
from components import ban_card_container, graph_container, tab_card_container
from components.portfolio_ui import create_portfolio_summary_metrics, create_risk_indicators, create_holdings_table

#from global_variables import PRICE_HISTORY_DF, CARD_METADATA_DF

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
            {"label": "All Time", "value": "all"},
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
    html.Div(id="portfolio-risk-row"),
    html.H3('Holdings Details', className="mt-4 mb-3"),
    create_holdings_table(),
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
    Input("select-portfolio", "value"),
    State("selected-cards", "data"),
)
def update_portfolio_metrics(pathname, value, selected_cards):
    logger.debug(f"Pathname: {pathname}")
    logger.debug(f"Timeframe: {value}")
    logger.debug(f"Selected Cards: {selected_cards}")

    if not selected_cards:
        return html.Div("No selected cards to calculate metrics.")

    selected_cards_df = pd.DataFrame(selected_cards)

    print(value)
    if value == "all":
        days = None
    else:
        days = int(value) 

    # Pass timeframe into your metrics function
    portfolio_metrics = create_portfolio_summary_metrics(
        selected_cards=selected_cards_df,
        days=days,  
    )

    return portfolio_metrics

@callback(
    Output("portfolio-risk-row", "children"),
    Input("select-portfolio", "value"),
    State("selected-cards", "data")
)
def update_risk_indicators(value, selected_cards):
    if not selected_cards:
        return html.Div("No cards selected for risk metrics.")
    
    selected_cards_df = pd.DataFrame(selected_cards)

    risk_row = create_risk_indicators(selected_cards=selected_cards_df)
    return risk_row