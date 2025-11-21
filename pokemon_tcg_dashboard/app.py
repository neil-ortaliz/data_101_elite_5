import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from pages.template import base_layout

app = Dash(__name__, use_pages=True, 
           external_stylesheets=[
               dbc.themes.BOOTSTRAP,
                "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
                ],     
           title="Pokémon TCG Dashboard")

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Market View",href="/",active="exact")),
        dbc.NavItem(dbc.NavLink("Portfolio", href="/portfolio", active="exact")),
        dbc.NavItem(dbc.NavLink("Portfolio Picker", href="/portfolio_picker", active="exact"), class_name="ms-auto"),
    ],
    pills=True,
    navbar=True
)

app.layout = html.Div([
        dcc.Store(id="selected-cards", storage_type="session"),
        html.Header([
            html.H1("Pokémon TCG Dashboard", style={"color": "white", "padding": "10px"}),
            nav
        ]),
        dash.page_container,

        html.Footer([
        ], style={"backgroundColor": "#f0f0f0", "padding": "10px", "textAlign": "center"})
    ])


if __name__ == '__main__':
    app.run(debug=True)