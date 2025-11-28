import dash
from dash import html

import dash_bootstrap_components as dbc

dash.register_page(__name__)


layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H1(
                        "Sorry, page doesn't exist!",
                        className="display-4 text-center mb-4"
                    ),
                    html.Img(
                        src="/assets/error_404.jpg",
                        style={"width": "100%", "maxWidth": "400px", "display": "block", "margin": "0 auto"}
                    )
                ]),
                className="shadow p-4 w-100",
                style={"borderRadius": "20px"}
            ),
            #width=12, lg=6, className="mx-auto"
        ),
        className="justify-content-center mt-5"
    ),
    fluid=True,
    className="d-flex align-items-center justify-content-center",
    style={"height": "100vh"}
)