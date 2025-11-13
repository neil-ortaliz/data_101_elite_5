import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from pages.template import base_layout


content = html.Div([
    html.H1('Multi-page app with Dash Pages'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

app = Dash(__name__, use_pages=True, 
           external_stylesheets=[dbc.themes.BOOTSTRAP], 
           title="Pokémon TCG Dashboard")


app.layout = base_layout(content, title="Pokémon TCG Dashboard")

if __name__ == '__main__':
    app.run(debug=True)