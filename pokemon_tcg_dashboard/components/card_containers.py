import dash_bootstrap_components as dbc

from dash import html, dcc


def tab_card_container(content=None, class_name=""):
    return dbc.Card(
        dbc.CardBody(
            [content]
        ),
        class_name=class_name
    )

def ban_card_container(fig=None, title="", header_id="", card_id="card", card_body_id=""):
    return dbc.Card(
        [
            dbc.CardHeader(children=title, id=header_id),
            dbc.CardBody(
                [
                    html.Div(fig)
                ], id=card_body_id
            )
        ],
        id=card_id
    )

def graph_container(fig=None, title="Visualization Here", class_name=None, fig_id="graph-container-fig", container_id="graph-container"):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(title, className="card-title"),
                    html.Div(dcc.Graph(id=fig_id, figure=fig))
                    
                ],
                id=container_id,
            )
        ],
        
        class_name=class_name
    )

def table_container(table=None, title="Table Here", class_name=None, container_id="table-container"):
    return dbc.Card(
        [   html.H4(title, className="card-title"),
            dbc.CardBody(
                [
                    html.Div(table)
                ],
                id=container_id
            )
        ],
        class_name=class_name
    )

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