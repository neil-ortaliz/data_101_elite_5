import dash_bootstrap_components as dbc
from dash import html

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

def create_market_overview_metrics():
    """
    Create the 4 metric cards for Market View
    
    Returns:
        dbc.Row with 4 metric cards
    """
    # TODO: These values will come from Member 2's calculations
    # For now, use placeholder values
    
    metrics_row = dbc.Row([
        dbc.Col(
            create_metric_card(
                title="Total Market Value",
                value="$45.2M",
                change="+2.3%",
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