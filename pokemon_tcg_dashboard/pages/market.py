import dash
from dash import html

import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/",
                    title="Market", 
                    name="Market",
                    order=1)

layout = html.Div([
    html.H1('This is our Home page'),
    html.Div('This is our Home page content.'),
])