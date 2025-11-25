import dash_bootstrap_components as dbc
from dash import html, dash_table
from components.market_ui import create_metric_card  # Reuse!

from utils.portfolio_calcs import PortfolioCalculator
from global_variables import PRICE_HISTORY_DF, CARD_METADATA_DF

import logging
logger = logging.getLogger(__name__)

def create_portfolio_summary_metrics(selected_cards=None, ,days=1):
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

    portfolio_calculator = PortfolioCalculator(selected_cards, PRICE_HISTORY_DF, CARD_METADATA_DF)
    total_portfolio_value = portfolio_calculator.calculate_total_portfolio_value()
    logger.debug(f"total_portfolio_value {total_portfolio_value}")
    card_nums = portfolio_calculator.calculate_card_count()

    metrics_row = dbc.Row([
        dbc.Col(
            create_metric_card(
                title="Total Portfolio Value",
                value= total_portfolio_value['formatted'],
                change="+$1,250 (+11.2%)",
                change_type="positive"
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Total Gain/Loss",
                value="+$1,250",
                change="+11.2%",
                change_type="positive"
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
                value="$79.81",
                change="+$5.20",
                change_type="positive"
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

def create_risk_indicators():
    """
    Create risk indicator section for Portfolio View
    
    Returns:
        dbc.Row with 3 risk badges
    """
    # TODO: Risk levels will come from Member 2's risk calculations
    
    risk_row = dbc.Row([
        dbc.Col([
            html.H5("Portfolio Risk Analysis", className="mb-3"),
        ], width=12),
        dbc.Col(
            create_risk_badge(
                title="Diversity Score",
                level="high",
                description="Your portfolio is well-diversified across multiple sets and rarities."
            ),
            width=12, md=4
        ),
        dbc.Col(
            create_risk_badge(
                title="Volatility Rating",
                level="medium",
                description="Moderate price fluctuations expected based on card types."
            ),
            width=12, md=4
        ),
        dbc.Col(
            create_risk_badge(
                title="Market Exposure",
                level="low",
                description="Low concentration in any single card or set."
            ),
            width=12, md=4
        ),
        dbc.Col([
            dbc.Button(
                "Learn More About Risk",
                color="link",
                size="sm",
                className="mt-2"
            )
        ], width=12)
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
                "set": "Obsidian Flames",
                "quantity": 2,
                "buy_price": "$38.00",
                "current_price": "$45.99",
                "gain_loss": "+$15.98",
                "gain_loss_pct": "+21.0%"
            },
            {
                "name": "Pikachu VMAX",
                "set": "Vivid Voltage",
                "quantity": 1,
                "buy_price": "$28.00",
                "current_price": "$32.50",
                "gain_loss": "+$4.50",
                "gain_loss_pct": "+16.1%"
            },
            {
                "name": "Mewtwo V",
                "set": "Pokemon GO",
                "quantity": 3,
                "buy_price": "$22.00",
                "current_price": "$18.75",
                "gain_loss": "-$9.75",
                "gain_loss_pct": "-14.8%"
            },
            {
                "name": "Umbreon VMAX",
                "set": "Evolving Skies",
                "quantity": 1,
                "buy_price": "$75.00",
                "current_price": "$89.99",
                "gain_loss": "+$14.99",
                "gain_loss_pct": "+20.0%"
            },
        ]
    
    table = dash_table.DataTable(
        id='holdings-table',
        columns=[
            {"name": "Card Name", "id": "name"},
            {"name": "Set", "id": "set"},
            {"name": "Qty", "id": "quantity"},
            {"name": "Buy Price", "id": "buy_price"},
            {"name": "Current Price", "id": "current_price"},
            {"name": "Gain/Loss", "id": "gain_loss"},
            {"name": "%", "id": "gain_loss_pct"},
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
                    'filter_query': '{gain_loss} contains "+"',
                    'column_id': ['gain_loss', 'gain_loss_pct']
                },
                'color': '#1E90FF',
                'fontWeight': 'bold'
            },
            # Losses in orange
            {
                'if': {
                    'filter_query': '{gain_loss} contains "-"',
                    'column_id': ['gain_loss', 'gain_loss_pct']
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
    add_button = dbc.Button(
        [html.Span("➕ ", style={"marginRight": "8px"}), "Add Card to Portfolio"],
        id="add-card-btn",
        color="success",
        className="mb-3"
    )
    
    return html.Div([
        add_button,
        table
    ])