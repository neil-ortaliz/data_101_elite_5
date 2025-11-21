'''
MEMBER 3 TASK LIST:

✅ Task 1: Set Performance Bar Chart (market_view_set_performance_bar_chart) - A horizontal bar chart showing value change for each Pokemon set.
Should show % gain/loss with color coding (green=profit, red=loss).
✅ Task 2: Portfolio Performance Line Chart (portfolio_view_performance_line_chart) - Multi-line chart showing portfolio value over time.
Should show total value + individual set contributions.
✅ Task 3: Collection Breakdown Pie Chart (portfolio_view_collection_pie_chart) - Pie chart showing portfolio composition by Pokemon set.
Should show percentage and value for each set.
🟨 Task 4: Price History Line Chart 
🟨 Task 5: Grade Price Comparison Chart
□ Task 6: Chart Optimization
'''
'''
Notes:
- Time range of set performance - add date filtering 
'''
'''
Nov 19, 2025
Main charts work as intended (tested in colab), but I need help for the following:
- Ensuring that the merged datasets/dataframes I'm using are correct.
- How to integrate data from Member 2 to the functions.

I just have some simple questions:
- Can I commit in Develop branch even though the charts aren't perfect yet?
- Do we use the sample_portfolio data for testing the charts for the portfolio view?
Neil: Paramaters just accept one df, mention 
'''
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import timedelta

# ----------------------------- Call data -------------------------------------
market_ebay_data = 'data/ebay_price_history.csv'
market_metadata = 'data/cards_metadata_table.csv'
market_price_history = 'data/price_history.csv'
portfolio_sample_data = 'data/portfolio_cards_metadata_table.csv'

ebay_df = pd.read_csv(market_ebay_data)
metadata_df = pd.read_csv(market_metadata)
price_history_df = pd.read_csv(market_price_history)
portfolio_sample_df = pd.read_csv(portfolio_sample_data)

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

# All three combined (DO I need this??)
market_df = ebay_metadata.merge(
    price_history_metadata[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
    on=['id'],
    how='left',
)
market_df = market_df.dropna(subset='setName')

# Date Format
ebay_metadata['date'] = pd.to_datetime(ebay_metadata['date'])
price_history_metadata['date'] = pd.to_datetime(price_history_metadata['date'])
market_df['date'] = pd.to_datetime(market_df['date'])

# ------------------------------- Computing Change in Price (codes from Phase 2) -------------------------
ebay_metadata = ebay_metadata.sort_values(by=['setName', 'date'])

# Group by set/day and compute average price per setName per day
set_daily = (
    ebay_metadata.groupby(['setName', 'date'])['average']
    .mean()
    .reset_index()
    .sort_values(by=['setName', 'date'])
)

set_daily['prev_price'] = set_daily.groupby('setName')['average'].shift(1)
set_daily['price_change'] = set_daily['average'] - set_daily['prev_price']
set_daily['pct_change'] = (set_daily['price_change'] / set_daily['prev_price']) * 100
set_daily['pct_change'] = set_daily['pct_change'].fillna(0)

latest_set_prices = (
    set_daily.sort_values('date')
             .groupby('setName')
             .tail(1)
             .reset_index(drop=True)
)

latest_set_prices = latest_set_prices[['setName', 'pct_change']]
latest_set_prices = latest_set_prices.rename(columns={'pct_change': 'value_change_pct'})

# -------------------------------- TABLE FORM -------------------------------------

# prices.market -> float
metadata_df["prices.market"] = pd.to_numeric(metadata_df["prices.market"], errors="coerce")

# Group by setName
top_sets = (
    metadata_df.groupby("setName")
    .agg(
        avg_market_price=("prices.market", "mean"),
        totalSetNumber=("totalSetNumber", "mean")
    )
    .reset_index()
    .sort_values(by="avg_market_price", ascending=False)
)

# Ensure numeric eBay values
ebay_metadata["average"] = pd.to_numeric(ebay_metadata["average"], errors="coerce")
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

# --- CREATE TABLES ---
tables = []
numeric_tables = []  # store numeric (non-formatted) versions for % change comparisons

for label, df_range in date_ranges.items():

    grouped = (
        df_range.groupby("setName")
        .agg(
            avg_market_price=("average", "mean"),
            totalSetNumber=("totalSetNumber", "mean")
        )
        .reset_index()
        .sort_values(by="avg_market_price", ascending=False)
    )

    grouped.insert(0, "Rank", range(1, len(grouped) + 1))

    # Compute change vs previous table (store numeric versions)
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

    # Save numeric table BEFORE formatting
    numeric_tables.append(merged.copy())

    # Format output table
    merged["Change"] = merged["Change"].fillna(0).round(2)
    merged["% Change"] = merged["% Change"].fillna(0).round(2)
    merged["avg_market_price"] = merged["avg_market_price"].apply(lambda x: f"${x:,.2f}")
    merged["totalSetNumber"] = merged["totalSetNumber"].round(0).astype(int)

    tables.append(merged)

# --- PLOTLY TABLE ---
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

# --- DROPDOWN MENU ---
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
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            x=1.15,
            y=1.05,
            showactive=True
        )
    ],
    title={"text": "Top Pokémon Card Sets — All Time", "x": 0.5},
)

fig.show()


# ------------------------ FUNCTION 1: Set Performance Bar Chart ----------------
def market_view_set_performance_bar_chart(time_range="Most Recent Change"):
    sorted_data = latest_set_prices.sort_values('value_change_pct')
    colors = ['#22c55e' if x >= 0 else '#ef4444' for x in sorted_data['value_change_pct']]

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

# ------------------- FUNCTION 2: Portfolio Performance Line Chart --------------
def portfolio_view_performance_line_chart():
    portfolio_ids = set(portfolio_sample_df['id'])
    portfolio_history = market_df[market_df['id'].isin(portfolio_ids)].copy()

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
def portfolio_view_collection_pie_chart():
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

# ------------------------ FUNCTION 4: Price History Line Chart  -----------

# Convert date fields to datetime and remove timezone safely
ebay_data["date"] = pd.to_datetime(ebay_data["date"], errors="coerce")
price_history_data["date"] = pd.to_datetime(price_history_data["date"], errors="coerce")

# Remove timezone (handles UTC timestamps)
if ebay_data["date"].dt.tz is not None:
    ebay_data["date"] = ebay_data["date"].dt.tz_localize(None)

if price_history_data["date"].dt.tz is not None:
    price_history_data["date"] = price_history_data["date"].dt.tz_localize(None)

# ------------------------- FILTER PRICE HISTORY ------------------------------
# Only Near Mint records for TCGplayer (for clean comparison)
price_history_nm = price_h[
    price_history_data["condition"] == "Near Mint"
].copy()

# ------------------------- MERGE WITH METADATA -------------------------------
ebay_merged = ebay_data.merge(
    meta_data[["id", "name", "setName"]],
    on="id",
    how="left"
)

tcg_merged = price_history_nm.merge(
    meta_data[["id", "name", "setName"]],
    on="id",
    how="left"
)

# Rename price columns for clarity
ebay_merged = ebay_merged.rename(columns={"average": "ebay_price"})
tcg_merged = tcg_merged.rename(columns={"market": "tcg_price"})

# ------------------------- MERGE PRICE SOURCES -------------------------------
all_prices = pd.merge(
    ebay_merged[["id", "date", "ebay_price"]],
    tcg_merged[["id", "date", "tcg_price"]],
    on=["id", "date"],
    how="outer"  # keep all records from both datasets
)

def card_view_price_history_line_chart(card_id, card_name):
    """
    Shows TCGplayer vs eBay price history for a single card.
    """

    card_df = all_prices[all_prices["id"] == card_id].copy()

    if card_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No price history available for {card_name}",
            template="plotly_white"
        )
        return fig

    fig = go.Figure()

    # Line: eBay
    if "ebay_price" in card_df.columns:
        fig.add_trace(go.Scatter(
            x=card_df["date"],
            y=card_df["ebay_price"],
            mode="lines",
            name="eBay",
            line=dict(width=2)
        ))

    # Line: TCGplayer
    if "tcg_price" in card_df.columns:
        fig.add_trace(go.Scatter(
            x=card_df["date"],
            y=card_df["tcg_price"],
            mode="lines",
            name="TCGplayer",
            line=dict(width=2, dash="dash")
        ))

    fig.update_layout(
        title=f"Price History – {card_name}",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        hovermode="x unified",
        height=450
    )

    return fig

'''
# -------------------- CALL FUNCTION --------------------
card_id = '68af6bbbd14a00763202573c'
card_name = 'Zekrom ex - 172/086"'

fig = card_view_price_history_line_chart(card_id, card_name)
fig.show()
'''
# ----------------- FUNCTION 5: Grade Price Comparison  -----------
def card_view_grade_price_bar_chart():

    graded_data = graded_merged[graded_merged['name'] == card_name].copy()
    ungraded_data = ungraded_merged[ungraded_merged['name'] == card_name].copy()

    if len(graded_data) == 0:
        print(f"No graded data found for: {card_name}")
        return

    # Ungraded average price
    if len(ungraded_data) == 0:
        ungraded_avg_price = graded_data['prices.market'].iloc[0]
        ungraded_sales_count = 0
    else:
        ungraded_avg_price = ungraded_data['market'].mean()
        ungraded_sales_count = len(ungraded_data)

    grades_sorted = [8, 9, 10]
    grade_counts = graded_data['psa_grade'].value_counts().sort_index()
    price_by_grade = graded_data.groupby('psa_grade')['average'].mean().sort_index()

    sales_categories = ['Ungraded\n(Near Mint)'] + [f'PSA {g}' for g in grades_sorted]
    sales_counts = [max(ungraded_sales_count, 1)] + [grade_counts.get(g, 0) for g in grades_sorted]

    price_categories = ['Ungraded\n(Near Mint)'] + [f'PSA {g}' for g in grades_sorted]
    prices = [ungraded_avg_price] + [price_by_grade.get(g, 0) for g in grades_sorted]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"Sales Volume: {card_name}", f"Price Comparison: {card_name}")
    )

    colors = ['#95a5a6', '#3498db', '#2ecc71', '#f39c12']

    # Sales volume bar
    fig.add_trace(go.Bar(x=sales_categories, y=sales_counts, marker_color=colors[:len(sales_counts)],
                         text=sales_counts, textposition='outside', name='Sales Volume'), row=1, col=1)

    # Price comparison bar
    fig.add_trace(go.Bar(x=price_categories, y=prices, marker_color=colors[:len(prices)],
                         text=[f"${p:.2f}" for p in prices], textposition='outside', name='Price'),
                  row=1, col=2)

    # ROI calculation for PSA 10
    psa10_price = price_by_grade.get(10, None)
    if psa10_price:
        roi = psa10_price - ungraded_avg_price - grading_cost
        roi_pct = (roi / (ungraded_avg_price + grading_cost)) * 100
        verdict = "✓ WORTH GRADING" if roi > 0 else "✗ NOT WORTH GRADING"
        roi_text = f"PSA 10 ROI: ${roi:.2f} ({roi_pct:+.0f}%) | {verdict}"

        # Add annotation box at bottom right of price chart
        fig.add_annotation(
            x=1, y=-0.25, text=roi_text, showarrow=False,
            xref='x2 domain', yref='y2 domain',
            font=dict(size=12, color='green' if roi > 0 else 'red', family='Arial', weight='bold'),
            align='right', bordercolor='green' if roi > 0 else 'red', borderwidth=1,
            bgcolor='white', opacity=0.8
        )

    fig.update_layout(
        height=500,
        width=1000,
        showlegend=False,
        template='plotly_white',
        title_text=f"Graded vs Ungraded Analysis: {card_name}"
    )

    fig.show()
    return graded_data, ungraded_data, fig
'''
# -------------------- CALL FUNCTION --------------------
card_name = 'Zekrom ex - 172/086'
graded, ungraded, fig = function5(card_name, grading_cost=20)
'''