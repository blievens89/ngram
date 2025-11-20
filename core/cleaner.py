"""
Text cleaning and n-gram extraction functions
"""

import re
from typing import List, Set, Optional


def clean_query(query: str, stop_words: Optional[Set[str]] = None) -> List[str]:
    """
    Clean and prepare query for n-gram extraction

    Args:
        query: The search query string to clean
        stop_words: Optional set of words to exclude from results

    Returns:
        List of cleaned word tokens

    Examples:
        >>> clean_query("Best Remortgage Deals!")
        ['best', 'remortgage', 'deals']

        >>> clean_query("Best Remortgage Deals!", stop_words={'best'})
        ['remortgage', 'deals']
    """
    # Convert to lowercase and remove special characters
    cleaned = re.sub(r'[^\w\s]', ' ', str(query).lower())

    # Split into words
    words = cleaned.split()

    # Remove stop words if provided
    if stop_words:
        words = [w for w in words if w not in stop_words]

    return words


def extract_ngrams(query: str, n: int, stop_words: Optional[Set[str]] = None) -> List[str]:
    """
    Extract n-grams from a query using sliding window approach

    Args:
        query: The search query string
        n: The size of n-grams to extract (1=unigram, 2=bigram, etc.)
        stop_words: Optional set of words to exclude

    Returns:
        List of n-gram strings

    Examples:
        >>> extract_ngrams("cheap remortgage calculator", n=2)
        ['cheap remortgage', 'remortgage calculator']

        >>> extract_ngrams("test", n=2)
        []
    """
    words = clean_query(query, stop_words)

    # Return empty list if query is too short
    if len(words) < n:
        return []

    # Generate n-grams using sliding window
    return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
