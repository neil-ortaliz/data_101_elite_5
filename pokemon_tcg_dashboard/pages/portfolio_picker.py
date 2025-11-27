import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State, ALL, ctx, no_update, exceptions

import pandas as pd
from datetime import date
import logging
logger = logging.getLogger(__name__)

from global_variables import PRICE_HISTORY_DF, CARD_METADATA_DF, SET_OPTIONS, RARITY_OPTIONS

dash.register_page(
    __name__,
    path="/portfolio_picker",
    title="Portfolio Picker",
    name="Portfolio Picker",
    order=4
)

CARDS_PER_PAGE = 100

# Search bar
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
    options=SET_OPTIONS,
    multi=True,
    placeholder="Filter By Set"
)

rarity_select = dcc.Dropdown(
    id="rarity-select",
    options=RARITY_OPTIONS,
    multi=True,
    placeholder="Filter By Rarity"
)

# Offcanvas
offcanvas = html.Div([
    dbc.Offcanvas(
        html.Div([
            html.Div(
                [
                    html.Div(
                        "Product Image Placeholder",
                        style={
                            'width': '100%',
                            'height': '350px',
                            'backgroundColor': '#f0f0f0',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'marginBottom': '15px'
                        }
                    )
                ],
                id="offcanvas-image"
            ),
            html.Div([
                dbc.Row([
                    dbc.Col(
                        html.H4(
                            "Mega Charizard V ex", 
                            className="mb-0", 
                            id="offcanvas-name"
                        ),
                        width=True
                    ),
                    dbc.Col(
                        html.Span(
                            "★",
                            style={'fontSize': '1.5em', 'color': 'gold'}
                        ),
                        width="auto"
                    )
                ], className="mb-1"),
                html.P(
                    "Mega Hyper Rare • 130/094",
                    className="text-muted small mb-3",
                    id="offcanvas-rarity"
                ),
            ]),
            html.Div([
                html.H3(
                    "$503.37", 
                    className="mb-0", 
                    id="offcanvas-price"
                ),
            ]),
            html.Hr(),
            html.Div([
                dbc.Row(
                    [
                        dbc.Col(
                            html.Small("Total: **$0.00**", id="offcanvas-total", style={'textAlign': 'right'}),
                            width=6
                        ),
                    ],
                    className="mb-3"
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div("Quantity", className="text-primary"), 
                            width=4,
                            align="center"
                        ),
                        dbc.Col(
                            dbc.InputGroup(
                                [
                                    dbc.Button("-", id={"type":"btn-minus","index":"offcanvas"}, n_clicks=0, color="light", style={'padding': '0 8px'}),
                                    dbc.Input(
                                        value=1,
                                        type="number",
                                        min=0,
                                        max=99,
                                        step=1,
                                        style={'textAlign': 'center', 'width': '50px'},
                                        id={"type":"quantity-input","index":"offcanvas"}
                                    ),
                                    dbc.Button("+", id={"type":"btn-plus","index":"offcanvas"}, n_clicks=0, color="light", style={'padding': '0 8px'}),
                                ],
                                size="sm",
                                className="w-auto"
                            ),
                            width=5,
                            align="center"
                        ),
                        dbc.Col(
                            html.Small("$0.00", style={'textAlign': 'right'}, id='quantity-price'),
                            width=3,
                            align="center"
                        ),
                    ],
                    className="align-items-center mb-3",
                ),
                dbc.Row([
                    dcc.DatePickerSingle(
                        month_format='MMMM Y',
                        placeholder='MMMM Y',
                        date=date.today(),
                        id="date-picker"
                    )
                ],
                className="mb-3"),
                dbc.Row(
                    dbc.Button("Add to Portfolio", id="add-to-portfolio")
                )
            ], style={'paddingBottom': '20px'})
        ]),
        id="offcanvas-placement",
        title=html.Div(["Add to Portfolio"], style={'fontWeight': 'bold'}),
        is_open=False,
        placement="end",
        style={'width': '400px'} 
    )
])

# Layout
layout = html.Div([
    dcc.Store(id="page-number", data=0),
    dcc.Store(id="offcanvas-unit-price", data=0),
    dcc.Store(id="offcanvas-tcgplayerid", data=None),
    html.Pre(id="debug-output",
             style={"whiteSpace": "pre-wrap", "background": "#222",
                    "color": "lime", "padding": "10px"}),
    offcanvas,
    dbc.Stack([
        html.Div([
            dbc.Row([
                dbc.Col([search_bar]),
                dbc.Col([clear_button]),
            ], justify="between")
        ], style={"margin-bottom": "15px"}),
        html.Div([
            dbc.Row([
                dbc.Col(set_select),
                dbc.Col(rarity_select)
            ])  
        ], style={"margin-bottom": "15px"}),
        html.Div([
            dbc.ButtonGroup([
                dbc.Button("Prev", id="page-prev", color="light"),
                dbc.Button("Next", id="page-next", color="light"),
            ]),
            html.Span(id="page-label", style={"marginLeft": "10px"})
        ], style={"marginBottom": "10px"}),
        html.Div(
            id="image-grid",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "16px"
            }
        )
    ])
])

# ----------------------
# Callbacks
# ----------------------

@callback(
    Output("set-select", "options"),
    Output("rarity-select", "options"),
    Input("cards-metadata", "data")
)
def update_dropdowns(data):
    if not data:
        return [], []
    df = pd.DataFrame(data)
    set_options = sorted(df["setName"].dropna().unique())
    rarity_options = sorted(df["rarity"].dropna().unique())
    return set_options, rarity_options

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
    image_df = CARD_METADATA_DF
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
    State("cards-metadata", "data")
)
def update_images(selected_sets, selected_types, searched_text,page, cards_metadata):
    page = int(page or 0)
    image_df = pd.DataFrame(cards_metadata)
    filtered = image_df.copy()
    if selected_sets:
        filtered = filtered[filtered["setName"].isin(selected_sets)]
    if selected_types:
        filtered = filtered[filtered["rarity"].isin(selected_types)]
    if searched_text:
        search_mask = filtered.apply(lambda row: row.astype(str).str.contains(searched_text, case=False).any(), axis=1)
        filtered = filtered[search_mask]
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    filtered = filtered.iloc[start:end]
    cards = []
    for _, row in filtered.iterrows():
        cards.append(
            html.Div(
                dbc.Card(
                    [
                        dbc.CardImg(
                            src=row["imageUrl"],
                            top=True,
                            class_name='card-image'
                        ),
                        dbc.CardImgOverlay(
                            dbc.CardBody(
                                dbc.Button("View Details", 
                                color="Link",
                                href=f"/card/{row['tcgPlayerId']}",),
                                class_name="d-flex justify-content-center align-items-center"
                            ),
                            class_name="hover-overlay"
                        ),
                        dbc.CardFooter(
                            [
                                html.P(
                                    row["name"],
                                    className="card-text",
                                    style={"marginBottom": "8px"}
                                ),
                                dbc.Button(
                                    "Add to My Portfolio",
                                    id={"type": "add-portfolio-button", "index": row["tcgPlayerId"]},
                                    n_clicks=0,
                                    class_name="add-portfolio-button",
                                    color="secondary",
                                    size="sm",
                                ),
                            ],
                            style={"textAlign": "center", "z-index":"10"}
                        ),
                    ],
                    class_name="card-normal",
                    style={
                        "borderRadius": "0px",
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                    },
                ),
                style={
                    "width": "100%",
                    "padding": "0",
                    "border": "none",
                }
            )
        )
    return cards

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

@callback(
    Output("offcanvas-placement", "is_open"),
    Output("offcanvas-name", "children"),
    Output("offcanvas-rarity", "children"),
    Output("offcanvas-price", "children"),
    Output("offcanvas-image", "children"),
    Output({"type":"quantity-input","index":"offcanvas"}, "value"),
    Output("quantity-price", "children"),
    Output("offcanvas-unit-price", "data"),
    Output("offcanvas-tcgplayerid", "data"),
    Output("selected-cards","data"),

    Input({"type": "add-portfolio-button", "index": ALL}, "n_clicks"),
    Input({"type":"btn-plus","index":"offcanvas"}, "n_clicks"),
    Input({"type":"btn-minus","index":"offcanvas"}, "n_clicks"),
    Input("date-picker", "date"),
    Input("clear-portfolio", "n_clicks"),
    Input("add-to-portfolio", "n_clicks"),   # <-- add-to-portfolio button
    State("offcanvas-placement", "is_open"),
    State({"type":"quantity-input","index":"offcanvas"}, "value"),
    State("cards-metadata", "data"),
    State("offcanvas-unit-price", "data"),
    State("offcanvas-tcgplayerid", "data"),
    State("selected-cards", "data"),
    prevent_initial_call=True
)
def handle_offcanvas(
    add_buttons_clicks, plus_clicks, minus_clicks,
    selected_date, clear_click, add_to_portfolio_click,  # <-- parameter for add-to-portfolio
    is_open, qty, card_data, stored_unit_price, stored_id, selected_cards
):
    trigger = ctx.triggered_id
    trigger_value = ctx.triggered[0]["value"] if ctx.triggered else None
    if isinstance(trigger, dict) and trigger.get("type") in ["btn-plus", "btn-minus", "add-portfolio-button"] and trigger_value == 0:
        raise exceptions.PreventUpdate

    qty = qty or 0
    selected_cards = selected_cards or []

    # ----------------------------------------------------
    # 1) CLEAR PORTFOLIO
    # ----------------------------------------------------
    if trigger == "clear-portfolio":
        return (
            is_open, no_update, no_update, no_update, no_update,
            0, "$0.00",
            stored_unit_price,
            stored_id,
            []  # clears selected-cards
        )

    # Convert card metadata to DataFrame
    df = pd.DataFrame(card_data).set_index("tcgPlayerId")

    # ----------------------------------------------------
    # 2) ADD-PORTFOLIO BUTTON → OPEN OFFCANVAS
    # ----------------------------------------------------
    if isinstance(trigger, dict) and trigger.get("type") == "add-portfolio-button":
        card_id = trigger["index"]
        row = df.loc[card_id]

        unit_price = float(row["prices.market"])
        img = html.Div(
            html.Img(
                src=row["imageUrl"],
                style={"width": "100%", "height": "350px", "objectFit": "contain"}
            )
        )

        return (
            not is_open,                       # open offcanvas
            row["name"],                       # name
            row["rarity"],                     # rarity
            f"${unit_price:,.2f}",             # price text
            img,                               # image
            0,                                 # reset qty
            "$0.00",                           # reset total
            unit_price,                        # store price
            card_id,                           # store tcgplayer id
            selected_cards
        )

    # ----------------------------------------------------
    # 3) ADD-TO-PORTFOLIO BUTTON → APPEND SELECTED CARD
    # ----------------------------------------------------
    if trigger == "add-to-portfolio":
        if stored_id is not None:
            # Check if card already exists in selected_cards
            existing_index = next((i for i, c in enumerate(selected_cards) if c["tcgPlayerId"] == stored_id), None)
            card_entry = {
                "tcgPlayerId": int(stored_id),
                "quantity": qty,
                "buy_price": stored_unit_price,
                "buy_date": selected_date
            }

            if existing_index is not None:
                # Replace the old entry
                selected_cards[existing_index] = card_entry
            else:
                # Append new entry
                selected_cards.append(card_entry)

        total_price = qty * stored_unit_price
        return (
            False, no_update, no_update, no_update, no_update,
            qty,
            f"${total_price:,.2f}",
            stored_unit_price,
            stored_id,
            selected_cards
        )

    # ----------------------------------------------------
    # 4) DATE PICKER → UPDATE PRICE
    # ----------------------------------------------------
    if trigger == "date-picker":
        card_id = stored_id
        unit_price = stored_unit_price

        try:
            mask = PRICE_HISTORY_DF["tcgPlayerId"] == card_id
            day_prices = PRICE_HISTORY_DF[mask].set_index("date")

            if selected_date in day_prices.index:
                unit_price = float(day_prices.loc[selected_date]["market"])
        except:
            pass

        total_price = qty * unit_price
        return (
            True, no_update, no_update,
            f"${unit_price:,.2f}",
            no_update,
            qty,
            f"${total_price:,.2f}",
            unit_price,
            stored_id,
            selected_cards
        )

    # ----------------------------------------------------
    # 5) PLUS / MINUS BUTTONS
    # ----------------------------------------------------
    if isinstance(trigger, dict) and trigger.get("type") in ["btn-plus", "btn-minus"]:
        unit_price = stored_unit_price

        if trigger["type"] == "btn-plus":
            qty += 1
        elif trigger["type"] == "btn-minus" and qty > 0:
            qty -= 1

        total_price = qty * unit_price

        return (
            True, no_update, no_update, no_update, no_update,
            qty,
            f"${total_price:,.2f}",
            unit_price,
            stored_id,
            selected_cards
        )
