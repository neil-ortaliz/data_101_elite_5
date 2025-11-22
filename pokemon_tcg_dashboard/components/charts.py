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
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent     # project root
DATA_DIR = BASE_DIR / "data"

# ----------------------------- Call data -------------------------------------
market_ebay_data = BASE_DIR/'data/ebay_price_history.csv'
market_metadata = BASE_DIR/'data/cards_metadata_table.csv'
market_price_history = BASE_DIR/'data/price_history.csv'
portfolio_sample_data = BASE_DIR/'data/sample_portfolio_cards_metadata_table.csv'

ebay_df = pd.read_csv(market_ebay_data)
metadata_df = pd.read_csv(market_metadata)
price_history_df = pd.read_csv(market_price_history)
portfolio_sample_df = pd.read_csv(portfolio_sample_data)

# ------------------------------ Merge Data --------------------------------------
'''
1. Ebay Price History + Metadata
2. Price History + Metadata
3. All three combined
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

# All three combined
market_df = ebay_metadata.merge(
    price_history_metadata[["id", "setId", "setName", "totalSetNumber", "updatedAt"]],
    on=['id'],
    how='left',
)

#print(f"market_df columns: {market_df.columns}")

market_df = market_df.dropna(subset='setName_x')

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


# ------------------------ FUNCTION 5: Grade Price Comparison  -----------
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