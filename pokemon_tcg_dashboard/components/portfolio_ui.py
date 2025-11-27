import dash_bootstrap_components as dbc
from dash import html, dash_table
from components.market_ui import create_metric_card  # Reuse!

from utils.portfolio_calcs import PortfolioCalculator
from global_variables import PRICE_HISTORY_DF, CARD_METADATA_DF

import logging
logger = logging.getLogger(__name__)

def create_portfolio_summary_metrics(selected_cards=None,days=1):
    """
    Create the 4 metric cards for Portfolio View
    
    Returns:
        dbc.Row with 4 portfolio metric cards
    """
    logging.debug("create_portfolio_summary_metrics called!")
    if selected_cards is None:
        logging.debug(f"selected_cards is None")
    else:
        logging.debug(f"passing selected_cards len with lenght of {len(selected_cards)}")
        logging.debug(f"selected_cards: {selected_cards}")

    type_map = {
        "gain": "positive",
        "loss": "negative",
        "neutral": "neutral"
    }
    
    portfolio_calculator = PortfolioCalculator(selected_cards, PRICE_HISTORY_DF, CARD_METADATA_DF)
    totals = portfolio_calculator.calculate_total_portfolio_value(days)
    gain_loss = portfolio_calculator.calculate_total_gain_loss(days)
    portfolio_change_type = "positive" if totals['value_change'] > 0 else "negative" if totals['value_change'] < 0 else "neutral"
    gain_loss_change_type = type_map.get(gain_loss['type'], "neutral")

    card_nums = portfolio_calculator.calculate_card_count(days)
    average = portfolio_calculator.calculate_average_card_value(days)
    average_change_type = "positive" if average['change'] > 0 else "negative" if average['change'] < 0 else "neutral"


    metrics_row = dbc.Row([
        dbc.Col(
            create_metric_card(
                title="Total Portfolio Value",
                value= totals['formatted'],
                change=f"{totals['value_change_formatted']} ({totals['percent_change_formatted']})",
                change_type=portfolio_change_type
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Total Gain/Loss",
                value=gain_loss['formatted_value'],
                change=gain_loss['formatted_pct'],
                change_type=gain_loss_change_type
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Number of Cards",
                value=card_nums['formatted'],
                change=f"{card_nums['unique_cards']} unique cards",
                change_type="neutral"
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Average Card Value",
                value=average['formatted'],
                change=average['change_formatted'],
                change_type=average_change_type
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
    ], className="mb-4")
    
    return metrics_row

def create_risk_badge(title, level, description):
    """
    Create a risk indicator badge
    
    Args:
        title: Badge title (e.g., "Diversity Score")
        level: "low", "medium", "high"
        description: Tooltip text explaining the metric
    
    Returns:
        dbc.Card with risk badge
    """
    # Color mapping
    color_map = {
        "low": "success",
        "medium": "warning",
        "high": "danger"
    }
    color = color_map.get(level.lower(), "secondary")
    
    # Create unique ID for tooltip
    tooltip_id = title.lower().replace(" ", "-") + "-info"
    
    badge_card = dbc.Card([
        dbc.CardBody([
            html.H6([
                title,
                html.Span(
                    " ⓘ",
                    id=tooltip_id,
                    style={"cursor": "pointer", "color": "#666", "marginLeft": "5px"}
                )
            ], className="mb-2"),
            dbc.Badge(
                level.upper(),
                color=color,
                className="me-2",
                pill=True
            ),
            dbc.Tooltip(
                description,
                target=tooltip_id,
                placement="top"
            )
        ])
    ], className="risk-badge-card mb-3")
    
    return badge_card

def create_risk_indicators(selected_cards=None):
    """
    Create risk indicator section for Portfolio View
    
    Returns:
        dbc.Row with 3 risk badges
    """

    portfolio_calculator = PortfolioCalculator(selected_cards, PRICE_HISTORY_DF, CARD_METADATA_DF)
    diversity = portfolio_calculator.calculate_diversity_score()
    volatility = portfolio_calculator.calculate_volatility_rating()
    market_exp = portfolio_calculator.calculate_market_exposure()
    
    risk_row = dbc.Row([
        dbc.Col([
            html.H5("Portfolio Risk Analysis", className="mb-3"),
        ], width=12),
        dbc.Stack([
            html.Div(
                create_risk_badge(
                    title="Diversity Score",
                    level= diversity["level"],
                    description= diversity["description"]
                )
            ),
            html.Div(
                create_risk_badge(
                    title="Volatility Rating",
                    level= volatility["level"],
                    description= volatility["description"]
                ),
            ),
            html.Div(
                create_risk_badge(
                title="Market Exposure",
                level= market_exp["level"],
                description= market_exp["description"]
                )
            )
        ],
        class_name="w-100")
    ], className="mb-4")
    
    return risk_row

def create_holdings_table(data=None):
    """
    Create portfolio holdings table
    
    Args:
        data: List of dicts with portfolio card data
    
    Returns:
        html.Div with add button and table
    """
    # TODO: Data from Member 2
    if data is None:
        data = [
            {
                "name": "Charizard ex",
                "set_name": "Obsidian Flames",
                "quantity": 2,
                "buy_price": "$38.00",
                "current_price": "$45.99",
                "price_change": "+$15.98",
                "pct_change": "+21.0%"
            },
            {
                "name": "Pikachu VMAX",
                "set_name": "Vivid Voltage",
                "quantity": 1,
                "buy_price": "$28.00",
                "current_price": "$32.50",
                "price_change": "+$4.50",
                "pct_change": "+16.1%"
            },
            {
                "name": "Mewtwo V",
                "set_name": "Pokemon GO",
                "quantity": 3,
                "buy_price": "$22.00",
                "current_price": "$18.75",
                "price_change": "-$9.75",
                "pct_change": "-14.8%"
            },
            {
                "name": "Umbreon VMAX",
                "set_name": "Evolving Skies",
                "quantity": 1,
                "buy_price": "$75.00",
                "current_price": "$89.99",
                "price_change": "+$14.99",
                "pct_change": "+20.0%"
            },
        ]
    
    table = dash_table.DataTable(
        id='holdings-table',
        columns=[
            {"name": "Card Name", "id": "name"},
            {"name": "Set", "id": "set_name"},
            {"name": "Qty", "id": "quantity"},
            {"name": "Buy Price", "id": "buy_price"},
            {"name": "Current Price", "id": "current_price"},
            {"name": "Price Change", "id": "price_change"},
            {"name": "% Change", "id": "pct_change"},
        ],
        data=data,
        sort_action="native",
        page_size=25,
        style_table={
            'overflowX': 'auto'
        },
        style_header={
            'backgroundColor': '#0075BE',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'padding': '10px'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '14px'
        },
        style_data_conditional=[
            # Gains in blue
            {
                'if': {
                    'filter_query': '{price_change} contains "+"',
                    'column_id': ['price_change', 'pct_change']
                },
                'color': '#1E90FF',
                'fontWeight': 'bold'
            },
            # Losses in orange
            {
                'if': {
                    'filter_query': '{price_change} contains "-"',
                    'column_id': ['price_change', 'pct_change']
                },
                'color': '#FF8C00',
                'fontWeight': 'bold'
            },
            # Row hover
            {
                'if': {'state': 'active'},
                'backgroundColor': 'rgba(0, 117, 190, 0.1)',
                'border': '1px solid #0075BE'
            }
        ]
    )
    
    # Add "Add Card" button
    '''add_button = dbc.Button(
        [html.Span("➕ ", style={"marginRight": "8px"}), "Add Card to Portfolio"],
        id="add-card-btn",
        color="success",
        className="mb-3"
    )'''
    
    return html.Div([
        #add_button,
        table
    ])