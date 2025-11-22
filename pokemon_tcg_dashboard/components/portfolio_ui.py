import dash_bootstrap_components as dbc
from dash import html
from components.market_ui import create_metric_card  # Reuse!

def create_portfolio_summary_metrics():
    """
    Create the 4 metric cards for Portfolio View
    
    Returns:
        dbc.Row with 4 portfolio metric cards
    """
    # TODO: Values will come from Member 2's portfolio calculations
    
    metrics_row = dbc.Row([
        dbc.Col(
            create_metric_card(
                title="Total Portfolio Value",
                value="$12,450",
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
                value="156",
                change="+3 this week",
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