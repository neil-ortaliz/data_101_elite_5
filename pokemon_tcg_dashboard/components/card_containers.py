import dash_bootstrap_components as dbc

from dash import html, dcc


def tab_card_container(content=None, class_name=""):
    return dbc.Card(
        dbc.CardBody(
            [content]
        ),
        class_name=class_name
    )

def ban_card_container(fig=None, title="", header_id="", card_id="card", card_body_id=""):
    return dbc.Card(
        [
            dbc.CardHeader(children=title, id=header_id),
            dbc.CardBody(
                [
                    html.Div(fig)
                ], id=card_body_id
            )
        ],
        id=card_id
    )

def graph_container(fig=None, title="Visualization Here", class_name=None, fig_id="graph-container-fig", container_id="graph-container"):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(title, className="card-title"),
                    html.Div(dcc.Graph(id=fig_id, figure=fig))
                    
                ],
                id=container_id,
            )
        ],
        
        class_name=class_name
    )