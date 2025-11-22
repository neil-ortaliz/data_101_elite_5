'''
================================ MEMBER 3 TASK LIST (UPDATED) ==============================

✅ Task 1: Set Performance Bar Chart (market_view_set_performance_bar_chart) - A horizontal bar chart showing value change for each Pokemon set.
Should show % gain/loss with color coding (green=profit, red=loss).
- Added date range filter (All Time, Last 90 Days, Last 30 Days, Last 15 Days, Last 7 Days).
- Added table form with dropdown to switch between date ranges.

🟨 Task 2: Portfolio Performance Line Chart (portfolio_view_performance_line_chart) - Multi-line chart showing portfolio value over time.
Should show total value + individual set contributions.

✅ Task 3: Collection Breakdown Pie Chart (portfolio_view_collection_pie_chart) - Pie chart showing portfolio composition by Pokemon set.
Should show percentage and value for each set.

✅ Task 4: Price History Line Chart 
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

import pandas as pd
from datetime import timedelta
from utils.loader import load_data

# ----------------------------- Call data -------------------------------------
ebay_df = load_data('ebay_price_history.csv')
metadata_df = load_data('cards_metadata_table.csv')
price_history_df = load_data('price_history.csv')
portfolio_sample_df = load_data('portfolio_cards_metadata_table.csv')

# ------------------------------ Merge Data --------------------------------------
'''
1. Ebay Price History + Metadata
2. Price History + Metadata
'''
# Ebay + Metadata
ebay_metadata = ebay_df.merge(
    metadata_df[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
    on="id",
    how="left"
)
ebay_metadata = ebay_metadata.dropna(subset='setName')

# Price History + Metadata
price_history_metadata = price_history_df.merge(
    metadata_df[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
    on="id",
    how="left"
)
price_history_metadata = price_history_metadata.dropna(subset="setName")

# Date Format
ebay_metadata['date'] = pd.to_datetime(ebay_metadata['date'])
price_history_metadata['date'] = pd.to_datetime(price_history_metadata['date'])


# ------------------------------- Compute Change in Price -------------------------
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

#========================================== MARKET VIEW ===================================================

# ------------------------ FUNCTION: Set Performance Bar Chart with Date Range ----------------
def market_view_set_performance_bar_chart(time_range="All Time"):
    """
    Bar chart of Pokemon set performance (price change %) filtered by date range.
    
    Parameters:
    - time_range: str, one of ["All Time", "Last 90 Days", "Last 30 Days", "Last 15 Days", "Last 7 Days"]
    
    Returns:
    - Plotly Figure
    """
    # Ensure 'date' is datetime
    latest_set_prices['date'] = pd.to_datetime(latest_set_prices['date'])
    max_date = latest_set_prices['date'].max()

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
        height=450,
        template='plotly_white',
        showlegend=False,
        margin=dict(l=150, r=50, t=50, b=50)
    )

    return fig

# ------------------------------------ TABLE FORM ------------------------------------------
def create_top_sets_table(ebay_metadata, price_col="average"):
    """
    Parameters
    ebay_metadata : pd.DataFrame
        DataFrame containing at least ['setName', 'totalSetNumber', 'date', price_col]
    price_col : str, default "average"
        Column name in ebay_metadata representing the market price
    """

    # Ensure numeric price
    ebay_metadata[price_col] = pd.to_numeric(ebay_metadata[price_col], errors="coerce")
    ebay_metadata["date"] = pd.to_datetime(ebay_metadata["date"], errors="coerce")

    # --- DATE RANGES ---
    max_date = ebay_metadata["date"].max()
    date_ranges = {
        "All Time": ebay_metadata,
        "Last 90 Days": ebay_metadata[ebay_metadata["date"] >= max_date - pd.Timedelta(days=90)],
        "Last 30 Days": ebay_metadata[ebay_metadata["date"] >= max_date - pd.Timedelta(days=30)],
        "Last 15 Days": ebay_metadata[ebay_metadata["date"] >= max_date - pd.Timedelta(days=15)],
        "Last 7 Days": ebay_metadata[ebay_metadata["date"] >= max_date - pd.Timedelta(days=7)],
    }

    tables = []
    numeric_tables = []

    for label, df_range in date_ranges.items():
        # Group by setName
        grouped = (
            df_range.groupby("setName")
            .agg(
                avg_market_price=(price_col, "mean"),
                totalSetNumber=("totalSetNumber", "mean")
            )
            .reset_index()
            .sort_values(by="avg_market_price", ascending=False)
        )
        grouped.insert(0, "Rank", range(1, len(grouped) + 1))

        # Compute change vs previous table
        if numeric_tables:
            prev = numeric_tables[-1][["setName", "avg_market_price"]].rename(
                columns={"avg_market_price": "prev_price"}
            )
            merged = grouped.merge(prev, on="setName", how="left")
            merged["Change"] = merged["avg_market_price"] - merged["prev_price"]
            merged["% Change"] = (merged["Change"] / merged["prev_price"]) * 100
        else:
            merged = grouped.copy()
            merged["Change"] = 0
            merged["% Change"] = 0

        # Save numeric version
        numeric_tables.append(merged.copy())

        # Format for display
        merged["Change"] = merged["Change"].fillna(0).round(2)
        merged["% Change"] = merged["% Change"].fillna(0).round(2)
        merged["avg_market_price"] = merged["avg_market_price"].apply(lambda x: f"${x:,.2f}")
        merged["totalSetNumber"] = merged["totalSetNumber"].round(0).astype(int)

        tables.append(merged)

    # --- Create Plotly Figure ---
    fig = go.Figure()

    for i, (label, table) in enumerate(tables):
        # Color coding for Change and % Change
        change_colors = ["#00CC96" if x > 0 else "#EF553B" if x < 0 else "black" for x in table["Change"]]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["Rank", "Set Name", "Avg. Market Price ($)", "Total Cards in Set", "Change", "% Change"],
                    fill_color="#636EFA",
                    align="center",
                    font=dict(color="white", size=13)
                ),
                cells=dict(
                    values=[
                        table["Rank"],
                        table["setName"],
                        table["avg_market_price"],
                        table["totalSetNumber"],
                        [f"{x:+.2f}" for x in table["Change"]],
                        [f"{x:+.2f}%" for x in table["% Change"]],
                    ],
                    fill_color="white",
                    align="center",
                    font=dict(size=12),
                    font_color=[
                        "black", "black", "black", "black", change_colors, change_colors
                    ],
                ),
                visible=(label == "All Time")
            )
        )

    # --- Dropdown Menu ---
    buttons = [
        dict(
            label=label,
            method="update",
            args=[
                {"visible": [j == i for j in range(len(tables))]},
                {"title": f"Top Pokémon Card Sets — {label}"}
            ],
        )
        for i, label in enumerate(date_ranges.keys())
    ]

    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            x=1.15,
            y=1.05,
            showactive=True
        )],
        title={"text": "Top Pokémon Card Sets — All Time", "x": 0.5},
    )

    return fig


#========================================== PORTFOLIO VIEW ===================================================
# ------------------- FUNCTION 2: Portfolio Performance Line Chart --------------
def portfolio_view_performance_line_chart(ids:list, days:int=1):
    portfolio_ids = ids
    portfolio_history = price_history_metadata[price_history_metadata['id'].isin(portfolio_ids)].copy()

    portfolio_history['date'] = pd.to_datetime(portfolio_history['date'])

    portfolio_daily_value = (
        portfolio_history.groupby('date')['average']
        .sum()
        .reset_index()
        .sort_values('date')
    )

    portfolio_daily_value.rename(columns={'average': 'total_value'}, inplace=True)

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
def portfolio_view_collection_pie_chart(ids:list, days:int=1):
    portfolio_ids = ids

    portfolio_breakdown_df = portfolio_sample_df.groupby('setName')['id'].nunique().reset_index()
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

    return fig


#========================================== CARD VIEW ===================================================
# ------------------------ FUNCTION 4: Price History Line Chart  -----------
# Convert date columns to datetime
ebay_metadata["date"] = pd.to_datetime(ebay_metadata["date"], errors="coerce")
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
}

# ---------------------------- Function ----------------------------
def card_view_price_history_line_chart(card_id, card_name):
    """
    Shows TCGplayer vs eBay price history for a single card as a line chart
    with a date dropdown filter and range slider.
    """

    card_df = all_prices[all_prices["id"] == card_id].copy()

    if card_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No price history available for {card_name}",
            template="plotly_white"
        )
        return fig

    card_df = card_df.sort_values("date")

    # Initialize traces
    traces = []
    if "ebay_price" in card_df.columns and card_df["ebay_price"].notna().any():
        traces.append(go.Scatter(
            x=card_df["date"],
            y=card_df["ebay_price"],
            mode="lines",
            name="eBay",
            line=dict(width=2)
        ))
    if "tcg_price" in card_df.columns and card_df["tcg_price"].notna().any():
        traces.append(go.Scatter(
            x=card_df["date"],
            y=card_df["tcg_price"],
            mode="lines",
            name="TCGplayer (Near Mint)",
            line=dict(width=2, dash="dash")
        ))

    fig = go.Figure(traces)

    # ---------------- Dropdown Buttons ----------------
    buttons = []
    for label, df in date_ranges.items():
        card_specific = df[df["id"] == card_id]

        ebay_y = card_specific["ebay_price"] if "ebay_price" in card_specific.columns else [None]*len(card_specific)
        tcg_y = card_specific["tcg_price"] if "tcg_price" in card_specific.columns else [None]*len(card_specific)

        y_data = []
        if any(traces[i].name == "eBay" for i in range(len(traces))):
            y_data.append(ebay_y)
        if any(traces[i].name == "TCGplayer (Near Mint)" for i in range(len(traces))):
            y_data.append(tcg_y)

        buttons.append(dict(
            label=label,
            method="update",
            args=[{"x": [card_specific["date"]]*len(y_data), "y": y_data}]
        ))

    fig.update_layout(
        title=f"Price History – {card_name}",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        hovermode="x unified",
        height=450,
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.0,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )],
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(count=30, label="30d", step="day", stepmode="backward"),
                    dict(count=90, label="90d", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig

# ----------------- FUNCTION 5: Grade Price Comparison  -----------
def card_view_card_grade_price_comparison(card_name, grading_cost=20):
    # -------------------- Filter Data --------------------
    graded_data = ebay_metadata[ebay_metadata['name'].str.contains(card_name, case=False, na=False)].copy()
    ungraded_data = price_history_metadata[price_history_metadata['name'].str.contains(card_name, case=False, na=False)].copy()

    if len(graded_data) == 0:
        print(f"No graded data found for: {card_name}")
        return

    graded_data['psa_grade_numeric'] = graded_data['grade'].str.extract(r'psa(\d+)', expand=False).astype(float)
    graded_data = graded_data[graded_data['psa_grade_numeric'].isin([8.0, 9.0, 10.0])]

    if len(ungraded_data) == 0:
        ungraded_avg_price = graded_data['average'].iloc[0]
        ungraded_sales_count = 0
    else:
        ungraded_avg_price = ungraded_data['market'].mean()
        ungraded_sales_count = len(ungraded_data)

    # -------------------- Prepare Data --------------------
    # Sales Volume
    grade_counts = graded_data['psa_grade_numeric'].value_counts().sort_index()
    categories_volume = ['Ungraded\n(Near Mint)'] + [f'PSA {int(g)}' for g in grade_counts.index]
    counts = [max(ungraded_sales_count, 1)] + grade_counts.tolist()
    colors = ['#95a5a6', '#3498db', '#2ecc71', '#f39c12']

    # Price
    price_by_grade = graded_data.groupby('psa_grade_numeric')['average'].mean().sort_index()
    categories_price = ['Ungraded\n(Near Mint)'] + [f'PSA {int(g)}' for g in price_by_grade.index]
    prices = [ungraded_avg_price] + price_by_grade.tolist()

    # -------------------- Create Subplots --------------------
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Sales Volume", "Average Price (USD)"))

    # Sales Volume Bar Chart
    fig.add_trace(go.Bar(
        x=categories_volume,
        y=counts,
        marker_color=colors[:len(counts)],
        text=counts,
        textposition='outside',
        name='Sales Volume'
    ), row=1, col=1)

    # Price Bar Chart
    fig.add_trace(go.Bar(
        x=categories_price,
        y=prices,
        marker_color=colors[:len(prices)],
        text=[f"${p:.2f}" for p in prices],
        textposition='outside',
        name='Average Price'
    ), row=1, col=2)

    # -------------------- ROI Annotation for PSA 10 --------------------
    if 10.0 in price_by_grade.index:
        psa10_price = price_by_grade[10.0]
        roi = psa10_price - ungraded_avg_price - grading_cost
        roi_pct = (roi / (ungraded_avg_price + grading_cost)) * 100
        verdict = "✓ WORTH GRADING" if roi > 0 else "✗ NOT WORTH GRADING"
        color = 'green' if roi > 0 else 'red'

        fig.add_annotation(
            x=0.75,  # position relative to the figure (right chart)
            y=-0.15,
            xref='paper',
            yref='paper',
            text=f"PSA 10 ROI: ${roi:.2f} ({roi_pct:+.0f}%) | {verdict}",
            showarrow=False,
            font=dict(size=12, color=color),
            align='center',
            bordercolor=color,
            borderwidth=1,
            borderpad=4,
            bgcolor='wheat',
            opacity=0.7
        )

    fig.update_layout(
        title_text=f"Graded vs Ungraded Analysis: {card_name}",
        height=600,
        template='plotly_white',
        showlegend=False
    )

    fig.show()

    return graded_data, ungraded_data
'''
# -------------------- CALL FUNCTION --------------------
graded_data, ungraded_data = portfolio_view_graded_ungraded_plotly("Zekrom ex - 172/086")
'''