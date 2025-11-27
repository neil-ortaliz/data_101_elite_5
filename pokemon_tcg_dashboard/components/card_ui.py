import dash_bootstrap_components as dbc
from dash import html

def create_card_header(card_data=None):
    """
    Create header section for Card View
    
    Args:
        card_data: Dict with card information
    
    Returns:
        dbc.Row with card image and metadata
    """
    # TODO: Card data from Member 2
    if card_data is None:
        card_data = {
            "name": "Charizard ex",
            "set": "Obsidian Flames",
            "rarity": "Double Rare",
            "card_number": "125/197",
            "image_url": "https://images.pokemontcg.io/sv3/125_hires.png",
            "current_price": "$45.99",
            "psa10_price": "$120.00",
            "ungraded_price": "$38.50",
            "total_listings": 234
        }
    
    header = dbc.Row([
        # Left: Card Image
        dbc.Col([
            html.Div([
                html.Img(
                    src=card_data.get("image_url", ""),
                    alt=card_data.get("name", ""),
                    className="card-image img-fluid",
                    style={
                        "maxHeight": "500px",
                        "borderRadius": "15px",
                        "boxShadow": "0 10px 30px rgba(0,0,0,0.2)",
                        "transition": "transform 0.3s"
                    }
                )
            ], className="text-center")
        ], width=12, md=5, className="mb-4"),
        
        # Right: Card Information
        dbc.Col([
            # Card name and set
            html.H2(card_data.get("name", ""), className="card-name mb-2"),
            html.P([
                dbc.Badge(card_data.get("set", ""), color="primary", className="me-2"),
                dbc.Badge(card_data.get("rarity", ""), color="secondary", className="me-2"),
                html.Span(f"#{card_data.get('card_number', '')}", className="text-muted")
            ], className="mb-3"),
            
            html.Hr(),
            
            # Current price (prominent)
            html.Div([
                html.H6("Current Market Price", className="text-muted mb-1"),
                html.H1(
                    card_data.get("current_price", ""),
                    className="current-price",
                    style={"color": "#0075BE", "fontWeight": "bold"}
                )
            ], className="mb-4"),
            
            # Quick stats
            html.H6("Quick Stats", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P("PSA 10 Price", className="text-muted mb-1"),
                        html.H5(card_data.get("psa10_price", ""), className="mb-0")
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.P("PSA 9 Price", className="text-muted mb-1"),
                        html.H5(card_data.get("psa9_price", ""), className="mb-0")
                    ])
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P("PSA 8 Price", className="text-muted mb-1"),
                        html.H5(card_data.get("psa8_price", ""), className="mb-0")
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.P("Ungraded Price", className="text-muted mb-1"),
                        html.H5(card_data.get("ungraded_price", ""), className="mb-0")
                    ])
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P("Total Listings", className="text-muted mb-1"),
                        html.H5(str(card_data.get("total_listings")), className="mb-0")
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.P("Market Trend", className="text-muted mb-1"),
                        html.H5(
                            [
                                html.Span(
                                    "↑" if card_data.get("card_trend") == "up" else ("↓" if card_data.get("card_trend") == "down" else "→"),
                                    style={
                                        "marginRight": "5px",
                                        "color": (
                                            "#1E90FF" if card_data.get("card_trend") == "up"
                                            else ("red" if card_data.get("card_trend") == "down" else "gray")
                                        )
                                    }
                                ),
                                "Trending Up" if card_data.get("card_trend") == "up" 
                                else ("Trending Down" if card_data.get("card_trend") == "down" else "Stable")
                            ],
                            className="mb-0",
                            style={
                                "color": (
                                    "#1E90FF" if card_data.get("card_trend") == "up"
                                    else ("red" if card_data.get("card_trend") == "down" else "gray")
                                )
                            }
                        )
                    ])
                ], width=6),
            ])
        ], width=12, md=7)
    ], className="card-header-section mb-5")
    
    return header

def create_action_buttons():
    """
    Create action buttons for Card View
    
    Returns:
        dbc.Row with 3 action buttons
    """
    buttons = dbc.Row([
        dbc.Col([
            dbc.Button(
                [
                    html.Span("➕ ", style={"marginRight": "8px"}),
                    "Add to Portfolio"
                ],
                id="add-to-portfolio-btn",
                color="success",
                size="lg",
                className="w-100 action-button"
            )
        ], width=12, md=4, className="mb-3"),
        
        dbc.Col([
            dbc.Button(
                [
                    html.Span("🔔 ", style={"marginRight": "8px"}),
                    "Set Price Alert"
                ],
                id="set-alert-btn",
                color="warning",
                size="lg",
                outline=True,
                className="w-100 action-button"
            )
        ], width=12, md=4, className="mb-3"),
        
        dbc.Col([
            dbc.Button(
                [
                    html.Span("📤 ", style={"marginRight": "8px"}),
                    "Share Card"
                ],
                id="share-card-btn",
                color="primary",
                size="lg",
                outline=True,
                className="w-100 action-button"
            )
        ], width=12, md=4, className="mb-3"),
    ], className="mb-4")
    
    return buttons