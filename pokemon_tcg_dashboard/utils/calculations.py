import pandas as pd

#from global_variables import CARD_METADATA_DF, PRICE_HISTORY_DF, EBAY_METADATA_DF
import logging
logger = logging.getLogger(__name__)

def calculate_cat_vol_price(price_history_df, ebay_history_df, card_id):
    graded_data = ebay_history_df[ebay_history_df['tcgPlayerId'] == card_id].copy()
    ungraded_data = price_history_df[price_history_df['tcgPlayerId'] == card_id].copy()

    if graded_data.empty or ungraded_data.empty:
        return None

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

    # Price
    price_by_grade = graded_data.groupby('psa_grade_numeric')['average'].mean().sort_index()
    categories_price = ['Ungraded'] + [f'PSA {int(g)}' for g in price_by_grade.index]
    prices = [ungraded_avg_price] + price_by_grade.tolist()

    return (categories_volume, counts), (categories_price, prices)

def calculate_roi(price_history_df, ebay_history_df, card_id, grading_cost=27.99):
    logging.debug("calculate_roi called")
    graded_data = ebay_history_df[ebay_history_df['tcgPlayerId'] == card_id].copy()
    ungraded_data = price_history_df[price_history_df['tcgPlayerId'] == card_id].copy()

    if not graded_data.empty or not ungraded_data.empty:

        graded_data['psa_grade_numeric'] = (
            graded_data['grade'].str.extract(r'psa(\d+)', expand=False).astype(float)
        )
        graded_data = graded_data[graded_data['psa_grade_numeric'].isin([8.0, 9.0, 10.0])]

        if ungraded_data.empty:
            ungraded_avg_price = graded_data['average'].iloc[0] if 'average' in graded_data.columns else 0
        else:
            ungraded_avg_price = ungraded_data['market'].mean() if 'market' in ungraded_data.columns else 0

        price_by_grade = graded_data.groupby('psa_grade_numeric')['average'].mean().sort_index()
        

    result = []

    for grade in [8.0, 9.0, 10.0]:
        if grade in price_by_grade.index:

            psa_price = price_by_grade[grade]
            roi = psa_price - ungraded_avg_price - grading_cost - ungraded_avg_price * 0.1
            roi_pct = (roi / (ungraded_avg_price + grading_cost)) * 100
            verdict = "✓ WORTH GRADING" if roi > 0 else "✗ NOT WORTH GRADING"
            verdict_color = "success" if roi > 0 else "danger"

            content = (
                f"PSA {int(grade)} ROI: ${roi:.2f} "
                f"({roi_pct:+.0f}%)\n"
                f"{verdict}"
            )

        else:
            # No graded market data for this grade
            content = f"No graded sales exist for PSA {int(grade)}"
            verdict_color = "secondary"

        result.append({
            'content': content,
            'color': verdict_color,
            'grade': int(grade)
        })

    return result
