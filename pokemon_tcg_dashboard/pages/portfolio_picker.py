import dash
from dash import html, dcc, Input, Output, callback, State, ALL, ctx, no_update
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

CARDS_PER_PAGE = 100

# search bar
search_bar = dbc.Input(
    id="card_search",
    type="text",
    placeholder="Search for a card..."
)

clear_button = dbc.Button("Clear Selected Cards", 
                          id="clear-portfolio",
                          color="light", 
                          class_name="me-1")

# Dropdowns
set_select = dcc.Dropdown(
    id="set-select",
    options=sorted(image_df["setName"].unique()),
    multi=True,
    placeholder="Filter By Set"
)

rarity_select = dcc.Dropdown(
    id="rarity-select",
    options=sorted(image_df["rarity"].unique()),
    multi=True,
    placeholder="Filter a Rarity"
)

# Layout
layout = html.Div([

    # Store current page number
    dcc.Store(id="page-number", data=0),

    # Debug 
    html.Pre(id="debug-output",
             style={"whiteSpace": "pre-wrap", "background": "#222",
                    "color": "lime", "padding": "10px"}),

    dbc.Stack([
        html.Div([
            dbc.Row([
                dbc.Col([search_bar]),
                dbc.Col([clear_button]),
            ], justify="between")
        ], style={"margin-bottom": "15px"}),
        # Filters
        html.Div([
            dbc.Row([
                dbc.Col(set_select),
                dbc.Col(rarity_select)
            ])  
        ], style={"margin-bottom": "15px"}),

        # Pagination controls
        html.Div([
            dbc.ButtonGroup([
                dbc.Button("Prev", id="page-prev", color="light"),
                dbc.Button("Next", id="page-next", color="light"),
            ]),
            
            html.Span(id="page-label", style={"marginLeft": "10px"})
        ], style={"marginBottom": "10px"}),

        # Image grid
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


@callback(
    Output("page-number", "data"),
    Output("page-label", "children"),
    Output("page-prev", "disabled"),
    Output("page-next", "disabled"),
    Input("page-prev", "n_clicks"),
    Input("page-next", "n_clicks"),
    State("page-number", "data"),
    State("set-select", "value"),
    State("rarity-select", "value"),
    State("card_search","value"),
)
def change_page(prev, next_, current_page, selected_sets, selected_types, searched_text):
    prev = prev or 0
    next_ = next_ or 0
    trigger = ctx.triggered_id
    current_page = int(current_page or 0)

    filtered = image_df.copy()
    if selected_sets:
        filtered = filtered[filtered["setName"].isin(selected_sets)]
    if selected_types:
        filtered = filtered[filtered["rarity"].isin(selected_types)]
    if searched_text:
        mask = filtered.apply(
            lambda row: row.astype(str).str.contains(searched_text, case=False).any(),
            axis=1
        )
        filtered = filtered[mask]

    total_cards = len(filtered)
    total_pages = max(1, (total_cards + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)

    # Only change page if a button was clicked
    if trigger == "page-prev" and current_page > 0:
        current_page -= 1
    elif trigger == "page-next" and current_page < total_pages - 1:
        current_page += 1

    disable_prev = current_page == 0
    disable_next = current_page >= total_pages - 1

    return (
        current_page,
        f"Page {current_page + 1} / {total_pages}",
        disable_prev,
        disable_next
    )



@callback(
    Output("image-grid", "children"),
    Input("set-select", "value"),
    Input("rarity-select", "value"),
    Input("card_search","value"),
    Input("page-number", "data"),
    
)
def update_images(selected_sets, selected_types, searched_text,page):
    page = int(page or 0)

    filtered = image_df.copy()

    if selected_sets:
        filtered = filtered[filtered["setName"].isin(selected_sets)]
    if selected_types:
        filtered = filtered[filtered["rarity"].isin(selected_types)]
    if searched_text:
        search_mask = filtered.apply(lambda row: row.astype(str).str.contains(searched_text, case=False).any(), axis=1)
        filtered = filtered[search_mask]

    # Pagination slice
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    filtered = filtered.iloc[start:end]

    cards = []
    for _, row in filtered.iterrows():
        cards.append(
            html.Button(
                dbc.Card(
                    [
                        dbc.CardImg(src=row["imageUrl"], top=True),
                        dbc.CardFooter([
                            html.P(row["name"], className="card-text"),
                            dbc.Button(
                                "Add to My Portfolio",
                                id={"type": "add-portfolio-button", "index": row["tcgPlayerId"]},
                                n_clicks=0,
                                class_name = 'add-portfolio-button'
                            )

                            ])
                    ],
                    class_name="card-normal",
                    style={
                        "borderRadius": "0px"
                    }
                ),
                id={"type": "card-button", "index": row["tcgPlayerId"]},
                style={"padding": 5, 
                    "border": "none",
                    "background": "none",
                    "maxWidth": "200px",
                    "maxHeight": "250px",
                    "width": "100%",
                    "height": "auto",},
                
            )
        )

    return cards


@callback(
    Output("selected-cards", "data", allow_duplicate=True),
    Input({"type": "add-portfolio-button", "index": ALL}, "n_clicks"),
    Input("clear-portfolio", "n_clicks"),
    State({"type": "add-portfolio-button", "index": ALL}, "id"),
    State("selected-cards", "data"),
    prevent_initial_call=True
)
def update_selection(card_clicks, clear_click, ids, selected_ids):
    selected_ids = selected_ids or []

    triggered = ctx.triggered_id
    if triggered is None:
        return no_update  # no change if no triggered id

    # Clear button clicked
    if triggered == "clear-portfolio":
        if clear_click is None or clear_click == 0:
            return no_update  # ignore initial call
        return []

    # Card button clicked
    if isinstance(triggered, dict) and "index" in triggered:
        if not card_clicks or all(c is None or c == 0 for c in card_clicks):
            return no_update  # no real click yet
        clicked_id = triggered["index"]
        if clicked_id in selected_ids:
            selected_ids.remove(clicked_id)
        else:
            selected_ids.append(clicked_id)
        return selected_ids

    return no_update


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