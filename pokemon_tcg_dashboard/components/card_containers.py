import dash_bootstrap_components as dbc

from dash import html

def ban_card_container(fig=None, title=""):
    return dbc.Card(
        [
            dbc.CardHeader(title),
            dbc.CardBody(
                [
                    html.Div(fig)
                ]
            )
        ]
    )

def graph_container(fig=None, title="Visualization Here", class_name=None):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(title, className="card-title"),
                    html.Div(fig)
                ]
            )
        ],
        class_name=class_name
    )