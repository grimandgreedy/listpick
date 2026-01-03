"""
End-to-end tests for editing workflows.

Tests cell editing, row operations, and file saving.
"""
import pytest
import time
import shutil
from pathlib import Path


@pytest.mark.e2e
@pytest.mark.slow
def test_add_row_edit_save(kitty, simple_data_path, tmp_path):
    """
    Test adding a row, editing it, saving, and verifying changes.

    Workflow:
    1. Copy test file to temp location
    2. Open in listpick
    3. Go to last row (G)
    4. Add row below (=)
    5. Go to last row again (G)
    6. Edit cell (e)
    7. Enter text and save (testcelldata + Return)
    8. Save file (Ctrl+s)
    9. Exit (q)
    10. Verify file has new row with expected data
    11. Cleanup temp file
    """
    # Copy test file to temp location (don't modify original)
    temp_file = tmp_path / "editable_simple.tsv"
    shutil.copy(simple_data_path, temp_file)

    # Read original file to know expected content
    with open(simple_data_path, 'r') as f:
        original_lines = f.readlines()
    original_line_count = len(original_lines)

    # Launch listpick with temp file
    kitty.launch_listpick(["-i", str(temp_file)])

    # Wait for app to load
    kitty.wait_for_text("Alice", timeout=3)

    # Go to last row (G)
    kitty.send_text("G")
    time.sleep(0.2)

    # Verify we're at the last row (Eve should be visible)
    kitty.assert_text_present("Eve")

    # Add row below (=)
    kitty.send_text("=")
    time.sleep(0.3)  # Wait for row to be added

    # Go to last row again (G) - should now be the new row
    kitty.send_text("G")
    time.sleep(0.2)

    # Edit cell (e)
    kitty.send_text("e")
    time.sleep(0.3)  # Wait for edit mode

    # Type text and confirm
    kitty.send_text("testcelldata")
    kitty.send_key("return")
    time.sleep(0.2)

    # Verify the text appears in the cell
    kitty.assert_text_present("testcelldata")

    # Save file (Ctrl+s) - save the changes
    kitty.send_key("ctrl+s")
    time.sleep(0.5)  # Wait for save

    # Exit (q)
    kitty.quit_app()
    time.sleep(0.3)

    # Verify file was modified correctly
    with open(temp_file, 'r') as f:
        modified_content = f.read()

    # File should contain our test data
    assert "testcelldata" in modified_content, \
        f"Expected 'testcelldata' in file, got: {modified_content}"

    # Verify last line contains testcelldata
    modified_lines = [line for line in modified_content.split('\n') if line.strip()]
    last_line = modified_lines[-1].strip()
    assert "testcelldata" in last_line, \
        f"Expected 'testcelldata' in last line, got: {last_line}"

    # First cell of last line should be testcelldata
    last_line_cells = last_line.split('\t')
    assert last_line_cells[0] == "testcelldata", \
        f"Expected first cell to be 'testcelldata', got: {last_line_cells[0]}"

    # Cleanup - temp_path is automatically cleaned up by pytest
    # but we'll explicitly remove the file to be sure
    if temp_file.exists():
        temp_file.unlink()


@pytest.mark.e2e
@pytest.mark.slow
def test_edit_existing_cell(kitty, simple_data_path, tmp_path):
    """
    Test editing an existing cell and saving changes.

    Workflow:
    1. Copy test file to temp
    2. Open in listpick
    3. Navigate to a cell
    4. Edit cell (e)
    5. Replace content
    6. Save (Ctrl+s)
    7. Exit (q)
    8. Verify changes
    """
    # Copy test file to temp location
    temp_file = tmp_path / "editable_for_modify.tsv"
    shutil.copy(simple_data_path, temp_file)

    # Launch listpick
    kitty.launch_listpick(["-i", str(temp_file)])
    kitty.wait_for_text("Alice", timeout=3)

    # Edit first cell (Alice)
    kitty.send_text("e")
    time.sleep(0.3)

    # Clear existing content and type new text
    # Select all and replace
    kitty.send_key("ctrl+a")
    time.sleep(0.1)
    kitty.send_text("ModifiedName")
    kitty.send_key("return")
    time.sleep(0.2)

    # Verify modification appears
    kitty.assert_text_present("ModifiedName")
    # Note: Alice might still appear elsewhere (e.g., in other rows or history)
    # so we'll verify the replacement by checking the file content later

    # Save
    kitty.send_key("ctrl+s")
    time.sleep(0.5)

    # Exit
    kitty.quit_app()

    # Verify file was saved correctly
    with open(temp_file, 'r') as f:
        lines = f.readlines()

    # Find the data lines (skip header and empty lines)
    data_lines = [line.strip() for line in lines if line.strip() and not line.startswith("Name\t")]

    assert "ModifiedName" in str(data_lines), "ModifiedName not found in saved file"
    # Check that the first data line starts with ModifiedName
    first_data_line = data_lines[0] if data_lines else ""
    assert first_data_line.startswith("ModifiedName"), \
        f"Expected first data line to start with 'ModifiedName', got: {first_data_line}"

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()


@pytest.mark.e2e
@pytest.mark.slow
def test_quit_without_saving_modified_file(kitty, simple_data_path, tmp_path):
    """
    Test quitting with unsaved changes shows warning.

    Workflow:
    1. Open file
    2. Make edit
    3. Try to quit without saving
    4. Verify warning or that changes are not saved
    5. Force quit with Ctrl+c
    """
    # Copy test file
    temp_file = tmp_path / "editable_no_save.tsv"
    shutil.copy(simple_data_path, temp_file)

    # Read original content
    with open(temp_file, 'r') as f:
        original_content = f.read()

    # Launch listpick
    kitty.launch_listpick(["-i", str(temp_file)])
    kitty.wait_for_text("Alice", timeout=3)

    # Make an edit
    kitty.send_text("e")
    time.sleep(0.3)
    kitty.send_key("ctrl+a")
    kitty.send_text("Changed")
    kitty.send_key("return")
    time.sleep(0.2)

    # Try to quit (q)
    kitty.send_text("q")
    time.sleep(0.5)

    # Check if warning appears or if it closed the file
    screen = kitty.get_screen_text()

    # If there's a warning, it might contain words like "unsaved", "modified", "save", etc.
    # Or it might have just closed the file (multi-file behavior)
    # Force quit anyway with Ctrl+c to ensure cleanup
    kitty.send_key("ctrl+c")
    time.sleep(0.5)

    # Verify file was NOT saved (original content preserved)
    with open(temp_file, 'r') as f:
        final_content = f.read()

    assert final_content == original_content, \
        "File content should not change when quitting without save"
    assert "Changed" not in final_content, \
        "Modified data should not be in file"

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()


@pytest.mark.e2e
@pytest.mark.slow
def test_add_multiple_rows_and_edit(kitty, simple_data_path, tmp_path):
    """
    Test adding multiple rows and editing them.

    Workflow:
    1. Open file
    2. Add row (=)
    3. Edit new row
    4. Add another row (=)
    5. Edit second new row
    6. Save
    7. Verify both rows added
    """
    # Copy test file
    temp_file = tmp_path / "editable_multi_rows.tsv"
    shutil.copy(simple_data_path, temp_file)

    # Launch listpick
    kitty.launch_listpick(["-i", str(temp_file)])
    kitty.wait_for_text("Alice", timeout=3)

    # Go to last row
    kitty.send_text("G")
    time.sleep(0.2)

    # Add first row
    kitty.send_text("=")
    time.sleep(0.3)

    # Edit it
    kitty.send_text("G")  # Go to new row
    time.sleep(0.2)
    kitty.send_text("e")
    time.sleep(0.3)
    kitty.send_text("FirstNewRow")
    kitty.send_key("return")
    time.sleep(0.2)

    # Add second row
    kitty.send_text("=")
    time.sleep(0.3)

    # Edit it
    kitty.send_text("G")  # Go to newest row
    time.sleep(0.2)
    kitty.send_text("e")
    time.sleep(0.3)
    kitty.send_text("SecondNewRow")
    kitty.send_key("return")
    time.sleep(0.2)

    # Save
    kitty.send_key("ctrl+s")
    time.sleep(0.5)

    # Exit
    kitty.quit_app()

    # Verify file has both new rows
    with open(temp_file, 'r') as f:
        content = f.read()

    # Check that both new rows are in the file
    assert "FirstNewRow" in content, "First new row not found"
    assert "SecondNewRow" in content, "Second new row not found"

    # Verify they appear in the right order (FirstNewRow before SecondNewRow)
    first_pos = content.find("FirstNewRow")
    second_pos = content.find("SecondNewRow")
    assert first_pos < second_pos, \
        f"FirstNewRow should appear before SecondNewRow in file"

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()
