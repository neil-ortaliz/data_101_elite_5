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
                        html.P("Ungraded Price", className="text-muted mb-1"),
                        html.H5(card_data.get("ungraded_price", ""), className="mb-0")
                    ])
                ], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P("Total Listings", className="text-muted mb-1"),
                        html.H5(str(card_data.get("total_listings", 0)), className="mb-0")
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.P("Market Trend", className="text-muted mb-1"),
                        html.H5([
                            html.Span("↑", style={"marginRight": "5px", "color": "#1E90FF"}),
                            "Trending Up"
                        ], className="mb-0", style={"color": "#1E90FF"})
                    ])
                ], width=6),
            ])
        ], width=12, md=7)
    ], className="card-header-section mb-5")
    
    return header