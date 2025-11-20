"""
Configuration file for N-Gram Query Analyser
Contains constants, default settings, and brand configuration
"""

from dataclasses import dataclass
from typing import List, Set, Dict


@dataclass
class BrandColors:
    """Platform81 brand colors"""
    NIGHT: str = "#111111"
    NIGHT_LIGHT: str = "#1a1a1a"
    NIGHT_LIGHTER: str = "#222222"
    EMERALD: str = "#47d495"
    POWDER_BLUE: str = "#98c1d9"
    BURNT_SIENNA: str = "#ee6c4d"
    SLATE_BLUE: str = "#6f58c9"


@dataclass
class AnalysisDefaults:
    """Default analysis settings"""
    NGRAM_SIZES: List[int] = None
    MIN_OCCURRENCES: int = 2
    SORT_METRIC: str = "total_cost"
    SORT_ASCENDING: bool = False
    COST_PERCENTILE: int = 75
    CVR_PERCENTILE: int = 25

    def __post_init__(self):
        if self.NGRAM_SIZES is None:
            self.NGRAM_SIZES = [1, 2, 3]


# Column mapping configurations
COLUMN_MAPPINGS: Dict[str, List[str]] = {
    'query': ['search term', 'search_term', 'query', 'search terms', 'searchterm'],
    'clicks': ['interactions', 'clicks', 'click', 'interaction', 'total clicks'],
    'cost': ['cost', 'spend', 'cost_gbp', 'total cost', 'totalcost'],
    'conversions': ['conversions', 'conv.', 'conv', 'converted', 'total conversions'],
    'impressions': ['impr.', 'impressions', 'impr', 'impression']
}

# Required columns (all except impressions)
REQUIRED_COLUMNS = ['query', 'clicks', 'cost', 'conversions']

# Default stop words
DEFAULT_STOP_WORDS: Set[str] = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will',
    'with', 'www', 'com', 'co', 'uk', 'org', 'net'
}

# Metric display configurations
METRIC_FORMATS = {
    'total_clicks': '{:,.0f}',
    'total_cost': '£{:,.2f}',
    'total_conversions': '{:,.0f}',
    'total_impressions': '{:,.0f}',
    'ctr': '{:.2f}%',
    'cvr': '{:.2f}%',
    'cpa': '£{:.2f}',
    'waste_score': '{:.3f}'
}

# Sort metric options
SORT_METRICS = ['total_cost', 'total_clicks', 'total_conversions', 'cpa', 'cvr', 'ctr']

# File paths
SAVED_ANALYSES_DIR = 'saved_analyses'
LOG_DIR = 'logs'

# Application settings
APP_TITLE = "N-Gram Query Analyser"
APP_ICON = "🔍"
APP_LAYOUT = "wide"

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
