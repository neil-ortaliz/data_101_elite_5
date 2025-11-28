import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import timedelta
from components.card_ui import create_card_header
from components.charts import card_view_price_history_line_chart, card_view_card_grade_price_comparison
from components import graph_container, tab_card_container
from global_variables import CARD_DATA_FETCHER, PRICE_HISTORY_DF, EBAY_METADATA_DF
from utils.grade_analysis import create_grade_distribution_chart
from utils import calculate_cat_vol_price, calculate_roi

import logging
logger = logging.getLogger(__name__)


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

    date_filter_controls = dbc.Row([
        dbc.Col([dcc.Dropdown(
            id="date-dropdown",
            options=[
                {"label": "All Time", "value": "all"},
                {"label": "Last 90 Days", "value": "90"},
                {"label": "Last 30 Days", "value": "30"},
                {"label": "Last 15 Days", "value": "15"},
                {"label": "Last 7 Days", "value": "7"},
            ],
            value="all",
            clearable=False
        )], width=12)
    ])
    # Filter controls for TCGPlayer chart
    tcg_filter_controls = dbc.Row([
        dbc.Col([dcc.Dropdown(
            id="tcg-grade-dropdown",
            options=[
                {"label": "All Conditions", "value": "all"},
                {"label": "Near Mint", "value": "Near Mint"},
                {"label": "Lightly Played", "value": "Lightly Played"},
                {"label": "Moderately Played", "value": "Moderately Played"},
                {"label": "Heavily Played", "value": "Heavily Played"},
                {"label": "Damaged", "value": "Damaged"}
            ],
            value="all",
            clearable=False
        )], width=12)
    ])

    # Filter controls for eBay chart
    ebay_filter_controls = dbc.Row([
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
        )], width=12)
    ])

    return html.Div([
        dcc.Location(id="url"),

        # --- CARD HEADER SECTION ---
        card_gen_content,
        date_filter_controls,
        html.Hr(),

        # --- SIDE-BY-SIDE TCG + EBAY CHARTS ---
        html.Div([
            # LEFT COLUMN — TCGplayer charts
            html.Div([
                tcg_filter_controls,
                html.Div(id="tcg-chart-container"),
            ], style={
                "flex": "1",
                "padding": "10px",
                "minWidth": "350px"
            }),

            # RIGHT COLUMN — eBay charts
            html.Div([
                ebay_filter_controls,
                html.Div(id="ebay-chart-container"),
            ], style={
                "flex": "1",
                "padding": "10px",
                "minWidth": "350px"
            })
        ], style={
            "display": "flex",
            "gap": "20px",
            "alignItems": "flex-start",
            "flexWrap": "wrap",      # responsive stacking
            "marginBottom": "30px"
        }),

        html.Hr(),

        # --- GRADE PRICE TREND ---
        html.Div(id='grade-chart-container', style={"marginTop": "20px"}),

        html.Hr(),

        # --- GRADE COMPARISON ---
        dbc.Row([
            dbc.Col(id='grade-comparison-container', width=8),
            dbc.Col([tab_card_container()],id="roi", width=4)
        ])
        #html.Div(id='grade-comparison-container', style={"marginTop": "20px"})
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

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, days = None, condition = 'any')
    if card_metadata is None:
        return html.H3("Card Not Found")

    card_data = {
        "name": card_metadata['name'],
        "set": card_metadata['set'],
        "rarity": card_metadata['rarity'],
        "card_number": card_id,
        "image_url": card_metadata['image_url'],
        "current_price": card_metadata['current_price'],
        "psa10_price": card_metadata['psa10_price'],
        "psa9_price": card_metadata['psa9_price'],
        "psa8_price": card_metadata['psa8_price'],
        "ungraded_price": card_metadata['ungraded_price'],
        "total_listings": card_metadata['total_listings'],
        "card_trend": card_metadata['card_trend']
    }

    return html.Div([
        create_card_header(card_data)
    ])

# ---------------- Update TCGPlayer chart ----------------
@callback(
    Output("tcg-chart-container", "children"),
    Input("date-dropdown", "value"),
    Input("tcg-grade-dropdown", "value"),
    Input("url", "pathname")
)
def update_tcg_chart(selected_date, selected_grade, pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, days = None, condition = 'any')
    if card_metadata is None:
        return html.Div("Card Not Found")

    fig = card_view_price_history_line_chart(
        card_name=card_metadata["name"],
        card_id=card_id,
        card_df=PRICE_HISTORY_DF,
        price_column="market",
        platform_name="Ungraded",
        grade_filter="condition",
        selected_date=selected_date,
        selected_grade=selected_grade
    )
    return graph_container(fig=fig, title="Ungraded Price History")


# ---------------- Update eBay chart ----------------
@callback(
    Output("ebay-chart-container", "children"),
    Input("date-dropdown", "value"),
    Input("ebay-grade-dropdown", "value"),
    Input("url", "pathname")
)
def update_ebay_chart(selected_date, selected_grade, pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, days = None, condition = 'any')
    if card_metadata is None:
        return html.Div("Card Not Found")

    fig = card_view_price_history_line_chart(
        card_name=card_metadata["name"],
        card_id=card_id,
        card_df=EBAY_METADATA_DF,
        price_column="average",
        platform_name="Graded",
        grade_filter="grade",
        selected_date=selected_date,
        selected_grade=selected_grade
    )
    return graph_container(fig=fig, title="Graded Price History")

# ---------------- Update Graded Bar Chart ---------------- 
@callback(
    Output("grade-chart-container", "children"),
    Input("url", "pathname")
)
def update_grade_chart(pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, days=None, condition='any')
    if card_metadata is None:
        return html.Div("Card Not Found")

    #print(card_metadata["name"])

    grade_df = EBAY_METADATA_DF
    
    fig = create_grade_distribution_chart(
        data=grade_df,
        card_id=card_id,
        card_name=card_metadata["name"]
    )
    return graph_container(fig=fig, title = 'Card Grade Distribution')

# ---------------- Grade Price Comparison Chart ---------------- 
@callback(
    Output("grade-comparison-container", "children"),
    Input("url", "pathname")
)
def update_grade_comparison_chart(pathname):
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, days=None, condition='any')
    if card_metadata is None:
        return html.Div("Card Not Found")

    #print(card_metadata["name"])
    
    fig = card_view_card_grade_price_comparison(
        price_history_df = PRICE_HISTORY_DF,
        ebay_history_df = EBAY_METADATA_DF,
        card_id=card_id,
        card_name=card_metadata["name"]
    )
    return graph_container(fig=fig, title = 'Ungraded vs Graded Comparison')

@callback(
    Output("roi", "children"),
    Input("url", "pathname")
)
def update_roi_annotations(pathname):
    logger.debug("update_roi_annotations called")
    card_number = pathname.split("/")[-1]
    try:
        card_id = int(card_number)
    except ValueError:
        return html.Div("Invalid Card ID")

    card_metadata = CARD_DATA_FETCHER.get_card_by_id(card_id=card_id, days=None, condition='any')
    if card_metadata is None:
        return html.Div("Card Not Found")

    #print(card_metadata["name"])
    
    results = calculate_roi(
        price_history_df = PRICE_HISTORY_DF,
        ebay_history_df = EBAY_METADATA_DF,
        card_id=card_id,
        #card_name=card_metadata["name"],
    )
    logger.debug("==============================================================")
    logger.debug(f"ROI Results: {results}")

    cards = []

    if results is None:
        results = [None for i in range(3)]

    for res in results:
        logger.debug(f"Results: {res}")
        if res is not None:
            content_text = res['content']

        if res is None:
            # Fallback card (no ROI data)
            card_body = dbc.CardBody(
                [
                    html.H4(f"PSA {res['grade']} Return on Investment:", className="mb-3"),
                    html.P("No graded sales exist in the market.", className="text-secondary")
                ],
                className="h-100 d-flex flex-column justify-content-start"
            )

        elif "No graded sales exist" in content_text:
            card_body = dbc.CardBody(
                [
                    html.H4(f"PSA {res['grade']} Return on Investment:", className="mb-3"),
                    html.P("No graded sales exist in the market.", className="text-secondary")
                ],
                className="h-100 d-flex flex-column justify-content-start"
            )
        else:
            # Extract ROI % and dollar value
            roi_pct = content_text.split("(")[1].split(")")[0]
            roi_dollar = content_text.split("ROI: ")[1].split(" (")[0]
            verdict_text = content_text.split("\n")[1]

            card_body = dbc.CardBody(
                [
                    html.H4(f"PSA {res['grade']} Return on Investment:", className="mb-3"),

                    html.H2(
                        roi_pct,
                        className=f"text-{res['color']} mb-2",
                        style={"fontWeight": "bold"}
                    ),

                    html.P(
                        roi_dollar,
                        style={"fontSize": "1.2rem"},
                        className="mb-3"
                    ),

                    dbc.Badge(
                        verdict_text,
                        color=res['color'],
                        className="p-2",
                        style={"fontSize": "1.1rem"}
                    ),
                ],
                className="h-100 d-flex flex-column justify-content-start"
            )

        cards.append(
            dbc.Card(
                card_body,
                className="w-100",
                style={"margin-bottom": "10px"}
            )
        )

    return dbc.Stack(cards)
