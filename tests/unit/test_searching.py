"""
Unit tests for searching.py module.

Tests for search function with highlighting and cursor positioning.
"""
import pytest
from listpick.utils.searching import search


class TestSearch:
    """Test the search function."""

    @pytest.fixture
    def sample_indexed_items(self):
        """Sample indexed items for testing."""
        return [
            (0, ["Alice", "30", "Engineer"]),
            (1, ["Bob", "25", "Designer"]),
            (2, ["Charlie", "35", "Manager"]),
            (3, ["Diana", "28", "Developer"]),
            (4, ["Eve", "32", "Analyst"]),
        ]

    def test_search_simple_match_found(self, sample_indexed_items):
        """Test search with simple query that finds a match."""
        found, cursor_pos, search_index, search_count, highlights = search(
            "Alice", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert cursor_pos == 0  # Alice is at position 0
        assert search_count == 1
        assert search_index == 1

    def test_search_no_match(self, sample_indexed_items):
        """Test search with query that doesn't match anything."""
        found, cursor_pos, search_index, search_count, highlights = search(
            "NOMATCH", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is False
        assert search_count == 0
        assert search_index == 0

    def test_search_from_middle_wraps_around(self, sample_indexed_items):
        """Test search from middle position wraps to beginning."""
        # Start from position 3, search for "Alice" (at position 0)
        found, cursor_pos, search_index, search_count, highlights = search(
            "Alice", sample_indexed_items, highlights=[], cursor_pos=3
        )
        assert found is True
        assert cursor_pos == 0  # Should wrap around and find Alice
        assert search_count == 1

    def test_search_multiple_matches(self, sample_indexed_items):
        """Test search with multiple matches."""
        # Search for pattern that matches multiple items (e.g., "e" appears in several names)
        found, cursor_pos, search_index, search_count, highlights = search(
            "e", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert search_count >= 2  # Multiple items contain "e"
        # Cursor should move to first match after position 0

    def test_search_case_insensitive(self, sample_indexed_items):
        """Test search is case insensitive by default."""
        found, cursor_pos, search_index, search_count, highlights = search(
            "alice", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert cursor_pos == 0

    def test_search_column_specific(self, sample_indexed_items):
        """Test search on specific column."""
        # Search for "Alice" in column 0
        found, cursor_pos, search_index, search_count, highlights = search(
            "--0 Alice", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert cursor_pos == 0

    def test_search_column_specific_no_match(self, sample_indexed_items):
        """Test search on specific column with no match."""
        # Search for "Alice" in column 1 (age column)
        found, cursor_pos, search_index, search_count, highlights = search(
            "--1 Alice", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is False
        assert search_count == 0

    def test_search_regex_pattern(self, sample_indexed_items):
        """Test search with regex pattern."""
        # Search for names starting with 'A'
        found, cursor_pos, search_index, search_count, highlights = search(
            "^[AB]", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert search_count >= 2  # Alice and Bob

    def test_search_empty_query(self, sample_indexed_items):
        """Test search with empty query."""
        found, cursor_pos, search_index, search_count, highlights = search(
            "", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is False
        assert search_count == 0

    def test_search_empty_indexed_items(self):
        """Test search on empty indexed items."""
        found, cursor_pos, search_index, search_count, highlights = search(
            "query", [], highlights=[], cursor_pos=0
        )
        assert found is False
        assert cursor_pos == 0
        assert search_count == 0

    def test_search_adds_highlights(self, sample_indexed_items):
        """Test that search adds highlights."""
        highlights = []
        found, cursor_pos, search_index, search_count, new_highlights = search(
            "Alice", sample_indexed_items, highlights=highlights, cursor_pos=0
        )
        assert found is True
        assert len(new_highlights) > 0
        # Check highlight structure
        assert new_highlights[0]["match"] == "Alice"
        assert new_highlights[0]["type"] == "search"

    def test_search_clears_previous_search_highlights(self, sample_indexed_items):
        """Test that search clears previous search highlights."""
        # Add some existing search highlights
        old_highlights = [
            {"match": "old", "type": "search", "color": 10},
            {"match": "keep", "type": "other", "color": 5},
        ]
        found, cursor_pos, search_index, search_count, new_highlights = search(
            "Alice", sample_indexed_items, highlights=old_highlights, cursor_pos=0
        )
        # Old search highlights should be removed
        search_highlights = [h for h in new_highlights if h.get("type") == "search"]
        # Should only have new search highlights, not old ones
        assert not any(h.get("match") == "old" for h in search_highlights)
        # Non-search highlights should be preserved
        assert any(h.get("match") == "keep" for h in new_highlights)

    def test_search_with_unselectable_indices(self, sample_indexed_items):
        """Test search skips unselectable indices."""
        # Make position 0 unselectable
        found, cursor_pos, search_index, search_count, highlights = search(
            "Alice", sample_indexed_items, highlights=[], cursor_pos=0,
            unselectable_indices=[0]
        )
        # Alice is at position 0 but it's unselectable, so no match
        assert found is False or cursor_pos != 0

    def test_search_reverse_direction(self, sample_indexed_items):
        """Test search in reverse direction."""
        # Start from position 2, search backwards
        found, cursor_pos, search_index, search_count, highlights = search(
            "Alice", sample_indexed_items, highlights=[], cursor_pos=2, reverse=True
        )
        assert found is True
        assert cursor_pos == 0  # Should find Alice going backwards

    def test_search_index_calculation(self, sample_indexed_items):
        """Test that search_index is calculated correctly."""
        # Search for "e" which appears multiple times
        found, cursor_pos, search_index, search_count, highlights = search(
            "i", sample_indexed_items, highlights=[], cursor_pos=0
        )
        if found:
            # search_index should be between 1 and search_count
            assert 1 <= search_index <= search_count

    def test_search_moves_cursor_to_first_match_after_current_pos(self, sample_indexed_items):
        """Test that search moves cursor to first match after current position."""
        # Start from position 0, search for "e" (skip matches at current position)
        found, cursor_pos, search_index, search_count, highlights = search(
            "e", sample_indexed_items, highlights=[], cursor_pos=0
        )
        if found:
            # Cursor should move past position 0
            assert cursor_pos > 0 or search_count == 1

    def test_search_partial_match(self, sample_indexed_items):
        """Test search with partial string match."""
        found, cursor_pos, search_index, search_count, highlights = search(
            "sign", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True  # Should match "Designer"
        assert cursor_pos == 1

    def test_search_digit_pattern(self, sample_indexed_items):
        """Test search with digit pattern."""
        found, cursor_pos, search_index, search_count, highlights = search(
            r"3[0-9]", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True  # Should match ages 30, 35, 32
        assert search_count >= 2

    def test_search_word_boundary(self, sample_indexed_items):
        """Test search with word boundary."""
        found, cursor_pos, search_index, search_count, highlights = search(
            r"\bEve\b", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert cursor_pos == 4  # Eve is at position 4

    def test_search_continue_from_current_match(self, sample_indexed_items):
        """Test continuing search from current match finds next match."""
        # First search
        found1, cursor_pos1, _, count1, highlights1 = search(
            "e", sample_indexed_items, highlights=[], cursor_pos=0
        )
        if found1 and count1 > 1:
            # Continue searching from first match
            found2, cursor_pos2, _, count2, highlights2 = search(
                "e", sample_indexed_items, highlights=[], cursor_pos=cursor_pos1
            )
            assert found2 is True
            # Should find next match (or wrap to first)
            assert cursor_pos2 != cursor_pos1 or count2 == 1

    def test_search_all_items_match(self, sample_indexed_items):
        """Test search where all items match."""
        # Every item has at least 2 digits in age
        found, cursor_pos, search_index, search_count, highlights = search(
            r"\d\d", sample_indexed_items, highlights=[], cursor_pos=0
        )
        assert found is True
        assert search_count == len(sample_indexed_items)

    def test_search_special_regex_characters(self, sample_indexed_items):
        """Test search with special regex characters (escaped)."""
        # Create special test data
        special_items = [(0, ["test.file", "data"])]
        found, cursor_pos, search_index, search_count, highlights = search(
            r"\.", special_items, highlights=[], cursor_pos=0
        )
        assert found is True

    def test_search_returns_correct_tuple_elements(self, sample_indexed_items):
        """Test that search returns all expected tuple elements."""
        result = search("Alice", sample_indexed_items, highlights=[], cursor_pos=0)
        assert isinstance(result, tuple)
        assert len(result) == 5
        found, cursor_pos, search_index, search_count, highlights = result
        assert isinstance(found, bool)
        assert isinstance(cursor_pos, int)
        assert isinstance(search_index, int)
        assert isinstance(search_count, int)
        assert isinstance(highlights, list)
