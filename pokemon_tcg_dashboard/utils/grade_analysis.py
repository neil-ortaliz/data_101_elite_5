# Task 5 - Grade Distribution Visualization

import pandas as pd
import plotly.graph_objects as go
from typing import Optional


def create_grade_distribution_chart(data: pd.DataFrame, card_id=None, card_name=None) -> go.Figure:
    """
    Create bar chart showing grade distribution with one bar per grade.

    Parameters
    ----------
    data : pd.DataFrame
        Must contain columns ['grade', 'count'] or ['grade', 'percentage'].
    card_id : int, optional
        ID to filter data.
    card_name : str, optional
        Card name for chart title.

    Returns
    -------
    go.Figure
    """

    # canonical ordered grades
    grade_order = ['PSA 8', 'PSA 9', 'PSA 10']

    # Filter by card_id if available
    if card_id is not None and 'tcgPlayerId' in data.columns:
        data = data[data['tcgPlayerId'] == card_id]

    # Standardize grade names
    data['grade'] = data['grade'].str.upper().str.replace('PSA', 'PSA ')

    # Aggregate counts per grade
    grade_counts = data.groupby('grade')['count'].sum().reindex(grade_order, fill_value=0)
    grade_data = grade_counts.reset_index().rename(columns={'count': 'count'})

    total = grade_data['count'].sum()
    if total == 0:
        fig = go.Figure()
        fig.update_layout(
            title=f"No graded price history available for {card_name}",
            template="plotly_white"
        )
        return fig

    grade_data['percentage'] = (grade_data['count'] / total) * 100

    # Color map
    color_map = {
        'PSA 8': '#9b59b6',  # Blue
        'PSA 9': '#f1c40f',  # Green
        'PSA 10': '#2ecc71'  # Purple
    }

    # Create separate bar per grade
    fig = go.Figure()
    for _, row in grade_data.iterrows():
        fig.add_trace(go.Bar(
            x=[row['grade']],
            y=[row['percentage']],
            text=f"{row['count']} cards<br>{row['percentage']:.1f}%",
            textposition='auto',
            marker_color=color_map.get(row['grade'], None),
            hovertemplate=(
                f"<b>{row['grade']}</b><br>"
                f"Count: {row['count']}<br>"
                f"Percentage: {row['percentage']:.1f}%<extra></extra>"
            )
        ))

    # Layout
    fig.update_layout(
        title=f"Grade Distribution for {card_name}",
        xaxis_title="Grade",
        yaxis_title="Percentage (%)",
        yaxis=dict(range=[0, 100], ticksuffix='%'),
        template='plotly_white',
        showlegend=False,
        height=400
    )

    return fig


# Task 6 - Grade Statistics

import pandas as pd
from typing import Dict, Any

def calculate_grade_statistics(graded_sales: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate statistics about card grading distribution.

    Parameters
    ----------
    graded_sales : pd.DataFrame
        Expected columns: ['card_id', 'grade', 'sale_price', 'sale_date']
        - 'grade' should be one of: 'Raw', 'PSA 1-7', 'PSA 8', 'PSA 9', 'PSA 10'
          (or a subset; missing ones will be treated as 0)
        - 'sale_price' will be coerced to numeric.

    Returns
    -------
    dict
        {
          'grade_counts': {grade: count, ...},
          'grade_percentages': {grade: pct, ...},
          'total_graded': int,
          'psa10_rarity': float,       # PSA 10 percentage (0–100)
          'rarity_label': str,         # Common / Uncommon / Rare / Very Rare / No Data
          'average_grade': float,      # numeric average (0–10 scale)
          'psa10_premium_pct': float   # % premium of PSA10 vs Raw (0 if not computable)
        }
    """
    # Defensive copy
    df = graded_sales.copy()

    # Handle empty input early
    if df.empty:
        return {
            "grade_counts": {g: 0 for g in ['Raw', 'PSA 1-7', 'PSA 8', 'PSA 9', 'PSA 10']},
            "grade_percentages": {g: 0.0 for g in ['Raw', 'PSA 1-7', 'PSA 8', 'PSA 9', 'PSA 10']},
            "total_graded": 0,
            "psa10_rarity": 0.0,
            "rarity_label": "No Data",
            "average_grade": 0.0,
            "psa10_premium_pct": 0.0,
        }

    # Ensure expected columns are present
    if "grade" not in df.columns:
        raise KeyError("graded_sales must contain a 'grade' column")
    if "sale_price" not in df.columns:
        raise KeyError("graded_sales must contain a 'sale_price' column")

    # Coerce sale_price to numeric (drop or coerce invalid)
    df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")

    # Count by grade
    grade_counts_raw = df["grade"].value_counts()
    total_graded = int(len(df))

    # Canonical grade order / buckets
    grade_labels = ['Raw', 'PSA 1-7', 'PSA 8', 'PSA 9', 'PSA 10']

    # Build distribution dicts, ensuring all buckets exist
    grade_counts: Dict[str, int] = {
        grade: int(grade_counts_raw.get(grade, 0)) for grade in grade_labels
    }

    if total_graded > 0:
        grade_percentages: Dict[str, float] = {
            grade: (count / total_graded) * 100.0
            for grade, count in grade_counts.items()
        }
    else:
        grade_percentages = {grade: 0.0 for grade in grade_labels}

    # PSA 10 rarity (percentage)
    psa10_rarity = float(grade_percentages.get("PSA 10", 0.0))

    # Rarity label
    if total_graded == 0 or grade_counts.get("PSA 10", 0) == 0:
        rarity_label = "No Data"
    elif psa10_rarity > 20:
        rarity_label = "Common"
    elif psa10_rarity > 10:
        rarity_label = "Uncommon"
    elif psa10_rarity > 5:
        rarity_label = "Rare"
    else:
        rarity_label = "Very Rare"

    # Average grade (numeric)
    grade_numeric = {
        "Raw": 0,
        "PSA 1-7": 5,   # mid-point of 1–7-ish bucket
        "PSA 8": 8,
        "PSA 9": 9,
        "PSA 10": 10,
    }

    weighted_sum = 0.0
    for grade, numeric in grade_numeric.items():
        weighted_sum += grade_counts.get(grade, 0) * numeric

    average_grade = float(weighted_sum / total_graded) if total_graded > 0 else 0.0

    # Value premium for PSA 10 vs Raw
    # Use mean of sale_price by grade
    avg_price_by_grade = df.groupby("grade")["sale_price"].mean()

    raw_price = float(avg_price_by_grade.get("Raw", 0.0) or 0.0)
    psa10_price = float(avg_price_by_grade.get("PSA 10", 0.0) or 0.0)

    if raw_price > 0 and psa10_price > 0:
        psa10_premium_pct = ((psa10_price - raw_price) / raw_price) * 100.0
    else:
        psa10_premium_pct = 0.0

    return {
        "grade_counts": grade_counts,
        "grade_percentages": grade_percentages,
        "total_graded": total_graded,
        "psa10_rarity": psa10_rarity,
        "rarity_label": rarity_label,
        "average_grade": average_grade,
        "psa10_premium_pct": psa10_premium_pct,
    }

if __name__ == "__main__":
    ebay_price_history_df: pd.DataFrame = pd.read_csv(
        "pokemon_tcg_dashboard/data/ebay_price_history.csv",
        parse_dates=["date"]
    )

    create_grade_distribution_chart(data = ebay_price_history_df)
