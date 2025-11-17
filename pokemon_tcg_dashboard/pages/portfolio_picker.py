import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc
from utils import get_image_urls

dash.register_page(
    __name__,
    path="/portfolio_picker",
    title="Portfolio Picker",
    name="Portfolio Picker",
    order=4
)

# Load your dataframe with card images
image_df = get_image_urls()

# Dropdowns
set_select = dcc.Dropdown(
    id="set-select",
    options=sorted(image_df["setName"].unique()),
    multi=True,
)

rarity_select = dcc.Dropdown(
    id="rarity-select",
    options=sorted(image_df["rarity"].unique()),
    multi=True,
)

# Layout
layout = html.Div([
    # Stores selected card IDs across pages
    dcc.Store(id="selected-cards", storage_type="session"),

    # Debug window (you can remove later)
    html.Pre(id="debug-output",
             style={"whiteSpace": "pre-wrap", "background": "#222",
                    "color": "lime", "padding": "10px"}),

    # Filters + Image grid
    dbc.Stack([
        html.Div([
            set_select,
            html.Br(),
            rarity_select,
            html.Br(),
        ]),

        html.Div(
            id="image-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
                "gap": "16px"
            }
        )
    ])
])

# ---------------------------------------------------------------------------
# 1) Create cards ONLY when filters change (fast)
# ---------------------------------------------------------------------------

@callback(
    Output("image-grid", "children"),
    Input("set-select", "value"),
    Input("rarity-select", "value"),
)
def update_images(selected_sets, selected_types):
    filtered = image_df.copy()

    if selected_sets:
        filtered = filtered[filtered["setName"].isin(selected_sets)]
    if selected_types:
        filtered = filtered[filtered["rarity"].isin(selected_types)]

    cards = []
    for _, row in filtered.iterrows():
        cards.append(
            html.Button(
                dbc.Card(
                    dbc.CardImg(src=row["imageUrl"], top=True),
                    className="card-normal",
                    style={"borderRadius": "8px"}
                ),
                id={"type": "card-button", "index": row["tcgPlayerId"]},
                style={"padding": 0, "border": "none", "background": "none"}
            )
        )

    return cards

# ---------------------------------------------------------------------------
# 2) Selection logic — only updates the store, not the grid
# ---------------------------------------------------------------------------

@callback(
    Output("selected-cards", "data", allow_duplicate=True),
    Input({"type": "card-button", "index": ALL}, "n_clicks"),
    State({"type": "card-button", "index": ALL}, "id"),
    State("selected-cards", "data"),
    prevent_initial_call=True
)
def update_selection(n_clicks, ids, selected_ids):
    selected_ids = selected_ids or []

    # Make sure something triggered
    if not ctx.triggered_id:
        return selected_ids

    clicked_id = ctx.triggered_id["index"]

    # Toggle logic
    if clicked_id in selected_ids:
        selected_ids.remove(clicked_id)
    else:
        selected_ids.append(clicked_id)

    return selected_ids


@callback(
    Output({"type": "card-button", "index": ALL}, "className"),
    Input("selected-cards", "data"),
    State({"type": "card-button", "index": ALL}, "id"),
)
def update_classes(selected_ids, ids):
    selected_ids = selected_ids or []
    classes = []

    for component_id in ids:
        if component_id["index"] in selected_ids:
            classes.append("card-selected")
        else:
            classes.append("card-normal")

    return classes


@callback(
    Output("debug-output", "children"),
    Input("selected-cards", "data")
)
def show_debug(selected):
    return f"Selected IDs = {selected}"
