import dash
from dash import html

import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/portfolio",
                    title="Portfolio", 
                    name="Portfolio",
                    order=2)

layout = html.Div([
    html.H1('This is our Portfolio page'),
    html.Div('This is our Portfolio page content.'),
])