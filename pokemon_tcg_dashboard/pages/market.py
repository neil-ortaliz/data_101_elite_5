# layout.py
from dash import html
from template import base_layout

content = html.Div([
    html.H3("Dashboard"),
    html.P("This is my dashboard page.")
])

layout = base_layout(content, title="Sales Dashboard")
