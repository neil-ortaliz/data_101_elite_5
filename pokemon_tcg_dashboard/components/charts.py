'''
================================ MEMBER 3 TASK LIST (UPDATED) ==============================

✅ Task 1: Set Performance Bar Chart (market_view_set_performance_bar_chart) - A horizontal bar chart showing value change for each Pokemon set.
Should show % gain/loss with color coding (green=profit, red=loss).
- Added date range filter (All Time, Last 90 Days, Last 30 Days, Last 15 Days, Last 7 Days).
- Added table form with dropdown to switch between date ranges.

✅ Task 2: Portfolio Performance Line Chart (portfolio_view_performance_line_chart) - Multi-line chart showing portfolio value over time.
Should show total value + individual set contributions.
- Issues: Unsure if it works smoothly

✅ Task 3: Collection Breakdown Pie Chart (portfolio_view_collection_pie_chart) - Pie chart showing portfolio composition by Pokemon set.
Should show percentage and value for each set.
- Issues: Unsure if it works smoothly

✅ Task 4: Price History Line Chart - Price history of a card from Ebay and TCG
- Issues: The chart works but since data is sparse, lines are disconnected. Need help to smooth or interpolate data for better visualization.

✅ Task 5: Grade Price Comparison Chart

□ Task 6: Chart Optimization

================================ Notes ==============================
- Time range of set performance - add date filtering 

Nov 19, 2025
Main charts work as intended (tested in colab), but I need help for the following:
- Ensuring that the merged datasets/dataframes I'm using are correct.
- How to integrate data from Member 2 to the functions.

Nov 21, 2025
- Portfolio - Neil will give list of IDs
- Add parameter that accept number of days for the callbacks
'''
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import dash_table

import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from utils.loader import load_data, get_set_price_history
import logging

# initialize module logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
from global_variables import PRICE_HISTORY_DF, CARD_METADATA_DF, EBAY_METADATA_DF, SET_PRICE_HISTORY_DFS
# ----------------------------- Call data -------------------------------------
ebay_df = EBAY_METADATA_DF.set_index('date')
metadata_df = CARD_METADATA_DF
price_history_df = PRICE_HISTORY_DF.set_index('date')
#portfolio_sample_df = load_data('portfolio_cards_metadata_table.csv')

# ------------------------------ Merge Data --------------------------------------
'''
1. Ebay Price History + Metadata
2. Price History + Metadata
'''


def merge_ebay_metadata_dfs(ebay_df, metadata_df):
    logger.debug("merge_ebay_metadata_dfs was called!")
    # Ebay + Metadata
    ebay_metadata = ebay_df.merge(
        metadata_df[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
        on="id",
        how="left"
    )
    ebay_metadata = ebay_metadata.dropna(subset='setName')
    ebay_metadata['date'] = pd.to_datetime(ebay_metadata['date'])
    return ebay_metadata

# Price History + Metadata
def merge_price_history_metadata_dfs(price_history_metadata, metadata_df):
    logger.debug("merge_price_history_metadata_dfs was called!")
    price_history_metadata = price_history_df.merge(
        metadata_df[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
        on="id",
        how="left"
    )

    price_history_metadata = price_history_metadata.dropna(subset="setName")
    price_history_metadata['date'] = pd.to_datetime(price_history_metadata['date'])
    return price_history_metadata

def merge_all_pricing_dfs():
    logger.debug("merge_all_pricing_dfs was called!")
    # All three combined
    ebay_metadata = merge_ebay_metadata_dfs(ebay_df, metadata_df)
    price_history_metadata = merge_price_history_metadata_dfs(price_history_df, metadata_df)
    market_df = ebay_metadata.merge(
        price_history_metadata[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
        on=['id'],
        how='left',
    )

    #print(f"market_df columns: {market_df.columns}")

    market_df = market_df.dropna(subset='setName_x')





# ------------------------------- Compute Change in Price -------------------------
def compute_price_change(ebay_metadata):
    logger.debug("compute_price_change was called")
    ebay_metadata = ebay_metadata.sort_values(by=['setName', 'date'])
    ebay_metadata['date'] = pd.to_datetime(ebay_metadata['date'])

    # Group by set/day and compute average price per setName per day
    set_daily = (
        ebay_metadata.groupby(['setName', 'date'])['average']
        .mean()
        .reset_index()
        .sort_values(by=['setName', 'date'])
    )

    # Compute previous day price and percentage change
    set_daily['prev_price'] = set_daily.groupby('setName')['average'].shift(1)
    set_daily['price_change'] = set_daily['average'] - set_daily['prev_price']
    set_daily['pct_change'] = (set_daily['price_change'] / set_daily['prev_price']) * 100
    set_daily['pct_change'] = set_daily['pct_change'].fillna(0)

    # Keep latest price change per set
    latest_set_prices = (
        set_daily.sort_values('date')
                .groupby('setName')
                .tail(1)
                .reset_index(drop=True)
    )
    latest_set_prices = latest_set_prices[['setName', 'date', 'pct_change']]
    latest_set_prices = latest_set_prices.rename(columns={'pct_change': 'value_change_pct'})

    return latest_set_prices

#========================================== MARKET VIEW ===================================================

# ------------------------ FUNCTION: Set Performance Bar Chart with Date Range ----------------
def market_view_set_performance_bar_chart(time_range="All Time"):
    logger.debug(f"Calling market_view_set_performance_bar_chart")
    """
    Bar chart of Pokemon set performance (price change %) filtered by date range.
    
    Parameters:
    - time_range: str, one of ["All Time", "Last 90 Days", "Last 30 Days", "Last 15 Days", "Last 7 Days"]
    
    Returns:
    - Plotly Figure
    """
    # 'date' is datetime
    ebay_metadata_df = merge_ebay_metadata_dfs(ebay_df, metadata_df)
    latest_set_prices = compute_price_change(ebay_metadata_df)
    latest_set_prices['date'] = pd.to_datetime(latest_set_prices['date'])
    max_date = latest_set_prices['date'].max()
    logger.debug(f"Latest set price max_date: {max_date} (rows={len(latest_set_prices)})")

    # Define date ranges
    date_ranges = {
        "All Time": latest_set_prices,
        "Last 90 Days": latest_set_prices[latest_set_prices['date'] >= max_date - pd.Timedelta(days=90)],
        "Last 30 Days": latest_set_prices[latest_set_prices['date'] >= max_date - pd.Timedelta(days=30)],
        "Last 15 Days": latest_set_prices[latest_set_prices['date'] >= max_date - pd.Timedelta(days=15)],
        "Last 7 Days": latest_set_prices[latest_set_prices['date'] >= max_date - pd.Timedelta(days=7)],
    }

    # Filter by selected time range
    filtered_data = date_ranges.get(time_range, latest_set_prices)
    logger.debug(f"Filtered data for '{time_range}' has {len(filtered_data)} rows")

    # Sort by value change for bar chart
    sorted_data = filtered_data.sort_values('value_change_pct')

    # Colors: green positive, red negative
    colors = ['#22c55e' if x >= 0 else '#ef4444' for x in sorted_data['value_change_pct']]

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_data['setName'],
        x=sorted_data['value_change_pct'],
        orientation='h',
        marker=dict(color=colors),
        text=sorted_data['value_change_pct'].apply(lambda x: f'{x:+.1f}%'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Change: %{x:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f'Pokemon Set Performance - {time_range}',
        xaxis_title='Price Change (%)',
        yaxis_title='',
        height=700,
        template='plotly_white',
        showlegend=False,
        margin=dict(l=150, r=50, t=50, b=50)
    )

    logger.debug(f"Created set performance bar chart (time_range={time_range}) with {len(sorted_data)} bars")
    return fig

# ------------------------------------ TABLE FORM ------------------------------------------
def create_top_sets_table(price_col="price", days=7, set_names=None):
    logger.debug(f"Calling create_top_sets_table")
    days = int(days)
    set_price_history_df = SET_PRICE_HISTORY_DFS.copy()

    if set_names is not None:
        if isinstance(set_names, str):
            set_names = [set_names]
        set_price_history_df = set_price_history_df[
            set_price_history_df['set_name'].isin(set_names)
        ]

    set_price_history_df[price_col] = pd.to_numeric(
        set_price_history_df[price_col], errors="coerce"
    )

    # --- DATE RANGES ---
    max_date = set_price_history_df.index.max()
    if days == -1:
        date_range_df = set_price_history_df
    else:
        date_range_df = set_price_history_df[
            set_price_history_df.index >= max_date - pd.Timedelta(days=days)
        ]

    current_df = (
        date_range_df.sort_index()
        .groupby("set_name")
        .tail(1)
        .reset_index()
    )

    # Get earliest price in the selected range
    filtered_min_date = date_range_df.index.min()
    earliest_prices_df = date_range_df[
        date_range_df.index == filtered_min_date
    ][["set_name", "price"]].reset_index()

    earliest_prices_df = earliest_prices_df.rename(
        columns={"price": "earliest_price"}
    )

    current_df = current_df.merge(
        earliest_prices_df[['set_name', 'earliest_price']],
        on='set_name',
        how='left'
    )

    current_df["price_change"] = current_df["price"] - current_df["earliest_price"]
    current_df["pct_change"] = (
        current_df["price_change"] / current_df["earliest_price"] * 100
    )

    current_df["Rank"] = (
        current_df["price"]
        .rank(ascending=False, method="first")
        .astype(int)
    )

    current_df = current_df.sort_values(by="Rank", ascending=True)

    current_df = current_df.replace([np.inf, -np.inf], np.nan)
    current_df[['price', 'price_change', 'pct_change']] =(
        current_df[['price', 'price_change', 'pct_change']].fillna("N/A")
    )

    # Format values for display
    current_df["price"] = current_df["price"].map(lambda x: f"${x:,.2f}")
    current_df["price_change"] = current_df["price_change"].map(lambda x: f"{x:+.2f}")
    current_df["pct_change"] = current_df["pct_change"].map(lambda x: f"{x:+.2f}%")

    data_table_columns = [
        {"name": "Set Name", "id": "set_name"},
        {"name": "Current Price", "id": "price"},
        {"name": "Change", "id": "price_change"},
        {"name": "% Change", "id": "pct_change"},
    ]

    style_data_conditional = [
        # Positive changes blue
        {"if": {"filter_query": "{price_change} contains '+'", "column_id": "price_change"},
         "color": "#1E90FF", "fontWeight": "bold"},
        {"if": {"filter_query": "{pct_change} contains '+'", "column_id": "pct_change"},
         "color": "#1E90FF", "fontWeight": "bold"},
        # Negative changes orange
        {"if": {"filter_query": "{price_change} contains '-'", "column_id": "price_change"},
         "color": "#FF8C00", "fontWeight": "bold"},
        {"if": {"filter_query": "{pct_change} contains '-'", "column_id": "pct_change"},
         "color": "#FF8C00", "fontWeight": "bold"},
        # Row hover effect
        {"if": {"state": "active"}, "backgroundColor": "rgba(0, 117, 190, 0.1)",
         "border": "1px solid #0075BE"}
    ]

    return dash_table.DataTable(
        id="top-movers-table",
        data=current_df.to_dict("records"),
        columns=data_table_columns,
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
        style_data_conditional=style_data_conditional,
        page_size=20,
        sort_action="native",
        #filter_action="native",
        style_table={"overflowX": "auto"}
    )



#========================================== PORTFOLIO VIEW ===================================================
# ------------------- FUNCTION 2: Portfolio Performance Line Chart --------------
def portfolio_view_performance_line_chart(ids:list, days:int=1):
    logger.debug(f"Calling portfolio_view_performance_line_chart")
    portfolio_ids = ids
    portfolio_history = price_history_metadata[price_history_metadata['id'].isin(ids)].copy()
    logger.debug(f"Loaded portfolio history for {len(ids)} ids -> rows={len(portfolio_history)}")
    portfolio_history['date'] = pd.to_datetime(portfolio_history['date'])

    if days > 1:
        max_date = portfolio_history['date'].max()
        portfolio_history = portfolio_history[portfolio_history['date'] >= max_date - pd.Timedelta(days=days)]
        logger.debug(f"Filtered portfolio history to last {days} days -> rows={len(portfolio_history)}")

    portfolio_daily_value = (
        portfolio_history.groupby('date')['average']
        .sum()
        .reset_index()
        .sort_values('date')
    )
    logger.debug(f"Aggregated portfolio_daily_value rows={len(portfolio_daily_value)}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_daily_value['date'],
        y=portfolio_daily_value['total_value'],
        mode='lines',
        line=dict(width=3),
        hovertemplate='<b>Date:</b> %{x}<br><b>Total Value:</b> $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Portfolio Value Performance Over Time',
        xaxis_title='Date',
        yaxis_title='Total Portfolio Value (USD)',
        template='plotly_white',
        height=450,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig

# ------------------------ FUNCTION 3: Collection Breakdown Pie Chart -----------
def portfolio_view_collection_pie_chart(ids:list):
    logger.debug(f"Calling portfolio_view_collection_pie_chart")
    portfolio_breakdown_df = metadata_df[metadata_df['tcgPlayerId'].isin(ids)]
    logger.debug(f"Filtered metadata for ids -> rows={len(portfolio_breakdown_df)}")
    portfolio_breakdown_df = portfolio_breakdown_df.groupby('setName')['id'].nunique().reset_index()
    portfolio_breakdown_df.columns = ['setName', 'UniqueItemCount']
    portfolio_breakdown_df = portfolio_breakdown_df.sort_values(by='UniqueItemCount', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=portfolio_breakdown_df['setName'],
        values=portfolio_breakdown_df['UniqueItemCount'],
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Vivid),
        hovertemplate='<b>%{label}</b><br>Unique Items: %{value}<br>%{percent}<extra></extra>'
    ))

    fig.update_layout(
        title='Collection Breakdown by Set',
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5)
    )
    logger.debug(f"Prepared pie chart data with {len(portfolio_breakdown_df['setName'].unique())} sets")
    return fig


#========================================== CARD VIEW ===================================================
# ------------------------ FUNCTION 4: Price History Line Chart  -----------
# Convert date columns to datetime
'''ebay_metadata["date"] = pd.to_datetime(ebay_metadata["date"], errors="coerce")
price_history_metadata["date"] = pd.to_datetime(price_history_metadata["date"], errors="coerce")

# Filter TCGplayer price history to Near Mint only
price_history_nm = price_history_metadata[price_history_metadata["condition"] == "Near Mint"].copy()

# Rename columns
ebay_metadata = ebay_metadata.rename(columns={"average": "ebay_price"})
price_history_nm = price_history_nm.rename(columns={"market": "tcg_price"})

# Merge eBay and TCGplayer price history into one DataFrame
all_prices = pd.merge(
    ebay_metadata[["id", "date", "ebay_price"]],
    price_history_nm[["id", "date", "tcg_price"]],
    on=["id", "date"],
    how="outer"
)

# Clean & sort
all_prices["date"] = pd.to_datetime(all_prices["date"], errors="coerce")
all_prices = all_prices.sort_values(["id", "date"])
all_prices = all_prices.groupby(["id", "date"]).agg({
    "ebay_price": "mean",
    "tcg_price": "mean"
}).reset_index()

# ---------------------------- Date Ranges ----------------------------
max_date = all_prices["date"].max()

date_ranges = {
    "All Time": all_prices,
    "Last 90 Days": all_prices[all_prices["date"] >= max_date - pd.Timedelta(days=90)],
    "Last 30 Days": all_prices[all_prices["date"] >= max_date - pd.Timedelta(days=30)],
    "Last 15 Days": all_prices[all_prices["date"] >= max_date - pd.Timedelta(days=15)],
    "Last 7 Days": all_prices[all_prices["date"] >= max_date - pd.Timedelta(days=7)],
}'''

# ---------------------------- Function ----------------------------
import plotly.graph_objects as go
from datetime import datetime

def card_view_price_history_line_chart(card_name, card_id, card_df, price_column, grade_filter, platform_name=None, selected_date="all", selected_grade="all"):
    TCG_GRADE_COLORS = {
        "Near Mint": "#2ecc71",
        "Lightly Played": "#3498db",
        "Moderately Played": "#e67e22",
        "Heavily Played": "#e74c3c",
        "Damaged": "#7f8c8d"  
    }

    PSA_GRADE_COLORS = {
        "psa8": "#9b59b6",
        "psa9": "#f1c40f",
        "psa10": "#2ecc71"
    }
    
    if platform_name is None:
        platform_name = price_column

    # Filter by card_id
    df = card_df[card_df["tcgPlayerId"] == card_id].copy()
    if df.empty or price_column not in df.columns or df[price_column].isna().all():
        fig = go.Figure()
        fig.update_layout(
            title=f"No price history available for {card_name} ({platform_name})",
            template="plotly_white"
        )
        return fig

    # Filter by date range
    if selected_date != "all":
        days = int(selected_date)
        max_date = df["date"].max() if not df.empty else datetime.now()
        df = df[df["date"] >= max_date - timedelta(days=days)]

    df = df.sort_values("date")

    fig = go.Figure()

    # If "all" grades selected and grade column exists, plot one line per grade
    if selected_grade == "all" and grade_filter in df.columns:
        grades = df[grade_filter].dropna().unique()
        for grade in grades:
            df_grade = df[df[grade_filter] == grade]
            if df_grade.empty:
                continue
            # Select color palette
            if platform_name.lower() == "tcgplayer":
                color = TCG_GRADE_COLORS.get(grade, "#000000")
            else:
                color = PSA_GRADE_COLORS.get(grade, "#000000")
            
            fig.add_trace(go.Scatter(
                x=df_grade["date"],
                y=df_grade[price_column],
                mode="lines+markers",
                name=str(grade),
                line=dict(color=color, width=2),
                marker=dict(size=4)
            ))
    else:
        # Single grade or no grade column
        if selected_grade != "all" and grade_filter in df.columns:
            df = df[df[grade_filter] == selected_grade]

        if df.empty or price_column not in df.columns or df[price_column].isna().all():
            fig = go.Figure()
            fig.update_layout(
                title=f"No price history available for {card_name} ({platform_name}) in selected grade/condition",
                template="plotly_white"
            )
            return fig
        
        if platform_name.lower() == "tcgplayer":
            color = TCG_GRADE_COLORS.get(selected_grade, "#000000")
        else:
            color = PSA_GRADE_COLORS.get(selected_grade, "#000000")

        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df[price_column],
            mode="lines+markers",
            name=platform_name,
            line=dict(width=2, color=color),
            marker=dict(size=4)
        ))

    fig.update_layout(
        title=f"Price History – {card_name} ({platform_name})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        hovermode="x unified",
        height=450,
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date",
            tickformat="%Y-%m-%d"
        )
    )

    return fig
# ----------------- FUNCTION 5: Grade Price Comparison  -----------
def card_view_card_grade_price_comparison(price_history_df, ebay_history_df, card_id, card_name, grading_cost=20):
    """
    Compare graded vs ungraded card prices and sales volumes, and calculate ROI for grading to PSA 10.

    Parameters:
    - price_history_df: DataFrame of historical ungraded card prices
    - ebay_history_df: DataFrame of graded card listings
    - card_id: unique identifier for the card (tcgPlayerId)
    - card_name: human-readable card name (for titles)
    - grading_cost: cost to grade a card (default $20)

    Returns:
    - graded_data: filtered DataFrame of graded cards
    - ungraded_data: filtered DataFrame of ungraded cards
    - fig: Plotly figure object
    """
    GRADE_COLORS = {
        "Ungraded": "#95a5a6",
        "PSA 8": "#9b59b6",
        "PSA 9": "#f1c40f",
        "PSA 10": "#2ecc71"
    }

    logger.debug(f"Calling card_view_card_grade_price_comparison for {card_name} ({card_id})")

    # -------------------- Filter Data --------------------
    graded_data = ebay_history_df[ebay_history_df['tcgPlayerId'] == card_id].copy()
    ungraded_data = price_history_df[price_history_df['tcgPlayerId'] == card_id].copy()
    
    logger.debug(f"Found graded rows={len(graded_data)}, ungraded rows={len(ungraded_data)} for '{card_name}'")

    if graded_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No graded data found for {card_name}",
            template="plotly_white"
        )
        return fig

    # Extract numeric PSA grades
    graded_data['psa_grade_numeric'] = graded_data['grade'].str.extract(r'psa(\d+)', expand=False).astype(float)
    graded_data = graded_data[graded_data['psa_grade_numeric'].isin([8.0, 9.0, 10.0])]

    # Ungraded average price and sales count
    if ungraded_data.empty:
        ungraded_avg_price = graded_data['average'].iloc[0] if 'average' in graded_data.columns else 0
        ungraded_sales_count = 0
    else:
        ungraded_avg_price = ungraded_data['market'].mean() if 'market' in ungraded_data.columns else 0
        ungraded_sales_count = len(ungraded_data)

    # -------------------- Prepare Data --------------------
    # Sales Volume
    grade_counts = graded_data['psa_grade_numeric'].value_counts().sort_index()
    categories_volume = ['Ungraded'] + [f'PSA {int(g)}' for g in grade_counts.index]
    counts = [max(ungraded_sales_count, 1)] + grade_counts.tolist()
    colors_volume = [GRADE_COLORS.get(cat, "#7f8c8d") for cat in categories_volume]  # fallback color if missing

    # Price
    price_by_grade = graded_data.groupby('psa_grade_numeric')['average'].mean().sort_index()
    categories_price = ['Ungraded'] + [f'PSA {int(g)}' for g in price_by_grade.index]
    prices = [ungraded_avg_price] + price_by_grade.tolist()
    colors_price = [GRADE_COLORS.get(cat, "#7f8c8d") for cat in categories_price]  # fallback color

    # -------------------- Create Subplots --------------------
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Sales Volume", "Average Price (USD)"))

    fig.update_layout(
        height=600,  # taller to fit annotations below
        template='plotly_white'
    )

    # Sales Volume Bar Chart
    fig.add_trace(go.Bar(
        x=categories_volume,
        y=counts,
        marker_color=colors_volume,
        text=counts,
        textposition='outside',
        name='Sales Volume'
    ), row=1, col=1)

    # Price Bar Chart
    fig.add_trace(go.Bar(
        x=categories_price,
        y=prices,
        marker_color=colors_price,
        text=[f"${p:.2f}" for p in prices],
        textposition='outside',
        name='Average Price'
    ), row=1, col=2)

    # -------------------- ROI Annotations for PSA 8, 9, 10 (horizontal) --------------------
    y_pos = -0.15  # row below the chart in paper coordinates
    x_start = 0.02  # starting horizontal position
    x_step = 0.32   # space between annotations (adjust as needed)

    for i, grade in enumerate([8.0, 9.0, 10.0]):
        if grade in price_by_grade.index:
            psa_price = price_by_grade[grade]
            roi = psa_price - ungraded_avg_price - grading_cost
            roi_pct = (roi / (ungraded_avg_price + grading_cost)) * 100
            verdict = "✓ WORTH GRADING" if roi > 0 else "✗ NOT WORTH GRADING"
            color = 'green' if roi > 0 else 'red'

            fig.add_annotation(
                x=x_start + i * x_step,  # position horizontally
                y=y_pos,
                xref='paper',
                yref='paper',
                text=f"PSA {int(grade)} ROI: ${roi:.2f} ({roi_pct:+.0f}%) | {verdict}",
                showarrow=False,
                font=dict(size=12, color=color),
                align='center',
                bordercolor=color,
                borderwidth=1,
                borderpad=4,
                bgcolor='wheat',
                opacity=0.8
            )
    return fig
'''
# -------------------- CALL FUNCTION --------------------
graded_data, ungraded_data = portfolio_view_graded_ungraded_plotly("Zekrom ex - 172/086")
'''