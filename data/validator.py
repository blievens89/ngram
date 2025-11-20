"""
Data validation and column mapping
"""

import pandas as pd
import streamlit as st
from typing import Optional, List
import logging

from config import COLUMN_MAPPINGS, REQUIRED_COLUMNS

logger = logging.getLogger(__name__)


def find_column(
    df: pd.DataFrame,
    candidates: List[str],
    required: bool = True
) -> Optional[str]:
    """
    Find first matching column from list of candidates

    Args:
        df: DataFrame to search
        candidates: List of possible column names (in priority order)
        required: Whether this column is required

    Returns:
        Column name if found, None otherwise
    """
    for candidate in candidates:
        if candidate in df.columns:
            logger.debug(f"Found column '{candidate}' from candidates: {candidates[:3]}")
            return candidate

    if required:
        logger.warning(f"Required column not found. Tried: {candidates}")

    return None


def validate_and_map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and map DataFrame columns to standard names

    This function:
    1. Normalizes column names (lowercase, strip whitespace)
    2. Maps various column name variations to standard names
    3. Validates that all required columns are present
    4. Creates a clean DataFrame with only needed columns
    5. Handles optional impressions column

    Args:
        df: Input DataFrame with variable column names

    Returns:
        Clean DataFrame with standardized column names:
        ['query', 'clicks', 'cost', 'conversions', 'impressions']

    Raises:
        ValueError: If required columns are missing
    """
    logger.info(f"Validating DataFrame with columns: {list(df.columns)}")

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    mapped = {}
    missing = []

    # Map each required column
    for target_col, candidates in COLUMN_MAPPINGS.items():
        is_required = target_col in REQUIRED_COLUMNS

        found_col = find_column(df, candidates, required=is_required)

        if found_col:
            mapped[target_col] = df[found_col]
            logger.debug(f"Mapped '{found_col}' -> '{target_col}'")
        elif is_required:
            # Format missing column message
            missing.append(f"{target_col} ({'/'.join(candidates[:2])})")

    # Raise error if required columns are missing
    if missing:
        available = ', '.join(df.columns)
        error_msg = (
            f"Missing required columns: {', '.join(missing)}. "
            f"Available columns: {available}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Handle optional impressions column
    if 'impressions' not in mapped:
        logger.info("Impressions column not found - using clicks as proxy")
        mapped['impressions'] = mapped['clicks'].copy()
        st.info("ℹ️ Impressions column not found - using clicks as proxy")

    # Create clean DataFrame
    result = pd.DataFrame(mapped)

    # Convert to numeric and handle errors
    numeric_cols = ['clicks', 'cost', 'conversions', 'impressions']
    for col in numeric_cols:
        result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0)

    # Remove rows with empty queries
    result = result[result['query'].notna() & (result['query'] != '')]

    logger.info(
        f"Validation complete. {len(result)} rows with columns: {list(result.columns)}"
    )

    return result


def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Check data quality and return statistics

    Args:
        df: Validated DataFrame

    Returns:
        Dictionary with data quality metrics
    """
    stats = {
        'total_rows': len(df),
        'rows_with_conversions': len(df[df['conversions'] > 0]),
        'conversion_rate': len(df[df['conversions'] > 0]) / len(df) * 100 if len(df) > 0 else 0,
        'total_cost': df['cost'].sum(),
        'total_clicks': df['clicks'].sum(),
        'total_conversions': df['conversions'].sum(),
        'avg_cpa': df['cost'].sum() / df['conversions'].sum() if df['conversions'].sum() > 0 else 0,
        'rows_with_zero_clicks': len(df[df['clicks'] == 0]),
        'rows_with_zero_cost': len(df[df['cost'] == 0]),
    }

    logger.info(f"Data quality check: {stats['total_rows']} rows, "
                f"{stats['conversion_rate']:.1f}% with conversions")

    return stats
