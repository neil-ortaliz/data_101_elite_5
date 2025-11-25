import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import timedelta
from components.card_ui import create_card_header, create_action_buttons
from components.charts import card_view_price_history_line_chart
from components import graph_container
from global_variables import CARD_DATA_FETCHER, PRICE_HISTORY_DF, EBAY_METADATA_DF

# ---------------- Register page ----------------
dash.register_page(
    __name__,
    path_template="/card/<card_id>",
)

# ---------------- Layout ----------------
def layout(card_id=None, **kwargs):
    card_gen_content = html.Div([
        html.Div(id="card-header-container"),
        html.Hr()
    ])

    # Filter controls for TCGPlayer chart
    tcg_filter_controls = dbc.Row([
        dbc.Col([dcc.Dropdown(
            id="tcg-date-dropdown",
            options=[
                {"label": "All Time", "value": "all"},
                {"label": "Last 90 Days", "value": "90"},
                {"label": "Last 30 Days", "value": "30"},
                {"label": "Last 15 Days", "value": "15"},
                {"label": "Last 7 Days", "value": "7"},
            ],
            value="all",
            clearable=False
        )], width=4),
        dbc.Col([dcc.Dropdown(
            id="tcg-grade-dropdown",
            options=[
                {"label": "All Grades", "value": "all"},
                {"label": "Near Mint", "value": "Near Mint"},
                {"label": "Lightly Played", "value": "Lightly Played"},
                {"label": "Moderately Played", "value": "Moderately Played"},
                {"label": "Heavily Played", "value": "Heavily Played"},
                {"label": "Damaged", "value": "Damaged"}
            ],
            value="all",
            clearable=False
        )], width=4)
    ])

    # Filter controls for eBay chart
    ebay_filter_controls = dbc.Row([
        dbc.Col([dcc.Dropdown(
            id="ebay-date-dropdown",
            options=[
                {"label": "All Time", "value": "all"},
                {"label": "Last 90 Days", "value": "90"},
                {"label": "Last 30 Days", "value": "30"},
                {"label": "Last 15 Days", "value": "15"},
                {"label": "Last 7 Days", "value": "7"},
            ],
            value="all",
            clearable=False
        )], width=4),
        dbc.Col([dcc.Dropdown(
            id="ebay-grade-dropdown",
            options=[
                {"label": "All Grades", "value": "all"},
                {"label": "PSA 8", "value": "psa8"},
                {"label": "PSA 9", "value": "psa9"},
                {"label": "PSA 10", "value": "psa10"}
            ],
            value="all",
            clearable=False
        )], width=4)
    ])

    return html.Div([
        dcc.Location(id="url"),
        card_gen_content,
        html.H5("Price History Filters"),
        tcg_filter_controls,
        html.Div(id="tcg-chart-container"),
        html.Hr(),
        html.H5("eBay Price History Filters"),
        ebay_filter_controls,
        html.Div(id="ebay-chart-container")
    ])


# ---------------- Populate card header ----------------
@callback(
    Output("card-header-container", "children"),
    Input("url", "pathname")
)
def update_card_header(pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.H3("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, psa="psa10")
    if card_metadata is None:
        return html.H3("Card Not Found")

    card_data = {
        "name": card_metadata['name'],
        "set": card_metadata['set'],
        "rarity": card_metadata['rarity'],
        "card_number": card_id,
        "image_url": card_metadata['image_url'],
        "current_price": card_metadata['current_price'],
        "psa10_price": card_metadata['psa_price'],
        "ungraded_price": card_metadata['ungraded_price'],
        "total_listings": card_metadata['total_listings'],
    }

    return html.Div([
        create_card_header(card_data),
        create_action_buttons()
    ])

# ---------------- Update TCGPlayer chart ----------------
@callback(
    Output("tcg-chart-container", "children"),
    Input("tcg-date-dropdown", "value"),
    Input("tcg-grade-dropdown", "value"),
    Input("url", "pathname")
)
def update_tcg_chart(selected_date, selected_grade, pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, psa="psa10")
    if card_metadata is None:
        return html.Div("Card Not Found")

    fig = card_view_price_history_line_chart(
        card_name=card_metadata["name"],
        card_id=card_id,
        card_df=PRICE_HISTORY_DF,
        price_column="market",
        platform_name="TCGPlayer",
        grade_filter="condition",
        selected_date=selected_date,
        selected_grade=selected_grade
    )
    return graph_container(fig=fig, title="Price History")


# ---------------- Update eBay chart ----------------
@callback(
    Output("ebay-chart-container", "children"),
    Input("ebay-date-dropdown", "value"),
    Input("ebay-grade-dropdown", "value"),
    Input("url", "pathname")
)
def update_ebay_chart(selected_date, selected_grade, pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, psa="psa10")
    if card_metadata is None:
        return html.Div("Card Not Found")

    fig = card_view_price_history_line_chart(
        card_name=card_metadata["name"],
        card_id=card_id,
        card_df=EBAY_METADATA_DF,
        price_column="average",
        platform_name="eBay",
        grade_filter="grade",
        selected_date=selected_date,
        selected_grade=selected_grade
    )
    return graph_container(fig=fig, title="eBay Price History")