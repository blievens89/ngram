"""
N-gram analysis and metric aggregation
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Set, Optional, Dict, List, Any
import logging

from .cleaner import extract_ngrams

logger = logging.getLogger(__name__)


def analyze_ngrams(
    df: pd.DataFrame,
    n: int,
    min_occurrences: int = 2,
    stop_words: Optional[Set[str]] = None
) -> pd.DataFrame:
    """
    Aggregate metrics for n-grams across all queries

    Args:
        df: DataFrame with columns: query, clicks, cost, conversions, impressions
        n: The size of n-grams to analyze
        min_occurrences: Minimum number of queries an n-gram must appear in
        stop_words: Optional set of words to exclude

    Returns:
        DataFrame with aggregated n-gram metrics including:
        - ngram: the n-gram text
        - query_count: number of queries containing this n-gram
        - total_clicks, total_cost, total_conversions, total_impressions
        - ctr, cvr, cpa: calculated metrics
        - queries: list of queries containing this n-gram

    Raises:
        ValueError: If required columns are missing from DataFrame
    """
    logger.info(f"Starting {n}-gram analysis on {len(df)} queries")

    # Validate required columns
    required_cols = ['query', 'clicks', 'cost', 'conversions']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Initialize aggregation dictionary
    ngram_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'clicks': 0,
        'cost': 0,
        'conversions': 0,
        'impressions': 0,
        'query_count': 0,
        'queries': []
    })

    # Aggregate metrics for each n-gram
    for _, row in df.iterrows():
        ngrams = extract_ngrams(row['query'], n, stop_words)

        for ngram in ngrams:
            ngram_data[ngram]['clicks'] += row['clicks']
            ngram_data[ngram]['cost'] += row['cost']
            ngram_data[ngram]['conversions'] += row['conversions']
            ngram_data[ngram]['impressions'] += row.get('impressions', row['clicks'])
            ngram_data[ngram]['query_count'] += 1
            ngram_data[ngram]['queries'].append(row['query'])

    # Convert to DataFrame
    result: List[Dict[str, Any]] = []

    for ngram, data in ngram_data.items():
        # Filter by minimum occurrences
        if data['query_count'] < min_occurrences:
            continue

        # Calculate derived metrics
        ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
        cvr = (data['conversions'] / data['clicks'] * 100) if data['clicks'] > 0 else 0
        cpa = (data['cost'] / data['conversions']) if data['conversions'] > 0 else 0

        result.append({
            'ngram': ngram,
            'query_count': data['query_count'],
            'total_clicks': data['clicks'],
            'total_cost': data['cost'],
            'total_conversions': data['conversions'],
            'total_impressions': data['impressions'],
            'ctr': ctr,
            'cvr': cvr,
            'cpa': cpa,
            'queries': data['queries']
        })

    logger.info(f"Found {len(result)} unique {n}-grams (min occurrences: {min_occurrences})")

    return pd.DataFrame(result)


def analyze_ngrams_vectorized(
    df: pd.DataFrame,
    n: int,
    min_occurrences: int = 2,
    stop_words: Optional[Set[str]] = None
) -> pd.DataFrame:
    """
    Faster n-gram analysis using vectorized pandas operations

    This is an optimized version that uses pandas vectorized operations
    instead of iterating through rows. Better for large datasets (>10k rows).

    Args:
        df: DataFrame with query data
        n: N-gram size
        min_occurrences: Minimum occurrences threshold
        stop_words: Words to exclude

    Returns:
        DataFrame with aggregated n-gram metrics
    """
    logger.info(f"Starting vectorized {n}-gram analysis on {len(df)} queries")

    # Extract all n-grams at once
    df_copy = df.copy()
    df_copy['ngrams'] = df_copy['query'].apply(
        lambda x: extract_ngrams(x, n, stop_words)
    )

    # Explode to have one row per n-gram
    df_exploded = df_copy.explode('ngrams')
    df_exploded = df_exploded[df_exploded['ngrams'].notna()]

    # Ensure impressions column exists
    if 'impressions' not in df_exploded.columns:
        df_exploded['impressions'] = df_exploded['clicks']

    # Group and aggregate
    result = df_exploded.groupby('ngrams').agg({
        'clicks': 'sum',
        'cost': 'sum',
        'conversions': 'sum',
        'impressions': 'sum',
        'query': ['count', list]
    }).reset_index()

    # Flatten column names
    result.columns = ['ngram', 'total_clicks', 'total_cost', 'total_conversions',
                      'total_impressions', 'query_count', 'queries']

    # Filter by minimum occurrences
    result = result[result['query_count'] >= min_occurrences]

    # Calculate derived metrics using vectorized operations
    result['ctr'] = np.where(
        result['total_impressions'] > 0,
        result['total_clicks'] / result['total_impressions'] * 100,
        0
    )
    result['cvr'] = np.where(
        result['total_clicks'] > 0,
        result['total_conversions'] / result['total_clicks'] * 100,
        0
    )
    result['cpa'] = np.where(
        result['total_conversions'] > 0,
        result['total_cost'] / result['total_conversions'],
        0
    )

    logger.info(f"Found {len(result)} unique {n}-grams using vectorized approach")

    return result
