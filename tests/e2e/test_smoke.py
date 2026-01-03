"""
Smoke tests for basic listpick functionality.

These tests verify that the application launches, basic navigation works,
and the app can exit cleanly.
"""
import pytest
import time


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.smoke
def test_launch_navigate_exit(kitty, simple_data_path):
    """
    Test basic launch, navigation, and exit.

    This is the most basic E2E test - verifies that:
    - App launches successfully
    - Data loads and displays
    - Basic navigation works (j/k/G/g)
    - App exits cleanly
    """
    # Launch app
    kitty.launch_listpick(["-i", str(simple_data_path)])

    # Wait for app to load
    kitty.wait_for_text("Alice", timeout=3)

    # Verify header is displayed
    kitty.assert_text_present("Name")
    kitty.assert_text_present("Age")

    # Navigate down
    kitty.navigate_down(2)
    time.sleep(0.2)
    kitty.assert_text_present("Charlie")

    # Navigate up
    kitty.navigate_up(1)
    time.sleep(0.2)
    kitty.assert_text_present("Bob")

    # Navigate to bottom
    kitty.navigate_to_bottom()
    time.sleep(0.2)
    # Eve should be visible (last item)
    screen = kitty.get_screen_text()
    assert "Eve" in screen

    # Navigate to top
    kitty.navigate_to_top()
    time.sleep(0.2)
    kitty.assert_text_present("Alice")

    # Exit cleanly
    kitty.quit_app()

    # Should return to shell
    time.sleep(0.5)
    screen = kitty.get_screen_text()
    # Shell prompt should be visible ($ or %)
    assert "$" in screen or "%" in screen or ">" in screen


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.smoke
def test_load_multiple_files(kitty, simple_data_path, numbers_data_path):
    """
    Test loading multiple files and switching between them.

    Verifies:
    - Multiple files can be loaded
    - Switching between files works (}/})
    - Each file shows correct data
    """
    # Launch with 2 files
    kitty.launch_listpick(["-i", str(simple_data_path), str(numbers_data_path)])

    # Wait for first file to load
    kitty.wait_for_text("Alice", timeout=3)

    # Verify first file (simple.tsv) is displayed
    kitty.assert_text_present("Alice")
    kitty.assert_text_present("Name")

    # Switch to next file (})
    kitty.send_text("}")
    time.sleep(0.3)

    # Should now show numbers.tsv
    kitty.wait_for_text("ID", timeout=2)
    kitty.assert_text_present("Value")

    # Should not show simple.tsv data anymore
    kitty.assert_text_absent("Alice")

    # Switch back to previous file ({)
    kitty.send_text("{")
    time.sleep(0.3)

    # Should show simple.tsv again
    kitty.wait_for_text("Alice", timeout=2)
    kitty.assert_text_present("Name")

    # Exit
    kitty.quit_app()
