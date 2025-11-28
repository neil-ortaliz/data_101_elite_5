import dash
from dash import Dash, html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import logging
import time

from utils import load_data, get_price_history

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s — %(levelname)s — %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

# Dash app
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
    ],
    title="Pokémon TCG Analytics: Gotta Price Em All"
)

# Timestamp changes every time app.py restarts
SERVER_START = time.time()

# Navbar
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Market View", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Portfolio", href="/portfolio", active="exact")),
        dbc.NavItem(dbc.NavLink("Catalogue", href="/catalogue", active="exact"), class_name="ms-auto"),
    ],
    pills=True,
    navbar=True
)

# Layout
app.layout = html.Div([
    dcc.Location(id='main-url', refresh=True),
    dcc.Store(id="selected-cards", storage_type="session"),
    dcc.Store(id="cards-metadata", data=load_data("cards_metadata_table.csv").to_dict("records")),
    #dcc.Store(id='price-history', data=get_price_history().to_dict("records")),


    html.Header([
        html.H1("Pokémon TCG Dashboard", style={"color": "white", "padding": "10px"}),
        nav
    ]),

    dash.page_container,

    html.Footer([], style={"backgroundColor": "#f0f0f0", "padding": "10px", "textAlign": "center"})
])



if __name__ == "__main__":
    app.run(debug=True)
