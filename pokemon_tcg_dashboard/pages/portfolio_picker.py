import dash
from dash import html, dcc, Input, Output, callback

import dash_bootstrap_components as dbc
from utils import get_image_urls

dash.register_page(__name__, path="/portfolio_picker",
                    title="Portfolio Picker", 
                    name="Portfolio Picker",
                    order=4)

image_df = get_image_urls()



set_select = dcc.Dropdown(
    id="set-select",
    options=[ 
        set_name for set_name in sorted(image_df['setName'].unique())
    ],
    multi=True,
)

rarity_select = dcc.Dropdown(
    id="rarity-select",
    options=[ 
        rarity for rarity in sorted(image_df['rarity'].unique())
    ],
    multi=True,
)

layout = dbc.Stack([
    html.Div([
            set_select,
            html.Br(),
            rarity_select,
            html.Br(),   
    ]),
    html.Div(
    [   
        html.Img(src=url, style={"width": "100%", "borderRadius": "8px"})
        for url in list(image_df['imageUrl'])
    ],
    style={
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
        "gap": "16px"
    },
    id="image-grid",)
])

@callback(
    Output("image-grid", "children"),
    Input("set-select", "value"),
    Input("rarity-select", "value")
)
def update_images(selected_sets, selected_types):
    filtered = image_df.copy()

    if selected_sets:
        filtered = filtered[filtered["setName"].isin(selected_sets)]
    if selected_types:
        filtered = filtered[filtered["rarity"].isin(selected_types)]

    return [
        html.Img(src=url, style={"width": "100%", "borderRadius": "8px"})
        for url in filtered["imageUrl"]
    ]