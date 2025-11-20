"""
Utility functions and helpers
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd

from config import SAVED_ANALYSES_DIR, LOG_DIR

logger = logging.getLogger(__name__)


def setup_logging():
    """
    Setup logging configuration for the application
    """
    # Create logs directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    # Create logger
    log_filename = os.path.join(
        LOG_DIR,
        f'ngram_analyzer_{datetime.now().strftime("%Y%m%d")}.log'
    )

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    logger.info("Logging initialized")


def save_analysis(results: Dict[int, pd.DataFrame], settings: dict, name: str) -> str:
    """
    Save analysis results to disk

    Args:
        results: Dictionary mapping n-gram size to DataFrame
        settings: Analysis settings dictionary
        name: Name for this analysis

    Returns:
        Filename of saved analysis
    """
    os.makedirs(SAVED_ANALYSES_DIR, exist_ok=True)

    save_data = {
        'timestamp': datetime.now().isoformat(),
        'name': name,
        'settings': settings,
        'results': {}
    }

    # Convert DataFrames to dict format (excluding 'queries' column for size)
    for n, df in results.items():
        # Drop queries column if it exists to save space
        df_save = df.drop(columns=['queries'], errors='ignore')
        save_data['results'][str(n)] = df_save.to_dict('records')

    filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.json"
    filepath = os.path.join(SAVED_ANALYSES_DIR, filename)

    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)

    logger.info(f"Analysis saved to {filepath}")
    return filename


def load_analysis(filename: str) -> Dict[int, pd.DataFrame]:
    """
    Load previously saved analysis

    Args:
        filename: Name of the saved analysis file

    Returns:
        Dictionary mapping n-gram size to DataFrame
    """
    filepath = os.path.join(SAVED_ANALYSES_DIR, filename)

    with open(filepath, 'r') as f:
        data = json.load(f)

    results = {}
    for n_str, records in data['results'].items():
        results[int(n_str)] = pd.DataFrame(records)

    logger.info(f"Analysis loaded from {filepath}")
    return results


def get_saved_analyses() -> list:
    """
    Get list of saved analysis files

    Returns:
        List of filenames
    """
    if not os.path.exists(SAVED_ANALYSES_DIR):
        return []

    files = [
        f for f in os.listdir(SAVED_ANALYSES_DIR)
        if f.endswith('.json') and f.startswith('analysis_')
    ]

    return sorted(files, reverse=True)  # Most recent first


def format_metric_value(value: float, metric: str) -> str:
    """
    Format a metric value for display

    Args:
        value: The numeric value
        metric: The metric name

    Returns:
        Formatted string
    """
    if metric in ['total_cost', 'cpa']:
        return f'£{value:,.2f}'
    elif metric in ['ctr', 'cvr']:
        return f'{value:.2f}%'
    elif metric in ['total_clicks', 'total_conversions', 'total_impressions', 'query_count']:
        return f'{int(value):,}'
    elif metric == 'waste_score':
        return f'{value:.3f}'
    else:
        return f'{value:,.2f}'


def export_to_text(df: pd.DataFrame, n: int, filepath: str = None) -> str:
    """
    Export n-grams to plain text format

    Args:
        df: N-gram DataFrame
        n: N-gram size
        filepath: Optional file path to save to

    Returns:
        Text content
    """
    lines = [f"{n}-GRAM ANALYSIS RESULTS", "=" * 50, ""]

    for _, row in df.iterrows():
        lines.append(f"N-gram: {row['ngram']}")
        lines.append(f"  Queries: {int(row['query_count'])}")
        lines.append(f"  Clicks: {int(row['total_clicks'])}")
        lines.append(f"  Cost: £{row['total_cost']:.2f}")
        lines.append(f"  Conversions: {int(row['total_conversions'])}")
        lines.append(f"  CVR: {row['cvr']:.2f}%")
        lines.append(f"  CPA: £{row['cpa']:.2f}")
        lines.append("")

    content = '\n'.join(lines)

    if filepath:
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Exported to {filepath}")

    return content
