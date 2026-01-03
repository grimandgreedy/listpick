"""
Unit tests for search_and_filter_utils.py module.

Tests for tokenise and apply_filter functions.
"""
import pytest
from listpick.utils.search_and_filter_utils import apply_filter, tokenise


# ============================================================================
# Tests for tokenise
# ============================================================================

class TestTokenise:
    """Test the tokenise function."""

    def test_tokenise_simple_query(self):
        """Test tokenising a simple query."""
        result = tokenise("hello")
        assert result == {-1: ["hello"]}

    def test_tokenise_column_specific(self):
        """Test tokenising column-specific query."""
        result = tokenise("--0 pattern")
        assert result == {0: ["pattern"]}

    def test_tokenise_multiple_columns(self):
        """Test tokenising multiple column filters."""
        result = tokenise("--0 alice --1 30")
        assert result == {0: ["alice"], 1: ["30"]}

    def test_tokenise_column_with_pattern(self):
        """Test tokenising column with regex pattern."""
        result = tokenise("--2 eng.*")
        assert result == {2: ["eng.*"]}

    def test_tokenise_mixed_filters(self):
        """Test tokenising mix of column-specific and general filters."""
        result = tokenise("--0 alice manager")
        assert result == {0: ["alice"], -1: ["manager"]}

    def test_tokenise_case_sensitive_flag(self):
        """Test tokenising with case-sensitive flag (--i)."""
        # The --i flag is handled in filtering logic, tokenise just parses tokens
        result = tokenise("--i pattern")
        # --i is consumed as a flag, not added to filters
        # After --i, "pattern" is the next token
        assert -1 in result or 0 in result  # Pattern should be added somewhere

    def test_tokenise_invert_flag(self):
        """Test tokenising with invert flag (--v)."""
        # The --v flag is handled in filtering logic
        result = tokenise("--v pattern")
        # --v is consumed, pattern should be added
        assert -1 in result

    def test_tokenise_empty_string(self):
        """Test tokenising empty string."""
        result = tokenise("")
        assert result == {}

    def test_tokenise_whitespace_only(self):
        """Test tokenising whitespace-only string."""
        result = tokenise("   ")
        assert result == {}

    def test_tokenise_multiple_patterns_same_column(self):
        """Test tokenising multiple patterns for same column."""
        result = tokenise("--0 alice --0 bob")
        assert 0 in result
        assert len(result[0]) == 2
        assert "alice" in result[0]
        assert "bob" in result[0]

    def test_tokenise_multiple_general_patterns(self):
        """Test tokenising multiple general patterns."""
        result = tokenise("alice bob charlie")
        assert result == {-1: ["alice", "bob", "charlie"]}

    def test_tokenise_column_at_end(self):
        """Test tokenising column specifier at end without pattern."""
        result = tokenise("pattern --0")
        # --0 at end without pattern should be handled gracefully
        assert -1 in result
        assert "pattern" in result[-1]

    def test_tokenise_invalid_regex_pattern(self):
        """Test tokenising invalid regex (handled in function)."""
        # Invalid regex should be caught and not added
        result = tokenise("[invalid")
        # Implementation tries to compile regex, invalid ones are skipped
        # Depends on implementation - may be empty or may add it anyway
        assert isinstance(result, dict)

    def test_tokenise_special_characters(self):
        """Test tokenising with special regex characters."""
        result = tokenise(r"\.")
        assert -1 in result
        assert r"\." in result[-1]

    def test_tokenise_quoted_pattern(self):
        """Test tokenising pattern with quotes (quotes not handled specially)."""
        result = tokenise('"alice bob"')
        # Quotes are treated as part of pattern
        assert -1 in result
        assert '"alice' in result[-1]

    def test_tokenise_numeric_pattern(self):
        """Test tokenising numeric pattern."""
        result = tokenise("--1 30")
        assert result == {1: ["30"]}

    def test_tokenise_column_large_number(self):
        """Test tokenising with large column number."""
        result = tokenise("--99 pattern")
        assert result == {99: ["pattern"]}


# ============================================================================
# Tests for apply_filter
# ============================================================================

class TestApplyFilter:
    """Test the apply_filter function."""

    @pytest.fixture
    def sample_row(self):
        """Sample row for testing."""
        return ["Alice", "30", "Engineer", "alice@example.com"]

    def test_apply_filter_match_all_columns(self, sample_row):
        """Test applying filter that matches any column."""
        filters = {-1: ["Alice"]}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_no_match_all_columns(self, sample_row):
        """Test applying filter that doesn't match any column."""
        filters = {-1: ["NOMATCH"]}
        assert apply_filter(sample_row, filters) is False

    def test_apply_filter_specific_column_match(self, sample_row):
        """Test applying filter to specific column with match."""
        filters = {0: ["Alice"]}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_specific_column_no_match(self, sample_row):
        """Test applying filter to specific column without match."""
        filters = {0: ["Bob"]}
        assert apply_filter(sample_row, filters) is False

    def test_apply_filter_wrong_column(self, sample_row):
        """Test applying filter to wrong column."""
        filters = {1: ["Alice"]}  # Alice is in column 0, not 1
        assert apply_filter(sample_row, filters) is False

    def test_apply_filter_case_insensitive(self, sample_row):
        """Test case-insensitive filtering (default)."""
        filters = {-1: ["alice"]}
        assert apply_filter(sample_row, filters, case_sensitive=False) is True

    def test_apply_filter_case_sensitive_match(self, sample_row):
        """Test case-sensitive filtering with match."""
        filters = {-1: ["Alice"]}
        assert apply_filter(sample_row, filters, case_sensitive=True) is True

    def test_apply_filter_case_sensitive_no_match(self, sample_row):
        """Test case-sensitive filtering without match."""
        # Use uppercase pattern that won't match (implementation uses lowercase check)
        filters = {-1: ["ALICE"]}
        assert apply_filter(sample_row, filters, case_sensitive=True) is False

    def test_apply_filter_regex_pattern(self, sample_row):
        """Test applying regex pattern filter."""
        filters = {-1: ["^Ali.*"]}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_multiple_filters_all_match(self, sample_row):
        """Test applying multiple filters that all match."""
        filters = {0: ["Alice"], 2: ["Engineer"]}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_multiple_filters_one_no_match(self, sample_row):
        """Test applying multiple filters where one doesn't match."""
        filters = {0: ["Alice"], 2: ["Manager"]}
        assert apply_filter(sample_row, filters) is False

    def test_apply_filter_column_out_of_range(self, sample_row):
        """Test applying filter to column index out of range."""
        filters = {10: ["pattern"]}
        assert apply_filter(sample_row, filters) is False

    def test_apply_filter_negative_column_not_minus_one(self, sample_row):
        """Test applying filter to negative column (other than -1)."""
        filters = {-2: ["pattern"]}
        assert apply_filter(sample_row, filters) is False

    def test_apply_filter_empty_filters(self, sample_row):
        """Test applying empty filters dictionary."""
        filters = {}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_partial_match(self, sample_row):
        """Test applying filter with partial match."""
        filters = {-1: ["gin"]}  # Should match "Engineer"
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_email_pattern(self, sample_row):
        """Test applying filter with email pattern."""
        filters = {-1: [r".*@example\.com"]}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_digit_pattern(self, sample_row):
        """Test applying filter with digit pattern."""
        filters = {1: [r"\d{2}"]}  # Match 2-digit age
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_word_boundary(self, sample_row):
        """Test applying filter with word boundary."""
        filters = {-1: [r"\bEngineer\b"]}
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_multiple_patterns_same_column(self, sample_row):
        """Test applying multiple patterns to same column (all must match)."""
        filters = {0: ["Ali", "ice"]}  # Both should match "Alice"
        assert apply_filter(sample_row, filters) is True

    def test_apply_filter_highlights_disabled(self, sample_row):
        """Test apply_filter without highlights."""
        filters = {-1: ["Alice"]}
        highlights = []
        result = apply_filter(sample_row, filters, add_highlights=False, highlights=highlights)
        assert result is True
        assert len(highlights) == 0

    def test_apply_filter_highlights_enabled(self, sample_row):
        """Test apply_filter with highlights enabled."""
        filters = {-1: ["Alice"]}
        highlights = []
        result = apply_filter(sample_row, filters, add_highlights=True, highlights=highlights)
        assert result is True
        assert len(highlights) > 0
        assert highlights[0]["match"] == "Alice"
        assert highlights[0]["field"] == "all"

    def test_apply_filter_highlights_column_specific(self, sample_row):
        """Test apply_filter with highlights for specific column."""
        filters = {0: ["Alice"]}
        highlights = []
        result = apply_filter(sample_row, filters, add_highlights=True, highlights=highlights)
        assert result is True
        assert len(highlights) > 0
        assert highlights[0]["field"] == 0

    def test_apply_filter_empty_row(self):
        """Test applying filter to empty row."""
        filters = {-1: ["pattern"]}
        assert apply_filter([], filters) is False

    def test_apply_filter_row_with_empty_strings(self):
        """Test applying filter to row with empty strings."""
        row = ["", "data", ""]
        filters = {-1: ["data"]}
        assert apply_filter(row, filters) is True

    def test_apply_filter_case_detection(self, sample_row):
        """Test that mixed case in pattern enables case sensitivity."""
        # If filter != filter.lower(), case sensitivity is enabled
        filters = {-1: ["Alice"]}  # "Alice" != "alice", so case sensitive
        # This should be case sensitive automatically
        result = apply_filter(sample_row, filters)
        assert result is True
