"""
Unit tests for money waster detection
"""

import pytest
import pandas as pd
from core.money_wasters import (
    identify_money_wasters,
    generate_negative_keywords,
    calculate_potential_savings
)


@pytest.fixture
def sample_ngram_data():
    """Sample n-gram analysis results"""
    return pd.DataFrame({
        'ngram': ['cheap', 'expensive', 'best', 'worst', 'good'],
        'total_cost': [100.0, 500.0, 200.0, 400.0, 150.0],
        'total_clicks': [1000, 500, 800, 400, 600],
        'total_conversions': [50, 5, 40, 3, 30],
        'cvr': [5.0, 1.0, 5.0, 0.75, 5.0],
        'cpa': [2.0, 100.0, 5.0, 133.33, 5.0],
        'query_count': [10, 5, 8, 4, 6]
    })


class TestIdentifyMoneyWasters:
    """Tests for identify_money_wasters function"""

    def test_basic_identification(self, sample_ngram_data):
        """Test basic money waster identification"""
        result = identify_money_wasters(sample_ngram_data, 75, 25)

        assert not result.empty
        assert 'waste_score' in result.columns

    def test_high_cost_low_cvr(self, sample_ngram_data):
        """Test that money wasters have high cost and low CVR"""
        result = identify_money_wasters(sample_ngram_data, 75, 25)

        # Get 75th percentile cost
        cost_threshold = sample_ngram_data['total_cost'].quantile(0.75)
        cvr_threshold = sample_ngram_data['cvr'].quantile(0.25)

        for _, row in result.iterrows():
            assert row['total_cost'] >= cost_threshold
            assert row['cvr'] <= cvr_threshold

    def test_waste_score_calculation(self, sample_ngram_data):
        """Test that waste score is calculated correctly"""
        result = identify_money_wasters(sample_ngram_data, 75, 25)

        # Waste score should be between 0 and 1
        assert all(0 <= score <= 1 for score in result['waste_score'])

    def test_sorted_by_waste_score(self, sample_ngram_data):
        """Test that results are sorted by waste score descending"""
        result = identify_money_wasters(sample_ngram_data, 75, 25)

        if len(result) > 1:
            waste_scores = result['waste_score'].tolist()
            assert waste_scores == sorted(waste_scores, reverse=True)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame(columns=['ngram', 'total_cost', 'cvr'])
        result = identify_money_wasters(empty_df, 75, 25)

        assert result.empty

    def test_no_money_wasters(self):
        """Test when no n-grams meet the criteria"""
        # All have low cost or high CVR
        df = pd.DataFrame({
            'ngram': ['good1', 'good2', 'good3'],
            'total_cost': [10.0, 20.0, 30.0],
            'cvr': [10.0, 15.0, 20.0],
            'total_clicks': [100, 200, 300],
            'total_conversions': [10, 30, 60]
        })

        result = identify_money_wasters(df, 90, 10)

        # Might be empty or have very few results
        assert isinstance(result, pd.DataFrame)

    def test_custom_thresholds(self, sample_ngram_data):
        """Test with custom percentile thresholds"""
        result_strict = identify_money_wasters(sample_ngram_data, 90, 10)
        result_loose = identify_money_wasters(sample_ngram_data, 50, 50)

        # Stricter thresholds should produce fewer results
        assert len(result_strict) <= len(result_loose)


class TestGenerateNegativeKeywords:
    """Tests for generate_negative_keywords function"""

    def test_basic_generation(self):
        """Test basic negative keyword generation"""
        money_wasters = pd.DataFrame({
            'ngram': ['bad1', 'bad2', 'bad3'],
            'waste_score': [0.9, 0.7, 0.5]
        })

        result = generate_negative_keywords(money_wasters, min_waste_score=0.5)

        assert len(result) == 3
        assert 'bad1' in result
        assert 'bad2' in result
        assert 'bad3' in result

    def test_waste_score_filter(self):
        """Test that minimum waste score filter works"""
        money_wasters = pd.DataFrame({
            'ngram': ['bad1', 'bad2', 'bad3'],
            'waste_score': [0.9, 0.7, 0.3]
        })

        result = generate_negative_keywords(money_wasters, min_waste_score=0.5)

        assert len(result) == 2
        assert 'bad1' in result
        assert 'bad2' in result
        assert 'bad3' not in result

    def test_max_results_limit(self):
        """Test that max_results limit works"""
        money_wasters = pd.DataFrame({
            'ngram': [f'bad{i}' for i in range(10)],
            'waste_score': [0.9 - i*0.05 for i in range(10)]
        })

        result = generate_negative_keywords(money_wasters, max_results=5)

        assert len(result) == 5

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame(columns=['ngram', 'waste_score'])
        result = generate_negative_keywords(empty_df)

        assert result == []

    def test_sorted_by_waste_score(self):
        """Test that results are sorted by waste score"""
        money_wasters = pd.DataFrame({
            'ngram': ['bad1', 'bad2', 'bad3'],
            'waste_score': [0.5, 0.9, 0.7]
        })

        result = generate_negative_keywords(money_wasters, min_waste_score=0.0)

        # Should be in order: bad2 (0.9), bad3 (0.7), bad1 (0.5)
        assert result[0] == 'bad2'
        assert result[1] == 'bad3'
        assert result[2] == 'bad1'


class TestCalculatePotentialSavings:
    """Tests for calculate_potential_savings function"""

    def test_basic_calculation(self):
        """Test basic savings calculation"""
        money_wasters = pd.DataFrame({
            'ngram': ['bad1', 'bad2'],
            'total_cost': [100.0, 200.0],
            'total_clicks': [1000, 2000],
            'total_conversions': [5, 10],
            'cpa': [20.0, 20.0]
        })

        result = calculate_potential_savings(money_wasters)

        assert result['total_wasted_cost'] == 300.0
        assert result['total_wasted_clicks'] == 3000
        assert result['wasted_conversions'] == 15
        assert result['avg_waste_cpa'] == 20.0

    def test_empty_dataframe(self):
        """Test with empty DataFrame"""
        empty_df = pd.DataFrame(columns=['total_cost', 'total_clicks', 'total_conversions', 'cpa'])
        result = calculate_potential_savings(empty_df)

        assert result['total_wasted_cost'] == 0
        assert result['total_wasted_clicks'] == 0
        assert result['wasted_conversions'] == 0
        assert result['avg_waste_cpa'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
