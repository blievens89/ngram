"""
Unit tests for text cleaning and n-gram extraction
"""

import pytest
from core.cleaner import clean_query, extract_ngrams


class TestCleanQuery:
    """Tests for clean_query function"""

    def test_basic_cleaning(self):
        """Test basic query cleaning"""
        result = clean_query("Test Query")
        assert result == ['test', 'query']

    def test_special_characters_removed(self):
        """Test that special characters are removed"""
        result = clean_query("Best Remortgage Deals!")
        assert result == ['best', 'remortgage', 'deals']

    def test_multiple_special_characters(self):
        """Test removal of various special characters"""
        result = clean_query("Test@Query#2024$$$")
        assert result == ['test', 'query', '2024']

    def test_stop_words_filtering(self):
        """Test that stop words are filtered out"""
        stop_words = {'the', 'a', 'and'}
        result = clean_query("The best and a query", stop_words)
        assert result == ['best', 'query']

    def test_empty_query(self):
        """Test handling of empty query"""
        result = clean_query("")
        assert result == []

    def test_only_special_characters(self):
        """Test query with only special characters"""
        result = clean_query("!!@@##$$")
        assert result == []

    def test_numbers_preserved(self):
        """Test that numbers are preserved"""
        result = clean_query("mortgage 2024")
        assert result == ['mortgage', '2024']

    def test_case_insensitive(self):
        """Test that cleaning is case insensitive"""
        result = clean_query("BEST Mortgage DEALS")
        assert result == ['best', 'mortgage', 'deals']

    def test_multiple_spaces(self):
        """Test handling of multiple spaces"""
        result = clean_query("best    mortgage    deals")
        assert result == ['best', 'mortgage', 'deals']


class TestExtractNgrams:
    """Tests for extract_ngrams function"""

    def test_bigram_extraction(self):
        """Test extraction of 2-grams"""
        result = extract_ngrams("cheap remortgage calculator", n=2)
        assert result == ['cheap remortgage', 'remortgage calculator']

    def test_trigram_extraction(self):
        """Test extraction of 3-grams"""
        result = extract_ngrams("cheap remortgage calculator rates", n=3)
        assert result == ['cheap remortgage calculator', 'remortgage calculator rates']

    def test_unigram_extraction(self):
        """Test extraction of 1-grams"""
        result = extract_ngrams("cheap remortgage", n=1)
        assert result == ['cheap', 'remortgage']

    def test_fourgram_extraction(self):
        """Test extraction of 4-grams"""
        result = extract_ngrams("best cheap remortgage calculator rates", n=4)
        assert result == ['best cheap remortgage calculator', 'cheap remortgage calculator rates']

    def test_query_too_short(self):
        """Test that empty list is returned when query is too short"""
        result = extract_ngrams("test", n=2)
        assert result == []

    def test_query_exactly_n_words(self):
        """Test query with exactly n words"""
        result = extract_ngrams("cheap remortgage", n=2)
        assert result == ['cheap remortgage']

    def test_with_stop_words(self):
        """Test n-gram extraction with stop words filtering"""
        stop_words = {'the', 'a'}
        result = extract_ngrams("the best remortgage deals", n=2, stop_words=stop_words)
        assert result == ['best remortgage', 'remortgage deals']

    def test_special_characters_handled(self):
        """Test that special characters are cleaned before n-gram extraction"""
        result = extract_ngrams("best! remortgage? deals", n=2)
        assert result == ['best remortgage', 'remortgage deals']

    def test_empty_query_returns_empty(self):
        """Test that empty query returns empty list"""
        result = extract_ngrams("", n=2)
        assert result == []

    def test_large_n(self):
        """Test with n larger than query length"""
        result = extract_ngrams("test query", n=5)
        assert result == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
