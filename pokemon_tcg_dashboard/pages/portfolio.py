import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
from utils import get_image_urls
from components import ban_card_container, graph_container, tab_card_container

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
        ],
        value="30"
    )
], class_name="mb-3")

ban_row = dbc.Row([
    dbc.Col([
        ban_card_container(fig="total portfolio value goes here",title="Total Portfolio Value")
    ]),
    dbc.Col([
        ban_card_container(fig="change goes here",title="Original Cost Basis")
    ]),
    dbc.Col([
        ban_card_container(fig="unrealized gain/loss here ",title="Unrealized Gain/Loss")
    ]),
    dbc.Col([
        ban_card_container(fig="change fig goes here", title="Value Change", header_id="ban-value-change")
    ]),
], class_name="g-3 mb-3")

graph_row = dbc.Row([
        dbc.Col([graph_container(fig="portfolio performance graph goes here", title="Portfolio Performance Vs Market")]),
        dbc.Col([graph_container(fig="pie chart collection breakdown goes here", title="Collection Breakdown by Set")]),
], class_name="g-3 mb-3")

grade_distribution_row = dbc.Row([
    dbc.Col([graph_container(fig="grade distribution graph goes here", title="⭐ Grade Distribution (Your Portfolio vs Market Average)")]),
], class_name="g-3 mb-3")

risk_row = dbc.Row([
    dbc.Col([graph_container(fig="risk and intelligence metrics", title="⚠️ Risk & Intelligence Metrics")]),
], class_name="g-3 mb-3")

holding_row = dbc.Row([
    dbc.Col([graph_container(fig="holding portfolio table here", title="📋 Holdings Details")]),
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
    ban_row,
    graph_row,
    grade_distribution_row,
    risk_row,
    holding_row
])

tabs = dbc.Tabs(
    [
        dbc.Tab(tab_card_container(owned_cards), label="Owned Cards"),
        dbc.Tab(tab_card_container(portfolio), label="Portfolio")
    ]
)

layout = html.Div([
    tabs
])

@callback(
    Output("portfolio-image-grid", "children"),
    Input("selected-cards", "data"
    )
)
def show_portfolio(selected_ids):
    if not selected_ids:
        return html.Div("No selected cards for your portfolio")
    
    portfolio_df = get_image_urls(ids=selected_ids)
    #print(portfolio_df)
    print(f"portfolio df type: {type(portfolio_df)}")

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

@callback(
    Output("ban-value-change", "children"),
    Input("select-portfolio", "value")
)
def update_gain_loss_title(timeframe):
    print(f"Selected timeframe: {timeframe}")
    return f"{timeframe}-Day Change"