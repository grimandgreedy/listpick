"""
Pytest configuration and shared fixtures for listpick tests.
"""
import pytest
from pathlib import Path


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def csv_fixtures_dir(fixtures_dir):
    """Return the path to CSV fixtures directory."""
    return fixtures_dir / "csv"


@pytest.fixture
def xlsx_fixtures_dir(fixtures_dir):
    """Return the path to XLSX fixtures directory."""
    return fixtures_dir / "xlsx"


@pytest.fixture
def ods_fixtures_dir(fixtures_dir):
    """Return the path to ODS fixtures directory."""
    return fixtures_dir / "ods"


@pytest.fixture
def json_fixtures_dir(fixtures_dir):
    """Return the path to JSON fixtures directory."""
    return fixtures_dir / "json"


@pytest.fixture
def config_fixtures_dir(fixtures_dir):
    """Return the path to config fixtures directory."""
    return fixtures_dir / "configs"


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_data():
    """Return sample data as list of lists for testing."""
    return [
        ["Alice", "30", "Engineer", "100000"],
        ["Bob", "25", "Designer", "80000"],
        ["Charlie", "35", "Manager", "120000"],
        ["Diana", "28", "Developer", "95000"],
        ["Eve", "32", "Analyst", "85000"],
    ]


@pytest.fixture
def sample_header():
    """Return sample header for testing."""
    return ["Name", "Age", "Role", "Salary"]


@pytest.fixture
def sample_indexed_items(sample_data):
    """Return sample indexed items (list of tuples with index)."""
    return [(i, row) for i, row in enumerate(sample_data)]


@pytest.fixture
def sample_data_with_numbers():
    """Return sample data with various number formats."""
    return [
        ["Item 1", "100", "1.5GB", "2023-01-15"],
        ["Item 2", "50", "500MB", "2023-02-20"],
        ["Item 3", "200", "2.1GB", "2023-01-10"],
        ["Item 4", "75", "750MB", "2023-03-05"],
    ]


@pytest.fixture
def sample_data_unicode():
    """Return sample data with unicode characters."""
    return [
        ["日本語", "中文", "한국어"],
        ["Hello", "World", "Test"],
        ["Café", "Résumé", "Naïve"],
        ["🎉", "🎊", "🎈"],
    ]


@pytest.fixture
def empty_data():
    """Return empty data list."""
    return []


@pytest.fixture
def single_row_data():
    """Return single row of data."""
    return [["Only", "One", "Row"]]


# ============================================================================
# Selection Fixtures
# ============================================================================

@pytest.fixture
def sample_selection():
    """Return sample selection dictionary."""
    return {0: True, 2: True, 4: True}


@pytest.fixture
def empty_selection():
    """Return empty selection dictionary."""
    return {}


# ============================================================================
# Row Highlight Fixtures
# ============================================================================

@pytest.fixture
def sample_row_highlight():
    """Return sample row highlight dictionary."""
    return {
        0: [(0, 5), (10, 15)],  # Row 0 has highlights at positions 0-5 and 10-15
        1: [(3, 8)],             # Row 1 has highlight at position 3-8
    }


@pytest.fixture
def empty_row_highlight():
    """Return empty row highlight dictionary."""
    return {}
