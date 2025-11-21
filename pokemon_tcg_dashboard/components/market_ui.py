import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

from utils.market_calcs import MarketCalculator
from utils.loader import load_data

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
        className="metric-card shadow-sm",
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
    
    price_history_df = load_data("price_history.csv")
    card_metadata_df = load_data("cards_metadata_table.csv")
    market_calculator = MarketCalculator(price_history_df, card_metadata_df)


    metrics_row = dbc.Row([
        dbc.Col(
            create_metric_card(
                title="Total Market Value",
                value=market_calculator.calculate_total_market_value()['formatted'],
                change=market_calculator.calculate_change(days)['formatted_value'],
                change_type="positive"
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="24h Change",
                value="+1.8%",
                change="↑ $812K",
                change_type="positive"
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Best Performing Set",
                value="SV151",
                change="+5.2%",
                change_type="positive"
            ),
            width=12, md=6, lg=3, className="mb-3"
        ),
        dbc.Col(
            create_metric_card(
                title="Active Listings",
                value="12,453",
                change="+342",
                change_type="neutral"
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
    
    from dash import dcc
    
    set_options = [
        {"label": "All Sets", "value": "all"},
        {"label": "Scarlet & Violet 151", "value": "sv151"},
        {"label": "Obsidian Flames", "value": "obf"},
        {"label": "Paldea Evolved", "value": "pev"},
        {"label": "Temporal Forces", "value": "tef"},
        {"label": "Twilight Masquerade", "value": "twm"},
    ]
    
    rarity_options = [
        {"label": "All Rarities", "value": "all"},
        {"label": "Common", "value": "common"},
        {"label": "Uncommon", "value": "uncommon"},
        {"label": "Rare", "value": "rare"},
        {"label": "Ultra Rare", "value": "ultra_rare"},
        {"label": "Special Illustration Rare", "value": "special_rare"},
    ]
    
    filters = dbc.Row([
        # Search bar
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("🔍"),
                dbc.Input(
                    id="search-input",
                    placeholder="Search cards...",
                    type="text"
                ),
            ])
        ], width=12, md=4, className="mb-3"),
        
        # Set filter
        dbc.Col([
            dcc.Dropdown(
                id="set-filter",
                options=set_options,
                value="all",
                placeholder="Filter by Set",
                clearable=False,
                style={"borderRadius": "5px"}
            )
        ], width=12, md=3, className="mb-3"),
        
        # Rarity filter
        dbc.Col([
            dcc.Dropdown(
                id="rarity-filter",
                options=rarity_options,
                value="all",
                placeholder="Filter by Rarity",
                clearable=False,
                style={"borderRadius": "5px"}
            )
        ], width=12, md=3, className="mb-3"),
        
        # Clear button
        dbc.Col([
            dbc.Button(
                "Clear Filters",
                id="clear-filters-btn",
                color="secondary",
                outline=True,
                className="w-100"
            )
        ], width=12, md=2, className="mb-3"),
    ], className="mb-4")
    
    return filters