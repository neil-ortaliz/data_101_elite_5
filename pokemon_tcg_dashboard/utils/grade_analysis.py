# Task 5 - Grade Distribution Visualization

import pandas as pd
import plotly.graph_objects as go
from typing import Optional

def create_grade_distribution_chart(grade_data: pd.DataFrame, card_name: Optional[str] = None) -> go.Figure:
    """
    Create stacked bar chart showing grade distribution.

    Parameters
    ----------
    grade_data : pd.DataFrame
        Must contain either:
          - columns ['grade', 'count']  OR
          - columns ['grade', 'count', 'percentage']
        'grade' values should match one of the expected grade categories (see grade_order).
    card_name : Optional[str]
        Card name for title (when showing a single card). If None, chart shows overall distribution.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    # canonical ordered grades (adjust if you have more granular levels)
    grade_order = ['Raw', 'PSA 1-7', 'PSA 8', 'PSA 9', 'PSA 10']

    # defensive copy
    df = grade_data.copy()

    # Normalize column names (accept common variants)
    if 'count' not in df.columns and 'counts' in df.columns:
        df = df.rename(columns={'counts': 'count'})
    if 'grade' not in df.columns:
        raise KeyError("grade_data must contain a 'grade' column")

    # If only counts provided, compute percentages. If percentages provided, prefer them but still normalize.
    if 'count' in df.columns:
        total = df['count'].sum()
        # avoid division by zero
        if total == 0:
            # just create zeroed percentages for all categories
            df['percentage'] = 0.0
        else:
            df['percentage'] = (df['count'] / total) * 100.0
    elif 'percentage' in df.columns:
        # ensure percentages numeric and normalized to sum 100
        df['percentage'] = pd.to_numeric(df['percentage'], errors='coerce').fillna(0.0)
        pct_total = df['percentage'].sum()
        if pct_total == 0:
            # nothing: treat as zeros
            pass
        else:
            # normalize so stacked bars sum to 100
            df['percentage'] = (df['percentage'] / pct_total) * 100.0
        # set count column to None (not available)
        df['count'] = None
    else:
        raise KeyError("grade_data must contain either 'count' or 'percentage' column")

    # Ensure every expected grade appears (fill missing with zeros)
    grades_df = pd.DataFrame({'grade': grade_order})
    df = grades_df.merge(df[['grade', 'count', 'percentage']], on='grade', how='left').fillna({'count': 0, 'percentage': 0.0})

    # Ensure proper ordering
    df['grade'] = pd.Categorical(df['grade'], categories=grade_order, ordered=True)
    df = df.sort_values('grade')

    # color map
    color_map = {
        'Raw': '#6b7280',    # Gray
        'PSA 1-7': '#f59e0b',# Orange
        'PSA 8': '#3b82f6',  # Blue
        'PSA 9': '#10b981',  # Green
        'PSA 10': '#8b5cf6'  # Purple
    }

    # Build stacked bar (single stacked bar)
    x_label = card_name if card_name else 'Distribution'
    fig = go.Figure()
    for _, row in df.iterrows():
        grade = row['grade']
        pct = float(row['percentage'])
        cnt = int(row['count']) if pd.notna(row['count']) else None

        # show zero slices too (so legend shows all grades)
        fig.add_trace(go.Bar(
            name=str(grade),
            x=[x_label],
            y=[pct],
            text=f"{cnt} cards<br>{pct:.1f}%" if cnt is not None else f"{pct:.1f}%",
            textposition='inside',
            marker_color=color_map.get(grade, None),
            hovertemplate=(
                f"<b>{grade}</b><br>" +
                (f"Count: {cnt}<br>" if cnt is not None else "") +
                f"Percentage: {pct:.1f}%<extra></extra>"
            )
        ))

    # Ensure stacked bars sum to ~100 (floating artifacts possible)
    # Layout
    title = f"Grade Distribution — {card_name}" if card_name else "Overall Grade Distribution"
    fig.update_layout(
        title=title,
        barmode='stack',
        height=360,
        showlegend=True,
        xaxis_title='',
        yaxis_title='Percentage (%)',
        yaxis=dict(range=[0, 100], ticksuffix='%'),
        template='plotly_white',
        legend=dict(title='Grade')
    )

    # Improve text visibility when some slices are small
    fig.update_traces(insidetextanchor='middle', cliponaxis=False)

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
