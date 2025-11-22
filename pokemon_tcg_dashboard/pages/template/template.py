from dash import html

def base_layout(content, title="Pokémon TCG Dashboard"):
    return html.Div([
        html.Header([
            html.H1(title, style={"color": "white", "padding": "10px"}),
        ]),

        html.Main(content, style={"padding": "20px"}),

        html.Footer([
        ], style={"backgroundColor": "#f0f0f0", "padding": "10px", "textAlign": "center"})
    ])
