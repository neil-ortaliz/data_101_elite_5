import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
from utils import get_card_metadata
from components import ban_card_container, graph_container, tab_card_container

dash.register_page(__name__, path_template="/card/<card_id>")

def layout(card_id="", **kwargs):
    card_gen_content = html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardImg(src="", top=True, id="card-image", class_name="h-100", style={"height": "100%", "object-fit": "cover"})
                ),
                width=3,
                class_name="card-normal h-100",
                style={"padding": 0, 
                    "border": "none",
                    "background": "none",
                    "maxWidth": "300px",
                    #"maxHeight": "200px",
                    #"width": "100%",
                    "height": "auto",
                    },
            ),
            dbc.Col([
                dbc.Row([
                    html.H1("Card Name Here", id="card-name-header")
                ]),
                dbc.Row([
                    dbc.Col([
                        ban_card_container(fig="card set here", title="Set", card_body_id="card-set")
                    ]),
                    dbc.Col([
                        ban_card_container(fig="card number here", title="Card Number", card_body_id="card-number")
                    ]),
                    dbc.Col([
                        ban_card_container(fig="card rarity here", title="Rarity", card_body_id="card-rarity")
                    ],),
                ], class_name="g-3 mb-3"),
                dbc.Row([
                    dbc.Col([
                        ban_card_container(fig="card type here", title="Type", card_body_id="card-type")
                    ]),
                    dbc.Col([
                        ban_card_container(fig="card set here", title="HP", card_body_id="card-hp")
                    ]),
                    dbc.Col([
                        ban_card_container(fig="card illustrator here", title="Illustrator", card_body_id="card-illustrator")
                    ]),
                ], class_name="g-3 mb-3"),
                dbc.Row([
                    html.Div([graph_container(fig=" current market price fig here", title="Current Market Price")])
                ])
            ])
        ], class_name="g-3 mb-3 card-row")
    ])
    return html.Div([
        dcc.Location(id="url"),
        html.H2(f"🎴 Card View for: {card_id}", id="card-title"),
        card_gen_content,
        # Additional card details and components would go here
    ])


@callback(
    Output("card-title", "children"),
    Output("card-image", "src"),
    Output("card-name-header", "children"),
    Output("card-set", "children"),
    Output("card-number", "children"),
    Output("card-rarity", "children"),
    Output("card-type", "children"),
    Output("card-hp", "children"),
    Output("card-illustrator", "children"),
    Input("url", "pathname"),
)
def update_card_page(pathname):
    card_number = pathname.split("/")[-1]
    #print(f"card_number: {card_number}")
    card_metadata = get_card_metadata(card_number)

    if card_metadata.empty:
        return (
            "🎴 Card View: Card Not Found",
            "",
            "Card Not Found",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A"
        )
    
    else:
        return (
            f"🎴 Card Details: {card_metadata['name']}",
            card_metadata['imageUrl'],
            card_metadata['name'],
            card_metadata['setName'],
            card_metadata['cardNumber'],
            card_metadata['rarity'],
            card_metadata["cardType"],
            card_metadata['hp'],
            card_metadata['artist']
        )
    