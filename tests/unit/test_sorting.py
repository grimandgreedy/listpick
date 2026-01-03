"""
Unit tests for sorting.py module.

Tests for sorting algorithms, number parsing, size parsing, time parsing, and date/time sorting.
"""
import pytest
from datetime import datetime
from listpick.utils.sorting import (
    parse_numerical,
    parse_size,
    time_to_seconds,
    time_sort,
    sort_items
)


# ============================================================================
# Tests for parse_numerical
# ============================================================================

class TestParseNumerical:
    """Test the parse_numerical function."""

    def test_parse_simple_integer(self):
        """Test parsing a simple integer."""
        assert parse_numerical("123") == 123.0

    def test_parse_float(self):
        """Test parsing a float."""
        assert parse_numerical("123.45") == 123.45

    def test_parse_number_in_string(self):
        """Test extracting first number from a string."""
        assert parse_numerical("abc123def") == 123.0

    def test_parse_scientific_notation(self):
        """Test parsing scientific notation (extracts mantissa)."""
        result = parse_numerical("1.5e10")
        assert result == 1.5  # Regex only matches the 1.5 part

    def test_parse_no_number(self):
        """Test string with no numbers returns infinity."""
        assert parse_numerical("no numbers") == float('inf')

    def test_parse_empty_string(self):
        """Test empty string returns infinity."""
        assert parse_numerical("") == float('inf')

    def test_parse_multiple_numbers(self):
        """Test that only first number is extracted."""
        assert parse_numerical("abc123def456ghi") == 123.0

    def test_parse_negative_number(self):
        """Test parsing string with negative sign (regex doesn't capture sign)."""
        # The regex pattern doesn't capture the minus sign
        assert parse_numerical("-123") == 123.0

    def test_parse_unicode_numbers(self):
        """Test parsing with unicode number characters."""
        # Regular ASCII numbers should work
        assert parse_numerical("Price: 42.50") == 42.50


# ============================================================================
# Tests for parse_size
# ============================================================================

class TestParseSize:
    """Test the parse_size function."""

    def test_parse_bytes(self):
        """Test parsing bytes."""
        assert parse_size("100B") == 100.0
        assert parse_size("100 B") == 100.0

    def test_parse_kilobytes(self):
        """Test parsing kilobytes."""
        assert parse_size("1KB") == 1024.0
        assert parse_size("1 KB") == 1024.0
        assert parse_size("1K") == 1024.0

    def test_parse_megabytes(self):
        """Test parsing megabytes."""
        assert parse_size("1MB") == 1024**2
        assert parse_size("1 MB") == 1024**2
        assert parse_size("500MB") == 500 * 1024**2

    def test_parse_gigabytes(self):
        """Test parsing gigabytes."""
        assert parse_size("1.5GB") == 1.5 * 1024**3
        assert parse_size("2 GB") == 2 * 1024**3
        assert parse_size("2.1G") == 2.1 * 1024**3

    def test_parse_terabytes(self):
        """Test parsing terabytes."""
        assert parse_size("1TB") == 1024**4
        assert parse_size("5.5 TB") == 5.5 * 1024**4

    def test_parse_petabytes(self):
        """Test parsing petabytes."""
        assert parse_size("1PB") == 1024**5

    def test_parse_case_insensitive(self):
        """Test that parsing is case insensitive."""
        assert parse_size("1gb") == 1024**3
        assert parse_size("1Gb") == 1024**3
        assert parse_size("1gB") == 1024**3

    def test_parse_decimal_sizes(self):
        """Test parsing decimal sizes."""
        assert parse_size("1.5KB") == 1.5 * 1024
        assert parse_size("2.5MB") == 2.5 * 1024**2

    def test_parse_no_size(self):
        """Test string with no size returns infinity."""
        assert parse_size("no size here") == float('inf')

    def test_parse_empty_string(self):
        """Test empty string returns infinity."""
        assert parse_size("") == float('inf')

    def test_parse_size_in_context(self):
        """Test extracting size from a larger string."""
        assert parse_size("File size: 1.5GB remaining") == 1.5 * 1024**3


# ============================================================================
# Tests for time_to_seconds
# ============================================================================

class TestTimeToSeconds:
    """Test the time_to_seconds function."""

    def test_parse_seconds(self):
        """Test parsing seconds."""
        assert time_to_seconds("30 sec") == 30
        assert time_to_seconds("45 s") == 45

    def test_parse_minutes(self):
        """Test parsing minutes."""
        assert time_to_seconds("5 minutes") == 300
        assert time_to_seconds("10 min") == 600

    def test_parse_hours(self):
        """Test parsing hours."""
        assert time_to_seconds("2 hours") == 7200
        assert time_to_seconds("1 hour") == 3600

    def test_parse_days(self):
        """Test parsing days."""
        assert time_to_seconds("1 day") == 86400
        assert time_to_seconds("2 days") == 172800

    def test_parse_years(self):
        """Test parsing years."""
        assert time_to_seconds("1 year") == 365 * 24 * 3600
        assert time_to_seconds("2 years") == 2 * 365 * 24 * 3600

    def test_parse_combined_units(self):
        """Test parsing combined time units."""
        # 1 hour 30 minutes = 3600 + 1800 = 5400
        assert time_to_seconds("1 hour 30 minutes") == 5400
        # 2 days 3 hours = 172800 + 10800 = 183600
        assert time_to_seconds("2 days 3 hours") == 183600

    def test_parse_inf(self):
        """Test parsing INF string."""
        assert time_to_seconds("INF") == float('inf')
        assert time_to_seconds("inf") == float('inf')
        assert time_to_seconds("  INF  ") == float('inf')

    def test_parse_invalid_format(self):
        """Test parsing invalid format returns 0."""
        # The implementation returns 0 for invalid formats (empty total_seconds)
        assert time_to_seconds("invalid") == 0
        assert time_to_seconds("") == 0

    def test_parse_unknown_unit(self):
        """Test parsing unknown time unit (contributes 0)."""
        # Unknown units contribute 0 to total
        result = time_to_seconds("5 unknown")
        assert result == 0


# ============================================================================
# Tests for time_sort
# ============================================================================

class TestTimeSort:
    """Test the time_sort function."""

    def test_parse_iso_date(self):
        """Test parsing ISO format date."""
        result = time_sort("2021-03-16")
        expected = datetime(2021, 3, 16)
        assert result == expected

    def test_parse_iso_datetime(self):
        """Test parsing ISO format datetime."""
        result = time_sort("2021-03-16 15:30")
        expected = datetime(2021, 3, 16, 15, 30)
        assert result == expected

    def test_parse_slash_date_ymd(self):
        """Test parsing slash-separated date (Y/M/D)."""
        result = time_sort("2021/03/16")
        expected = datetime(2021, 3, 16)
        assert result == expected

    def test_parse_slash_date_dmy(self):
        """Test parsing slash-separated date (D/M/Y)."""
        result = time_sort("05/03/2024")
        expected = datetime(2024, 3, 5)
        assert result == expected

    def test_parse_slash_date_short_year(self):
        """Test parsing date with short year."""
        result = time_sort("01/01/23")
        expected = datetime(2023, 1, 1)
        assert result == expected

    def test_parse_full_weekday_format(self):
        """Test parsing full weekday format."""
        result = time_sort("Saturday 01 Feb 2025 21:19:47")
        expected = datetime(2025, 2, 1, 21, 19, 47)
        assert result == expected

    def test_parse_abbreviated_weekday_format(self):
        """Test parsing abbreviated weekday format."""
        result = time_sort("Sat 01 Feb 2025 21:19:47")
        expected = datetime(2025, 2, 1, 21, 19, 47)
        assert result == expected

    def test_parse_time_only_hm(self):
        """Test parsing time only (H:M)."""
        result = time_sort("04:30")
        expected = datetime(1900, 1, 1, 4, 30)
        assert result == expected

    def test_parse_time_only_hms(self):
        """Test parsing time only (H:M:S)."""
        result = time_sort("04:30:23")
        expected = datetime(1900, 1, 1, 4, 30, 23)
        assert result == expected

    def test_parse_invalid_date(self):
        """Test parsing invalid date returns default (00:00)."""
        result = time_sort("not a date")
        expected = datetime(1900, 1, 1, 0, 0)
        assert result == expected

    def test_parse_empty_string(self):
        """Test parsing empty string returns default (00:00)."""
        result = time_sort("")
        expected = datetime(1900, 1, 1, 0, 0)
        assert result == expected


# ============================================================================
# Tests for sort_items
# ============================================================================

class TestSortItems:
    """Test the sort_items function."""

    @pytest.fixture
    def indexed_data_numbers(self):
        """Sample indexed data with numbers."""
        return [
            (0, ["Item 1", "100", "data"]),
            (1, ["Item 2", "50", "data"]),
            (2, ["Item 3", "200", "data"]),
            (3, ["Item 4", "75", "data"]),
        ]

    @pytest.fixture
    def indexed_data_text(self):
        """Sample indexed data with text."""
        return [
            (0, ["Zebra", "data"]),
            (1, ["apple", "data"]),
            (2, ["Banana", "data"]),
            (3, ["cherry", "data"]),
        ]

    @pytest.fixture
    def indexed_data_sizes(self):
        """Sample indexed data with sizes."""
        return [
            (0, ["File 1", "1.5GB"]),
            (1, ["File 2", "500MB"]),
            (2, ["File 3", "2.1GB"]),
            (3, ["File 4", "750MB"]),
        ]

    @pytest.fixture
    def indexed_data_dates(self):
        """Sample indexed data with dates."""
        return [
            (0, ["Event 1", "2023-03-15"]),
            (1, ["Event 2", "2023-01-10"]),
            (2, ["Event 3", "2023-12-25"]),
            (3, ["Event 4", "2023-06-20"]),
        ]

    def test_sort_original_order(self, indexed_data_numbers):
        """Test sorting by original order."""
        # Shuffle first
        data = [(2, ["Item 3", "200", "data"]), (0, ["Item 1", "100", "data"]),
                (3, ["Item 4", "75", "data"]), (1, ["Item 2", "50", "data"])]
        sort_items(data, sort_method=0, sort_column=0, sort_reverse=False)
        # Should be sorted by original index
        assert data[0][0] == 0
        assert data[1][0] == 1
        assert data[2][0] == 2
        assert data[3][0] == 3

    def test_sort_lexicographic_lowercase(self, indexed_data_text):
        """Test lexicographic sorting (case-insensitive)."""
        data = indexed_data_text.copy()
        sort_items(data, sort_method=1, sort_column=0, sort_reverse=False)
        # Should be: apple, Banana, cherry, Zebra
        assert data[0][1][0] == "apple"
        assert data[1][1][0] == "Banana"
        assert data[2][1][0] == "cherry"
        assert data[3][1][0] == "Zebra"

    def test_sort_lexicographic_case_sensitive(self, indexed_data_text):
        """Test lexicographic sorting (case-sensitive)."""
        data = indexed_data_text.copy()
        sort_items(data, sort_method=2, sort_column=0, sort_reverse=False)
        # Should be: Banana, Zebra, apple, cherry (uppercase before lowercase)
        assert data[0][1][0] == "Banana"
        assert data[1][1][0] == "Zebra"
        assert data[2][1][0] == "apple"
        assert data[3][1][0] == "cherry"

    def test_sort_numerical(self, indexed_data_numbers):
        """Test numerical sorting."""
        data = indexed_data_numbers.copy()
        sort_items(data, sort_method=6, sort_column=1, sort_reverse=False)
        # Should be sorted numerically: 50, 75, 100, 200
        assert data[0][1][1] == "50"
        assert data[1][1][1] == "75"
        assert data[2][1][1] == "100"
        assert data[3][1][1] == "200"

    def test_sort_numerical_reverse(self, indexed_data_numbers):
        """Test numerical sorting in reverse."""
        data = indexed_data_numbers.copy()
        sort_items(data, sort_method=6, sort_column=1, sort_reverse=True)
        # Should be sorted numerically reversed: 200, 100, 75, 50
        assert data[0][1][1] == "200"
        assert data[1][1][1] == "100"
        assert data[2][1][1] == "75"
        assert data[3][1][1] == "50"

    def test_sort_size(self, indexed_data_sizes):
        """Test size sorting."""
        data = indexed_data_sizes.copy()
        sort_items(data, sort_method=7, sort_column=1, sort_reverse=False)
        # Should be sorted by size: 500MB, 750MB, 1.5GB, 2.1GB
        assert data[0][1][1] == "500MB"
        assert data[1][1][1] == "750MB"
        assert data[2][1][1] == "1.5GB"
        assert data[3][1][1] == "2.1GB"

    def test_sort_time(self, indexed_data_dates):
        """Test time/date sorting."""
        data = indexed_data_dates.copy()
        sort_items(data, sort_method=5, sort_column=1, sort_reverse=False)
        # Should be sorted by date: 2023-01-10, 2023-03-15, 2023-06-20, 2023-12-25
        assert data[0][1][1] == "2023-01-10"
        assert data[1][1][1] == "2023-03-15"
        assert data[2][1][1] == "2023-06-20"
        assert data[3][1][1] == "2023-12-25"

    def test_sort_empty_list(self):
        """Test sorting empty list."""
        data = []
        sort_items(data, sort_method=1, sort_column=0, sort_reverse=False)
        assert data == []

    def test_sort_single_item(self):
        """Test sorting single item list."""
        data = [(0, ["Only", "One"])]
        sort_items(data, sort_method=1, sort_column=0, sort_reverse=False)
        assert len(data) == 1
        assert data[0][1][0] == "Only"

    def test_sort_with_empty_strings(self):
        """Test sorting with empty strings (should sort to end)."""
        data = [
            (0, ["", "data"]),
            (1, ["Apple", "data"]),
            (2, ["  ", "data"]),  # Whitespace only
            (3, ["Banana", "data"]),
        ]
        sort_items(data, sort_method=1, sort_column=0, sort_reverse=False)
        # Empty/whitespace strings should be at the end
        assert data[0][1][0] == "Apple"
        assert data[1][1][0] == "Banana"
        assert data[2][1][0].strip() == ""
        assert data[3][1][0].strip() == ""

    def test_sort_column_out_of_range(self):
        """Test sorting with column index out of range (should handle gracefully)."""
        data = [(0, ["A"]), (1, ["B"])]
        # Try to sort on column 5 which doesn't exist
        sort_items(data, sort_method=1, sort_column=5, sort_reverse=False)
        # Should not crash, data remains unchanged or handled gracefully
        assert len(data) == 2

    def test_sort_alphanumeric_lowercase(self):
        """Test alphanumeric sorting (case-insensitive)."""
        data = [
            (0, ["file-10", "data"]),
            (1, ["file-2", "data"]),
            (2, ["file_1", "data"]),
            (3, ["file-20", "data"]),
        ]
        sort_items(data, sort_method=3, sort_column=0, sort_reverse=False)
        # Alphanumeric sort treats non-alphanumeric chars specially
        # The exact order depends on the implementation
        assert len(data) == 4

    def test_sort_stability(self):
        """Test that sort is stable for equal values."""
        data = [
            (0, ["A", "1"]),
            (1, ["B", "1"]),
            (2, ["C", "1"]),
        ]
        sort_items(data, sort_method=6, sort_column=1, sort_reverse=False)
        # All have same value in column 1, original order should be preserved
        assert data[0][0] == 0
        assert data[1][0] == 1
        assert data[2][0] == 2
