"""
Unit tests for data validation and column mapping
"""

import pytest
import pandas as pd
import numpy as np
from data.validator import find_column, validate_and_map_columns, validate_data_quality


class TestFindColumn:
    """Tests for find_column function"""

    def test_finds_first_candidate(self):
        """Test that first matching candidate is returned"""
        df = pd.DataFrame(columns=['search term', 'clicks', 'cost'])
        result = find_column(df, ['search term', 'query', 'keyword'])
        assert result == 'search term'

    def test_finds_second_candidate(self):
        """Test that second candidate is found if first doesn't exist"""
        df = pd.DataFrame(columns=['query', 'clicks', 'cost'])
        result = find_column(df, ['search term', 'query', 'keyword'])
        assert result == 'query'

    def test_returns_none_when_not_found(self):
        """Test that None is returned when no match found"""
        df = pd.DataFrame(columns=['something', 'else'])
        result = find_column(df, ['search term', 'query'], required=False)
        assert result is None

    def test_case_sensitive_matching(self):
        """Test that matching is case sensitive (after normalization)"""
        df = pd.DataFrame(columns=['clicks', 'cost'])
        result = find_column(df, ['clicks', 'click'])
        assert result == 'clicks'


class TestValidateAndMapColumns:
    """Tests for validate_and_map_columns function"""

    def test_standard_google_ads_columns(self):
        """Test with standard Google Ads column names"""
        df = pd.DataFrame({
            'Search term': ['test query'],
            'Clicks': [100],
            'Cost': [50.0],
            'Conversions': [5],
            'Impr.': [1000]
        })

        result = validate_and_map_columns(df)

        assert 'query' in result.columns
        assert 'clicks' in result.columns
        assert 'cost' in result.columns
        assert 'conversions' in result.columns
        assert 'impressions' in result.columns

    def test_alternative_column_names(self):
        """Test with alternative column name variations"""
        df = pd.DataFrame({
            'search_term': ['test'],
            'interactions': [100],
            'spend': [50.0],
            'conv.': [5]
        })

        result = validate_and_map_columns(df)

        assert 'query' in result.columns
        assert 'clicks' in result.columns
        assert 'cost' in result.columns
        assert 'conversions' in result.columns

    def test_missing_required_column_raises_error(self):
        """Test that missing required columns raise ValueError"""
        df = pd.DataFrame({
            'Search term': ['test'],
            'Clicks': [100]
            # Missing cost and conversions
        })

        with pytest.raises(ValueError) as excinfo:
            validate_and_map_columns(df)

        assert 'Missing required columns' in str(excinfo.value)

    def test_impressions_defaults_to_clicks(self):
        """Test that missing impressions defaults to clicks"""
        df = pd.DataFrame({
            'Search term': ['test'],
            'Clicks': [100],
            'Cost': [50.0],
            'Conversions': [5]
            # No impressions
        })

        result = validate_and_map_columns(df)

        assert 'impressions' in result.columns
        assert result['impressions'].iloc[0] == result['clicks'].iloc[0]

    def test_numeric_conversion(self):
        """Test that numeric columns are converted properly"""
        df = pd.DataFrame({
            'Search term': ['test'],
            'Clicks': ['100'],  # String
            'Cost': ['50.50'],  # String
            'Conversions': ['5']  # String
        })

        result = validate_and_map_columns(df)

        assert result['clicks'].dtype in [np.int64, np.float64]
        assert result['cost'].dtype == np.float64
        assert result['conversions'].dtype in [np.int64, np.float64]

    def test_invalid_numeric_values_become_zero(self):
        """Test that invalid numeric values are converted to 0"""
        df = pd.DataFrame({
            'Search term': ['test'],
            'Clicks': ['invalid'],
            'Cost': ['50.50'],
            'Conversions': ['5']
        })

        result = validate_and_map_columns(df)

        assert result['clicks'].iloc[0] == 0

    def test_empty_queries_removed(self):
        """Test that rows with empty queries are removed"""
        df = pd.DataFrame({
            'Search term': ['test', '', None, 'another'],
            'Clicks': [100, 50, 75, 200],
            'Cost': [50.0, 25.0, 37.5, 100.0],
            'Conversions': [5, 2, 3, 10]
        })

        result = validate_and_map_columns(df)

        assert len(result) == 2  # Only 'test' and 'another' remain
        assert 'test' in result['query'].values
        assert 'another' in result['query'].values

    def test_column_name_normalization(self):
        """Test that column names are normalized (lowercase, stripped)"""
        df = pd.DataFrame({
            '  Search Term  ': ['test'],
            'CLICKS': [100],
            'Cost ': [50.0],
            ' Conversions': [5]
        })

        result = validate_and_map_columns(df)

        # Should successfully map despite spacing and case differences
        assert 'query' in result.columns
        assert len(result) == 1


class TestValidateDataQuality:
    """Tests for validate_data_quality function"""

    def test_basic_quality_stats(self):
        """Test that basic quality statistics are calculated"""
        df = pd.DataFrame({
            'query': ['test1', 'test2', 'test3'],
            'clicks': [100, 50, 75],
            'cost': [50.0, 25.0, 37.5],
            'conversions': [5, 0, 3],
            'impressions': [1000, 500, 750]
        })

        stats = validate_data_quality(df)

        assert stats['total_rows'] == 3
        assert stats['rows_with_conversions'] == 2
        assert stats['total_cost'] == 112.5
        assert stats['total_clicks'] == 225
        assert stats['total_conversions'] == 8

    def test_conversion_rate_calculation(self):
        """Test that conversion rate is calculated correctly"""
        df = pd.DataFrame({
            'query': ['test1', 'test2', 'test3', 'test4'],
            'clicks': [100, 50, 75, 25],
            'cost': [50.0, 25.0, 37.5, 12.5],
            'conversions': [5, 0, 0, 3],
            'impressions': [1000, 500, 750, 250]
        })

        stats = validate_data_quality(df)

        # 2 out of 4 rows have conversions = 50%
        assert stats['conversion_rate'] == 50.0

    def test_avg_cpa_calculation(self):
        """Test that average CPA is calculated correctly"""
        df = pd.DataFrame({
            'query': ['test1', 'test2'],
            'clicks': [100, 50],
            'cost': [100.0, 50.0],
            'conversions': [10, 5],
            'impressions': [1000, 500]
        })

        stats = validate_data_quality(df)

        # Total cost 150, total conversions 15, CPA = 10
        assert stats['avg_cpa'] == 10.0

    def test_zero_conversions_cpa(self):
        """Test CPA calculation when there are zero conversions"""
        df = pd.DataFrame({
            'query': ['test1'],
            'clicks': [100],
            'cost': [50.0],
            'conversions': [0],
            'impressions': [1000]
        })

        stats = validate_data_quality(df)

        assert stats['avg_cpa'] == 0

    def test_empty_dataframe(self):
        """Test quality validation on empty DataFrame"""
        df = pd.DataFrame(columns=['query', 'clicks', 'cost', 'conversions', 'impressions'])

        stats = validate_data_quality(df)

        assert stats['total_rows'] == 0
        assert stats['conversion_rate'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
