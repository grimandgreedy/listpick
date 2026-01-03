# Listpick Testing Suite

Comprehensive testing suite for the listpick project with **137 unit tests** and **14 E2E tests**.

## Test Structure

```
tests/
├── conftest.py                # Pytest configuration and shared fixtures
├── unit/                      # Pure unit tests (137 tests)
│   ├── test_sorting.py        # 43 tests
│   ├── test_filtering.py      # 19 tests
│   ├── test_searching.py      # 23 tests
│   └── test_search_filter_utils.py  # 52 tests
├── integration/               # Integration tests (planned)
├── e2e/                       # End-to-end tests (14 tests)
│   ├── conftest.py
│   ├── kitty_helper.py        # KittyController helper class
│   ├── test_smoke.py          # 2 tests
│   ├── test_editing.py        # 4 tests
│   ├── test_files_open_close.py  # 8 tests
│   ├── test_filtering.py
│   ├── test_input_field.py
│   └── test_selection.py
├── fixtures/                  # Test data files
│   ├── csv/
│   ├── xlsx/
│   ├── e2e/                   # E2E test fixtures
│   └── configs/
└── mocks/                     # Mock objects for testing
```

## Running Tests

### Quick Start

```bash
# Run all unit tests (fastest, ~0.1s)
./scripts/run_unit_tests.sh

# Run all tests with coverage
./scripts/run_tests.sh

# Run tests in parallel (faster)
./scripts/run_tests.sh -n auto

# Run E2E tests (requires kitty terminal)
./scripts/run_e2e_tests.sh

# E2E smoke tests only
./scripts/run_e2e_tests.sh -m smoke

```

### Test Options

```bash
# Verbose output
./scripts/run_tests.sh -v

# Run specific test file
./scripts/run_tests.sh tests/unit/test_sorting.py

# Run specific test
./scripts/run_tests.sh tests/e2e/test_editing.py::test_add_row_edit_save

# Stop on first failure
./scripts/run_tests.sh -x

# Generate HTML coverage report
./scripts/run_tests.sh --cov-report=html
open htmlcov/index.html
```

### Running by Category

```bash
# Unit tests only
./scripts/run_tests.sh tests/unit/

# Run only unit tests (by marker)
./scripts/run_tests.sh -m unit

# Skip slow tests
./scripts/run_tests.sh -m "not slow"

# Run only end-to-end tests
./scripts/run_tests.sh -m e2e
```

## Unit Testing

### Coverage

**137 passing tests** covering core business logic:

**Modules Tested:**
- `src/listpick/utils/sorting.py` - All functions (43 tests)
- `src/listpick/utils/filtering.py` - Fully tested (19 tests)
- `src/listpick/utils/searching.py` - Fully tested (23 tests)
- `src/listpick/utils/search_and_filter_utils.py` - Fully tested (52 tests)

**Test Execution:** ~0.1 seconds for all unit tests

### Key Features

- **Comprehensive Coverage**: All sort types, regex patterns, flags (--i, --v, --N)
- **Edge Cases**: Empty data, invalid input, malformed patterns
- **Fast Execution**: Quick feedback during development
- **Well-Organized**: Clear test class structure with descriptive names

### Shared Fixtures

Defined in `tests/conftest.py`:
- `sample_data` - Standard test data
- `sample_header` - Column headers
- `sample_indexed_items` - Indexed data tuples
- `sample_selection` - Selection dictionaries
- Path fixtures for test data files

### Writing Unit Tests

```python
import pytest
from listpick.utils.sorting import parse_numerical

class TestParseNumerical:
    """Test the parse_numerical function."""

    def test_parse_simple_integer(self):
        """Test parsing a simple integer."""
        assert parse_numerical("123") == 123.0

    def test_parse_no_number(self):
        """Test string with no numbers returns infinity."""
        assert parse_numerical("no numbers") == float('inf')
```

### Using Fixtures

```python
def test_with_fixtures(sample_data, sample_header):
    """Use fixtures defined in conftest.py."""
    assert len(sample_data) == 5
    assert len(sample_header) == 4
```

## End-to-End Testing

### Overview

**14 passing E2E tests** using real kitty terminal control to test complete workflows.

**Test Categories:**
- Smoke tests (2) - Basic app functionality
- Editing tests (4) - Row addition, cell editing, file saving
- File management tests (8) - Opening, closing, saving files

**Test Execution:** ~67 seconds for all E2E tests (~4.8s per test)

### Prerequisites

Install [kitty terminal](https://sw.kovidgoyal.net/kitty/):

```bash
# macOS
brew install kitty

# Linux (check kitty website for distribution-specific instructions)
```

### Running E2E Tests

```bash
# All E2E tests
./scripts/run_e2e_tests.sh

# Smoke tests only (fastest)
./scripts/run_e2e_tests.sh -m smoke

# Verbose output with print statements
./scripts/run_e2e_tests.sh -v -s

# Specific test file
pytest tests/e2e/test_editing.py -v
```

### KittyController API

The `KittyController` helper class provides high-level methods for testing:

**Core Methods:**
- `launch_kitty()` - Start kitty terminal
- `send_text(text)` - Type text
- `send_key(key)` - Send special key (return, F5, ctrl+c)
- `get_screen_text()` - Capture terminal output
- `wait_for_text(text, timeout=5)` - Wait for text to appear
- `cleanup()` - Kill kitty process

**High-Level Methods:**
- `launch_listpick(args)` - Launch app with arguments
- `navigate_down(count)`, `navigate_up(count)` - j/k navigation
- `navigate_to_bottom()`, `navigate_to_top()` - G/g navigation
- `select_current()`, `select_all()`, `deselect_all()` - Selection
- `open_filter()`, `clear_filter()` - Filtering
- `quit_app()` - Exit application

**Assertions:**
- `assert_text_present(text)` - Assert text visible on screen
- `assert_footer_contains(text)` - Check footer content
- `assert_selection_count(N)` - Verify N items selected

### Writing E2E Tests

```python
import pytest

@pytest.mark.e2e
@pytest.mark.slow
def test_my_workflow(kitty, simple_data_path):
    """Test description."""
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice")

    # Interact
    kitty.navigate_down(2)
    kitty.select_current()

    # Assert
    kitty.assert_selection_count(1)

    # Cleanup
    kitty.quit_app()
```

### E2E Fixtures

Defined in `tests/e2e/conftest.py`:
- `kitty` - KittyController with automatic cleanup
- `listpick_with_simple_data` - Pre-loaded instance
- Path fixtures for test data files (simple_data_path, numbers_data_path, etc.)

**Test Data:** Available in `tests/fixtures/e2e/`
- `simple.tsv` - Basic data (5 rows, 4 columns)
- `numbers.tsv` - Numeric data for sorting tests
- `empty.tsv` - Edge case testing

### Debugging E2E Tests

**Automatic Screenshots:**
- Saved to `test_screenshots/` on test failure
- Includes timestamp for debugging

**Manual Debugging:**
```python
# Capture screen content
screen = kitty.get_screen_text()
print(screen)

# Manual screenshot
kitty.save_screenshot("debug.txt")

# Verbose mode
./scripts/run_e2e_tests.sh -v -s
```

### E2E Best Practices

1. **Test Isolation** - Each test gets fresh kitty instance with automatic cleanup
2. **Robust Waiting** - Use `wait_for_text()` instead of fixed sleeps
3. **Context Manager** - Ensures cleanup even on test failure
4. **High-Level Abstractions** - Use methods like `navigate_down(3)` instead of repeated `send_text("j")`

## Test Markers

Tests are categorized with pytest markers:

- `@pytest.mark.unit` - Pure unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.smoke` - Quick smoke tests
- `@pytest.mark.requires_kitty` - Tests requiring kitty terminal

## Coverage Reports

```bash
# Generate terminal coverage report
./scripts/run_tests.sh

# Generate HTML coverage report
./scripts/run_tests.sh --cov-report=html
open htmlcov/index.html
```