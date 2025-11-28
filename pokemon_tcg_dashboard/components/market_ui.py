import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from dash import dcc
from utils.market_calcs import MarketCalculator
from utils.loader import load_data

from global_variables import RARITY_OPTIONS, PRICE_HISTORY_DF, CARD_METADATA_DF

import logging
logger = logging.getLogger(__name__)



def create_metric_card(title, value, change=None, change_type="neutral"):
    """
    Create a single metric card
    
    Args:
        title: Card title (e.g., "Total Market Value")
        value: Main value to display (e.g., "$45.2M")
        change: Optional change value (e.g., "+1.8%")
        change_type: "positive", "negative", or "neutral"
    
    Returns:
        dbc.Card component
    """
    # Color based on change type
    color_map = {
        "positive": "#1E90FF",  # Blue for gains
        "negative": "#FF8C00",  # Orange for losses
        "neutral": "#808080"    # Gray for neutral
    }
    change_color = color_map.get(change_type, "#808080")
    
    # Arrow icon based on change type
    arrow = "↑" if change_type == "positive" else "↓" if change_type == "negative" else ""
    
    card = dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title text-muted mb-2"),
            html.H3(value, className="card-value mb-1"),
            html.P(
                [
                    html.Span(arrow, style={"marginRight": "5px"}),
                    html.Span(change if change else "")
                ],
                style={"color": change_color, "fontWeight": "bold"},
                className="mb-0"
            ) if change else html.Div()
        ]),
        className="metric-card shadow-sm h-100",
        style={
            "borderRadius": "10px",
            "border": "none",
            "transition": "transform 0.2s",
            "cursor": "pointer"
        }
    )
    
    return card

def create_market_overview_metrics(days:int=1):
    """
    Create the 4 metric cards for Market View
    
    Returns:
        dbc.Row with 4 metric cards
    """
    # TODO: These values will come from Member 2's calculations
    # For now, use placeholder values
    logger.debug("create_market_overview_metrics called!")
    
    price_history_df = PRICE_HISTORY_DF
    card_metadata_df = CARD_METADATA_DF
    market_calculator = MarketCalculator(price_history_df, card_metadata_df)
    market_change_type = "positive" if market_calculator.calculate_change(days)['change_value'] > 0 else "negative" if market_calculator.calculate_change(days)['change_value'] < 0 else "neutral"
    set_change_type = "positive" if market_calculator.calculate_best_performing_set(days)['change_pct'] > 0 else "negative" if market_calculator.calculate_best_performing_set(days)['change_pct'] < 0 else "neutral"
    logger.debug(f"total_market_value: {market_calculator.calculate_total_market_value()}")
    logger.debug(f"price_change: {market_calculator.calculate_change(days)}")
    label = "All time Change" if days == -1 else f"{days} Change"
    
    metrics_row = dbc.Row([
        dbc.Col(
            create_metric_card(
                title="Total Market Value",
                value=market_calculator.calculate_total_market_value()['formatted'],
                #change=market_calculator.calculate_change(days)['formatted_value'],
                change_type= market_change_type
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title=label,
                value=market_calculator.calculate_change(days)['formatted_pct'],
                change=market_calculator.calculate_change(days)['formatted_value'],
                change_type=market_change_type
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Best Performing Set",
                value=market_calculator.calculate_best_performing_set(days)['set_name'],
                change=market_calculator.calculate_best_performing_set(days)['formatted'],
                change_type=set_change_type
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Active Listings",
                value=market_calculator.count_active_listings(days)['formatted'],
                #change="+342",
                #change_type="neutral"
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
    ], className="mb-4")
    
    return metrics_row

def create_market_filters():
    """
    Create filter controls for Market View
    
    Returns:
        dbc.Row with search and filter components
    """
    # TODO: Dropdown options will come from Member 2's data
    # Placeholder options for now
    
    
    
    '''set_options = [
        {"label": "All Sets", "value": "all"},
        {"label": "Scarlet & Violet 151", "value": "sv151"},
        {"label": "Obsidian Flames", "value": "obf"},
        {"label": "Paldea Evolved", "value": "pev"},
        {"label": "Temporal Forces", "value": "tef"},
        {"label": "Twilight Masquerade", "value": "twm"},
    ]'''
    
    '''rarity_options = [
        {"label": "All Rarities", "value": "all"},
        {"label": "Common", "value": "common"},
        {"label": "Uncommon", "value": "uncommon"},
        {"label": "Rare", "value": "rare"},
        {"label": "Ultra Rare", "value": "ultra_rare"},
        {"label": "Special Illustration Rare", "value": "special_rare"},
    ]'''
    
    filters = dbc.Row([
        # Search bar
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("🔍"),
                dbc.Input(
                    id="market-search-input",
                    placeholder="Search cards...",
                    type="text"
                ),
            ])
        ], width=4),
        
        # Rarity filter
        dbc.Col([
            dcc.Dropdown(
                id="market-rarity-select",
                options=RARITY_OPTIONS,
                #value="all",
                placeholder="Filter by Rarity",
                multi=True,
                clearable=False,
                style={"borderRadius": "5px"}
            )
        ], width=4),
        
        # Clear button
        dbc.Col([
            dbc.Button(
                "Clear Filters",
                id="clear-filters-btn",
                color="secondary",
                outline=True,
                className="w-100"
            )
        ], width=4),
    ])
    
    return filters

def create_top_movers_table(data=None):
    """
    Create top movers table
    
    Args:
        data: List of dicts with keys: name, set, current_price, price_change, pct_change
    
    Returns:
        html.Div with toggle buttons and table
    """
    # TODO: Data will come from Member 2
    # Placeholder data for testing
    if data is None:
        data = [
            {
                "name": "Charizard ex",
                "setName": "Obsidian Flames",
                "current_price": "$45.99",
                "price_change": "+5.2%",
                "pct_change": "+12.8%"
            },
            {
                "name": "Pikachu VMAX",
                "setName": "Vivid Voltage",
                "current_price": "$32.50",
                "price_change": "+3.1%",
                "pct_change": "+8.4%"
            },
            {
                "name": "Mewtwo V",
                "setName": "Pokemon GO",
                "current_price": "$18.75",
                "price_change": "-2.3%",
                "pct_change": "-5.1%"
            },
            {
                "name": "Umbreon VMAX",
                "setName": "Evolving Skies",
                "current_price": "$89.99",
                "price_change": "+8.5%",
                "pct_change": "+15.2%"
            },
            {
                "name": "Rayquaza VMAX",
                "setName": "Evolving Skies",
                "current_price": "$125.00",
                "price_change": "-1.5%",
                "pct_change": "-3.8%"
            },
        ]
    
    table = dash_table.DataTable(
        id='top-movers-table',
        columns=[
            {"name": "Card Name", "id": "name"},
            {"name": "Set", "id": "setName"},
            {"name": "Current Price", "id": "current_price"},
            {"name": "Price Change", "id": "price_change"},
            {"name": "Percent Change", "id": "pct_change"},
        ],
        data=data,
        sort_action="native",
        page_size=20,
        style_table={
            'overflowX': 'auto'
        },
        style_header={
            'backgroundColor': '#0075BE',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'padding': '10px',
            "font-family": "Helvetica, Arial, sans-serif"
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '14px',
            "font-family": "Helvetica, Arial, sans-serif"
        },
        style_data_conditional=[
            # Color positive changes blue
            {
                'if': {
                    'filter_query': '{price_change} contains "+"',
                    'column_id': 'price_change'
                },
                'color': '#1E90FF',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{pct_change} contains "+"',
                    'column_id': 'pct_change'
                },
                'color': '#1E90FF',
                'fontWeight': 'bold'
            },
            # Color negative changes orange
            {
                'if': {
                    'filter_query': '{price_change} contains "-"',
                    'column_id': 'price_change'
                },
                'color': '#FF8C00',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{pct_change} contains "-"',
                    'column_id': 'pct_change'
                },
                'color': '#FF8C00',
                'fontWeight': 'bold'
            },
            # Row hover effect
            {
                'if': {'state': 'active'},
                'backgroundColor': 'rgba(0, 117, 190, 0.1)',
                'border': '1px solid #0075BE'
            }
        ]
    )
    
    # Add toggle buttons for Gainers/Losers
    '''toggle_buttons = dbc.ButtonGroup([
        dbc.Button("Gainers", id="btn-gainers", color="primary", outline=True),
        dbc.Button("Losers", id="btn-losers", color="danger", outline=True),
    ], className="mb-3")'''
    
    '''return html.Div([
        toggle_buttons,
        table
    ])'''

    return table

def create_set_release_date_table(data):
    """
    Creates a Dash DataTable showing Pokémon set names and release dates.

    Parameters:
    -----------
    data : pd.DataFrame
        Must contain at least two columns: 'setName' and 'release_date'

    Returns:
    --------
    dash_table.DataTable
    """
    df = data[['setName', 'release_date']].copy()
    df['release_date'] = pd.to_datetime(df['release_date']).dt.date.astype(str)

    table = dash_table.DataTable(
        columns=[
            {"name": "Set Name", "id": "setName", "type": "text"},
            {"name": "Release Date", "id": "release_date", "type": "text"}
        ],
        data=df.to_dict('records'),
        sort_action='native',      # allow sorting by clicking headers
        page_size=20,              # show 10 rows per page
        style_table={
            'height': '100%',      
            'overflowY': 'auto',   
            'width': '100%'
        },
        style_header={
            'backgroundColor': '#0075BE',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'padding': '10px',
            "font-family": "Helvetica, Arial, sans-serif"
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '14px',
            "font-family": "Helvetica, Arial, sans-serif"
        }
    )

    return table
