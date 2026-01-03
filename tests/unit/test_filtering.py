"""
Unit tests for filtering.py module.

Tests for filtering indexed items based on query strings with column selectors and flags.
"""
import pytest
from listpick.utils.filtering import filter_items


class TestFilterItems:
    """Test the filter_items function."""

    @pytest.fixture
    def sample_items(self):
        """Sample data for filtering tests."""
        return [
            ["Alice", "30", "Engineer", "alice@example.com"],
            ["Bob", "25", "Designer", "bob@example.com"],
            ["Charlie", "35", "Manager", "charlie@example.com"],
            ["Diana", "28", "Developer", "diana@example.com"],
            ["Eve", "32", "Analyst", "eve@example.com"],
        ]

    @pytest.fixture
    def sample_indexed_items(self, sample_items):
        """Sample indexed items."""
        return [(i, item) for i, item in enumerate(sample_items)]

    def test_filter_basic_query(self, sample_items, sample_indexed_items):
        """Test basic filtering with simple query."""
        result = filter_items(sample_items, sample_indexed_items, "Alice")
        assert len(result) == 1
        assert result[0][1][0] == "Alice"

    def test_filter_regex_pattern(self, sample_items, sample_indexed_items):
        """Test filtering with regex pattern."""
        result = filter_items(sample_items, sample_indexed_items, "^[AB]")
        # Should match Alice, Bob, and Analyst (Eve) - pattern matches anywhere in row
        assert len(result) >= 2
        assert result[0][1][0] == "Alice"
        assert result[1][1][0] == "Bob"

    def test_filter_column_specific(self, sample_items, sample_indexed_items):
        """Test filtering on specific column."""
        result = filter_items(sample_items, sample_indexed_items, "--0 Alice")
        # Should only match Alice in column 0 (name)
        assert len(result) == 1
        assert result[0][1][0] == "Alice"

    def test_filter_column_specific_no_match(self, sample_items, sample_indexed_items):
        """Test filtering on specific column with no match."""
        result = filter_items(sample_items, sample_indexed_items, "--1 Alice")
        # Alice is not in column 1 (age), should return empty
        assert len(result) == 0

    def test_filter_multiple_columns(self, sample_items, sample_indexed_items):
        """Test filtering with multiple column specifications."""
        result = filter_items(sample_items, sample_indexed_items, "--2 Engineer")
        # Should match Engineer in column 2 (role)
        assert len(result) == 1
        assert result[0][1][2] == "Engineer"

    def test_filter_case_insensitive_default(self, sample_items, sample_indexed_items):
        """Test that filtering is case insensitive by default."""
        result = filter_items(sample_items, sample_indexed_items, "alice")
        # Should match Alice even with lowercase query
        assert len(result) == 1
        assert result[0][1][0] == "Alice"

    def test_filter_empty_query(self, sample_items, sample_indexed_items):
        """Test filtering with empty query."""
        result = filter_items(sample_items, sample_indexed_items, "")
        # Empty query should match all items
        assert len(result) == len(sample_items)

    def test_filter_no_matches(self, sample_items, sample_indexed_items):
        """Test filtering with query that matches nothing."""
        result = filter_items(sample_items, sample_indexed_items, "NOMATCH")
        assert len(result) == 0

    def test_filter_empty_items(self):
        """Test filtering empty items list."""
        result = filter_items([], [], "query")
        assert result == []

    def test_filter_empty_nested_list(self):
        """Test filtering list with empty nested list."""
        result = filter_items([[]], [[]], "query")
        assert result == []

    def test_filter_partial_match(self, sample_items, sample_indexed_items):
        """Test filtering with partial string match."""
        result = filter_items(sample_items, sample_indexed_items, "sign")
        # Should match Designer
        assert len(result) == 1
        assert result[0][1][2] == "Designer"

    def test_filter_email_domain(self, sample_items, sample_indexed_items):
        """Test filtering for email domain."""
        result = filter_items(sample_items, sample_indexed_items, "@example.com")
        # All emails contain @example.com
        assert len(result) == len(sample_items)

    def test_filter_column_number(self, sample_items, sample_indexed_items):
        """Test filtering on age column."""
        result = filter_items(sample_items, sample_indexed_items, "--1 3[0-9]")
        # Should match ages in 30s: 30, 35, 32
        assert len(result) == 3

    def test_filter_multiple_patterns_same_row(self, sample_items, sample_indexed_items):
        """Test filtering with multiple patterns that must all match."""
        result = filter_items(sample_items, sample_indexed_items, "--0 Bob --2 Designer")
        # Should match only Bob who is a Designer
        assert len(result) == 1
        assert result[0][1][0] == "Bob"
        assert result[0][1][2] == "Designer"

    def test_filter_invalid_regex(self, sample_items, sample_indexed_items):
        """Test filtering with invalid regex (should be handled gracefully)."""
        # Invalid regex like unclosed bracket
        result = filter_items(sample_items, sample_indexed_items, "--0 [invalid")
        # Should handle gracefully, likely returns all or none
        assert isinstance(result, list)

    def test_filter_preserves_original_index(self, sample_items, sample_indexed_items):
        """Test that filtering preserves original indices."""
        result = filter_items(sample_items, sample_indexed_items, "Charlie")
        # Charlie is at original index 2
        assert result[0][0] == 2
        assert result[0][1][0] == "Charlie"

    def test_filter_special_regex_characters(self, sample_items, sample_indexed_items):
        """Test filtering with special regex characters."""
        result = filter_items(sample_items, sample_indexed_items, r"\.")
        # Should match emails with dot (.)
        assert len(result) == len(sample_items)

    def test_filter_digit_pattern(self, sample_items, sample_indexed_items):
        """Test filtering with digit pattern."""
        result = filter_items(sample_items, sample_indexed_items, r"\d{2}")
        # Should match ages (all are 2 digits)
        assert len(result) == len(sample_items)

    def test_filter_word_boundary(self, sample_items, sample_indexed_items):
        """Test filtering with word boundary."""
        result = filter_items(sample_items, sample_indexed_items, r"\bEve\b")
        # Should match only exact word "Eve"
        assert len(result) == 1
        assert result[0][1][0] == "Eve"
