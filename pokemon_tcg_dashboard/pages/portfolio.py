import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
from utils import get_image_urls
from components.portfolio_ui import create_portfolio_summary_metrics

dash.register_page(__name__, path="/portfolio",
                    title="Portfolio", 
                    name="Portfolio",
                    order=2)


owned_cards = html.Div(
            id="portfolio-image-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
                "gap": "16px"
            }
        )

portfolio = html.Div([
    create_portfolio_summary_metrics(),
    html.H3('Portfolio Details'),
    html.Div('More portfolio content will go here.'),
])

tabs = dbc.Tabs(
    [
        dbc.Tab(owned_cards, label="Owned Cards"),
        dbc.Tab(portfolio, label="Portfolio")
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
            html.Button(
                dbc.Card(
                    dbc.CardImg(src=row["imageUrl"], top=True),
                    class_name="card-normal",
                    style={"borderRadius": "8px"}
                ),
                id={"type": "card-button", "index": row["tcgPlayerId"]},
                style={"padding": 0, "border": "none", "background": "none"}
            )
        )

    return cards