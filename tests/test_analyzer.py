"""
Unit tests for n-gram analysis
"""

import pytest
import pandas as pd
import numpy as np
from core.analyzer import analyze_ngrams, analyze_ngrams_vectorized


@pytest.fixture
def sample_data():
    """Sample query data for testing"""
    return pd.DataFrame({
        'query': [
            'cheap remortgage',
            'best remortgage deals',
            'remortgage rates',
            'cheap mortgage',
            'best mortgage deals'
        ],
        'clicks': [100, 200, 150, 80, 180],
        'cost': [150.0, 300.0, 225.0, 120.0, 270.0],
        'conversions': [10, 20, 15, 8, 18],
        'impressions': [1000, 2000, 1500, 800, 1800]
    })


class TestAnalyzeNgrams:
    """Tests for analyze_ngrams function"""

    def test_basic_analysis(self, sample_data):
        """Test basic n-gram analysis"""
        result = analyze_ngrams(sample_data, n=1, min_occurrences=1)

        assert not result.empty
        assert 'ngram' in result.columns
        assert 'total_clicks' in result.columns
        assert 'total_cost' in result.columns
        assert 'total_conversions' in result.columns

    def test_bigram_analysis(self, sample_data):
        """Test 2-gram analysis"""
        result = analyze_ngrams(sample_data, n=2, min_occurrences=1)

        assert not result.empty
        # Should find bigrams like 'best remortgage', 'remortgage deals', etc.
        assert any('remortgage' in ngram for ngram in result['ngram'])

    def test_min_occurrences_filter(self, sample_data):
        """Test that min_occurrences filter works"""
        # With min_occurrences=3, only words appearing 3+ times should be included
        result = analyze_ngrams(sample_data, n=1, min_occurrences=3)

        # All n-grams should appear in at least 3 queries
        assert all(result['query_count'] >= 3)

    def test_metric_calculations(self, sample_data):
        """Test that metrics are calculated correctly"""
        result = analyze_ngrams(sample_data, n=1, min_occurrences=1)

        # Check that CTR, CVR, CPA are present and valid
        assert 'ctr' in result.columns
        assert 'cvr' in result.columns
        assert 'cpa' in result.columns

        # All metrics should be non-negative
        assert all(result['ctr'] >= 0)
        assert all(result['cvr'] >= 0)
        assert all(result['cpa'] >= 0)

    def test_stop_words_filtering(self, sample_data):
        """Test that stop words are excluded"""
        stop_words = {'best', 'cheap'}
        result = analyze_ngrams(sample_data, n=1, min_occurrences=1, stop_words=stop_words)

        # Should not contain any stop words
        assert not any(ngram in stop_words for ngram in result['ngram'])

    def test_queries_list_tracking(self, sample_data):
        """Test that queries containing each n-gram are tracked"""
        result = analyze_ngrams(sample_data, n=1, min_occurrences=1)

        # Check that queries list exists and has content
        assert 'queries' in result.columns
        assert all(len(queries) > 0 for queries in result['queries'])

    def test_missing_required_columns(self):
        """Test that missing required columns raises error"""
        bad_data = pd.DataFrame({
            'query': ['test'],
            'clicks': [100]
            # Missing cost and conversions
        })

        with pytest.raises(ValueError):
            analyze_ngrams(bad_data, n=1)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame(columns=['query', 'clicks', 'cost', 'conversions'])
        result = analyze_ngrams(empty_df, n=1, min_occurrences=1)

        assert result.empty

    def test_single_query(self):
        """Test analysis with single query"""
        single_data = pd.DataFrame({
            'query': ['test query'],
            'clicks': [100],
            'cost': [50.0],
            'conversions': [5],
            'impressions': [1000]
        })

        result = analyze_ngrams(single_data, n=1, min_occurrences=1)
        assert len(result) == 2  # 'test' and 'query'

    def test_aggregation_accuracy(self):
        """Test that aggregation is mathematically correct"""
        # Create data where we know the expected aggregation
        test_data = pd.DataFrame({
            'query': ['test query', 'test search', 'test analysis'],
            'clicks': [10, 20, 30],
            'cost': [100.0, 200.0, 300.0],
            'conversions': [1, 2, 3],
            'impressions': [100, 200, 300]
        })

        result = analyze_ngrams(test_data, n=1, min_occurrences=1)

        # Find 'test' n-gram
        test_row = result[result['ngram'] == 'test'].iloc[0]

        # Should aggregate all three queries
        assert test_row['total_clicks'] == 60  # 10 + 20 + 30
        assert test_row['total_cost'] == 600.0  # 100 + 200 + 300
        assert test_row['total_conversions'] == 6  # 1 + 2 + 3
        assert test_row['query_count'] == 3


class TestAnalyzeNgramsVectorized:
    """Tests for vectorized n-gram analysis"""

    def test_vectorized_same_as_standard(self, sample_data):
        """Test that vectorized version produces same results as standard"""
        result_standard = analyze_ngrams(sample_data, n=2, min_occurrences=1)
        result_vectorized = analyze_ngrams_vectorized(sample_data, n=2, min_occurrences=1)

        # Sort both for comparison
        result_standard = result_standard.sort_values('ngram').reset_index(drop=True)
        result_vectorized = result_vectorized.sort_values('ngram').reset_index(drop=True)

        # Compare key columns (excluding queries list which may have different order)
        compare_cols = ['ngram', 'query_count', 'total_clicks', 'total_cost', 'total_conversions']

        for col in compare_cols:
            assert result_standard[col].equals(result_vectorized[col]) or \
                   np.allclose(result_standard[col], result_vectorized[col])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
