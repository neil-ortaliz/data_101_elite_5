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