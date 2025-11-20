"""
Money waster detection and analysis
"""

import pandas as pd
import logging
from typing import List

logger = logging.getLogger(__name__)


def identify_money_wasters(
    df: pd.DataFrame,
    cost_threshold_percentile: int = 75,
    cvr_threshold_percentile: int = 25
) -> pd.DataFrame:
    """
    Identify high-cost, low-conversion n-grams (money wasters)

    Money wasters are n-grams that:
    1. Have cost above the specified percentile (default: 75th)
    2. Have CVR below the specified percentile (default: 25th)

    Args:
        df: DataFrame with n-gram analysis results
        cost_threshold_percentile: Percentile for high cost threshold (50-95)
        cvr_threshold_percentile: Percentile for low CVR threshold (5-50)

    Returns:
        DataFrame of money wasters sorted by waste_score (descending)

    Notes:
        Waste score is calculated as: (normalized_cost) * (1 - cvr/100)
        Higher scores indicate more wasteful n-grams
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to money waster detection")
        return df

    logger.info(
        f"Identifying money wasters (cost>{cost_threshold_percentile}th, "
        f"cvr<{cvr_threshold_percentile}th percentile)"
    )

    # Calculate thresholds
    cost_threshold = df['total_cost'].quantile(cost_threshold_percentile / 100)
    cvr_threshold = df['cvr'].quantile(cvr_threshold_percentile / 100)

    logger.debug(f"Cost threshold: £{cost_threshold:.2f}, CVR threshold: {cvr_threshold:.2f}%")

    # Filter for money wasters
    money_wasters = df[
        (df['total_cost'] >= cost_threshold) &
        (df['cvr'] <= cvr_threshold)
    ].copy()

    if money_wasters.empty:
        logger.info("No money wasters found with current thresholds")
        return money_wasters

    # Calculate waste score
    max_cost = money_wasters['total_cost'].max()
    money_wasters['waste_score'] = (
        (money_wasters['total_cost'] / max_cost) *
        (1 - money_wasters['cvr'] / 100)
    )

    # Sort by waste score
    money_wasters = money_wasters.sort_values('waste_score', ascending=False)

    logger.info(f"Found {len(money_wasters)} money wasters")

    return money_wasters


def generate_negative_keywords(
    money_wasters: pd.DataFrame,
    min_waste_score: float = 0.5,
    max_results: int = 100
) -> List[str]:
    """
    Generate negative keyword suggestions from money wasters

    Args:
        money_wasters: DataFrame from identify_money_wasters()
        min_waste_score: Minimum waste score to include (0.0-1.0)
        max_results: Maximum number of negative keywords to return

    Returns:
        List of n-gram strings sorted by waste score
    """
    if money_wasters.empty:
        logger.warning("No money wasters provided for negative keyword generation")
        return []

    # Sort by waste score descending, then filter and limit results
    sorted_wasters = money_wasters.sort_values('waste_score', ascending=False)
    candidates = sorted_wasters[
        sorted_wasters['waste_score'] >= min_waste_score
    ]['ngram'].head(max_results).tolist()

    logger.info(
        f"Generated {len(candidates)} negative keyword suggestions "
        f"(min waste score: {min_waste_score})"
    )

    return candidates


def calculate_potential_savings(money_wasters: pd.DataFrame) -> dict:
    """
    Calculate potential savings from excluding money wasters

    Args:
        money_wasters: DataFrame from identify_money_wasters()

    Returns:
        Dictionary with:
        - total_wasted_cost: Total cost on money wasters
        - total_wasted_clicks: Total clicks on money wasters
        - wasted_conversions: Conversions from money wasters
        - avg_waste_cpa: Average CPA of money wasters
        - potential_savings_pct: Percentage of total cost wasted
    """
    if money_wasters.empty:
        return {
            'total_wasted_cost': 0,
            'total_wasted_clicks': 0,
            'wasted_conversions': 0,
            'avg_waste_cpa': 0,
            'potential_savings_pct': 0
        }

    total_cost = money_wasters['total_cost'].sum()
    total_clicks = money_wasters['total_clicks'].sum()
    total_conversions = money_wasters['total_conversions'].sum()
    avg_cpa = money_wasters['cpa'].mean()

    return {
        'total_wasted_cost': total_cost,
        'total_wasted_clicks': total_clicks,
        'wasted_conversions': total_conversions,
        'avg_waste_cpa': avg_cpa,
        'potential_savings_pct': 0  # Would need total dataset to calculate
    }
