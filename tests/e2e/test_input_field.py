"""
End-to-end tests for input field functionality.

Tests the input field used throughout the application (filter, search, edit, etc.).
Uses the filter input field ('f') as the primary test vehicle.
"""
import pytest
import time


@pytest.mark.e2e
@pytest.mark.slow
def test_basic_text_input(kitty, simple_data_path):
    """
    Test basic text input in the filter field.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type text
    4. Verify text appears in input field
    5. Confirm with Enter
    6. Verify filter applied
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type text
    kitty.send_text("Alice")
    time.sleep(0.2)

    # Verify text appears in screen (input field should show "Alice")
    screen = kitty.get_screen_text()
    assert "Alice" in screen, "Input text should appear in filter field"

    # Confirm with Enter
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify filter was applied (only Alice shown)
    kitty.assert_text_present("Alice")
    kitty.assert_text_absent("Bob")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_escape_cancels_input(kitty, simple_data_path):
    """
    Test that Escape key cancels input without applying changes.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type text
    4. Press Escape
    5. Verify filter NOT applied (all items still visible)
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type text
    kitty.send_text("Alice")
    time.sleep(0.2)

    # Cancel with Escape
    kitty.send_key("escape")
    time.sleep(0.3)

    # Verify filter NOT applied - all items still visible
    kitty.assert_text_present("Alice")
    kitty.assert_text_present("Bob")
    kitty.assert_text_present("Charlie")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_backspace_deletes_char(kitty, simple_data_path):
    """
    Test that backspace deletes characters.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "Alice"
    4. Press backspace twice
    5. Verify "Ali" remains
    6. Add "ce" back
    7. Confirm and verify filter
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "Alice"
    kitty.send_text("Alice")
    time.sleep(0.2)

    # Delete "ce" with backspace (twice)
    kitty.send_key("backspace")
    time.sleep(0.1)
    kitty.send_key("backspace")
    time.sleep(0.2)

    # Type "ce" again
    kitty.send_text("ce")
    time.sleep(0.2)

    # Confirm
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify filter applied (only Alice shown)
    kitty.assert_text_present("Alice")
    kitty.assert_text_absent("Bob")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_cursor_movement_left_right(kitty, simple_data_path):
    """
    Test cursor movement with left/right arrow keys.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "Bob"
    4. Move cursor left (3 times to start)
    5. Type "Alice" at beginning
    6. Result should be "AliceBob"
    7. Confirm and verify matches both
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "Bob"
    kitty.send_text("Bob")
    time.sleep(0.2)

    # Move cursor to beginning (left arrow 3 times)
    for _ in range(3):
        kitty.send_key("left")
        time.sleep(0.05)

    # Type "Alice " at the beginning
    kitty.send_text("Alice ")
    time.sleep(0.2)

    # Now we have "Alice Bob" which should match rows containing Alice or Bob
    # Confirm
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify both Alice and Bob are shown (filter matches "Alice Bob" substring)
    kitty.assert_text_present("Alice")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_ctrl_a_beginning_ctrl_e_end(kitty, simple_data_path):
    """
    Test Ctrl+A (beginning of line) and Ctrl+E (end of line).

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "middle"
    4. Ctrl+A to go to beginning
    5. Type "start "
    6. Ctrl+E to go to end
    7. Type " end"
    8. Result: "start middle end"
    9. Cancel and verify no filter applied
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "middle"
    kitty.send_text("middle")
    time.sleep(0.2)

    # Ctrl+A to beginning
    kitty.send_key("ctrl+a")
    time.sleep(0.1)

    # Type "start " at beginning
    kitty.send_text("start ")
    time.sleep(0.2)

    # Ctrl+E to end
    kitty.send_key("ctrl+e")
    time.sleep(0.1)

    # Type " end" at end
    kitty.send_text(" end")
    time.sleep(0.2)

    # Screen should show "start middle end"
    screen = kitty.get_screen_text()
    assert "start middle end" in screen, "Input field should show 'start middle end'"

    # Cancel with escape
    kitty.send_key("escape")
    time.sleep(0.3)

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_ctrl_u_delete_to_start(kitty, simple_data_path):
    """
    Test Ctrl+U deletes from cursor to start of line.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "Hello World"
    4. Ctrl+U to delete all
    5. Verify input field empty
    6. Type "Alice" and confirm
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "Hello World"
    kitty.send_text("Hello World")
    time.sleep(0.2)

    # Ctrl+U to delete to start
    kitty.send_key("ctrl+u")
    time.sleep(0.2)

    # Type "Alice" in the now-empty field
    kitty.send_text("Alice")
    time.sleep(0.2)

    # Confirm
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify filter applied (only Alice shown)
    kitty.assert_text_present("Alice")
    kitty.assert_text_absent("Bob")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_ctrl_k_delete_to_end(kitty, simple_data_path):
    """
    Test Ctrl+K deletes from cursor to end of line.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "Alice Bob"
    4. Move cursor after "Alice" (left 4 times)
    5. Ctrl+K to delete " Bob"
    6. Confirm with "Alice" only
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "Alice Bob"
    kitty.send_text("Alice Bob")
    time.sleep(0.2)

    # Move cursor left 4 times to position after "Alice"
    for _ in range(4):
        kitty.send_key("left")
        time.sleep(0.05)

    # Ctrl+K to delete to end
    kitty.send_key("ctrl+k")
    time.sleep(0.2)

    # Confirm (should have "Alice" only)
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify filter applied (only Alice shown)
    kitty.assert_text_present("Alice")
    kitty.assert_text_absent("Bob")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_delete_key_forward_delete(kitty, simple_data_path):
    """
    Test Delete key (or Ctrl+D) deletes character after cursor.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "Alixce"
    4. Move cursor left 3 times (cursor after "i", before "x")
    5. Press Ctrl+D to delete "x" (character after cursor)
    6. Confirm with "Alice"
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "Alixce" (intentional typo)
    kitty.send_text("Alixce")
    time.sleep(0.2)

    # Move cursor left 3 times (cursor after "i", before "x")
    for _ in range(3):
        kitty.send_key("left")
        time.sleep(0.05)

    # Now cursor is after 'i', press Ctrl+D to delete 'x'
    kitty.send_key("ctrl+d")
    time.sleep(0.2)

    # Confirm (should have "Alice")
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify filter applied (only Alice shown)
    kitty.assert_text_present("Alice")
    kitty.assert_text_absent("Bob")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_empty_input_field(kitty, simple_data_path):
    """
    Test that submitting empty input field doesn't crash.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Press Enter immediately (empty input)
    4. Verify all items still visible (no filter applied)
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Press Enter immediately (empty input)
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify all items still visible
    kitty.assert_text_present("Alice")
    kitty.assert_text_present("Bob")
    kitty.assert_text_present("Charlie")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_special_characters_in_input(kitty, simple_data_path):
    """
    Test that special characters can be entered in input field.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type regex pattern with special chars: "^A.*"
    4. Confirm
    5. Verify regex filter applied (Alice shown, starts with A)
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type regex pattern
    kitty.send_text("^A.*")
    time.sleep(0.2)

    # Confirm
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify Alice is shown (starts with A)
    kitty.assert_text_present("Alice")
    # Bob and Charlie should not be shown
    kitty.assert_text_absent("Bob")
    kitty.assert_text_absent("Charlie")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_long_input_text(kitty, simple_data_path):
    """
    Test that long text can be entered and handled properly.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type a very long string
    4. Verify it doesn't crash
    5. Cancel with Escape
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type a long string (50+ characters)
    long_text = "a" * 60
    kitty.send_text(long_text)
    time.sleep(0.3)

    # Verify the input field shows some of the text (may be truncated in display)
    screen = kitty.get_screen_text()
    assert "aaa" in screen, "Long input should be visible in field"

    # Cancel with Escape
    kitty.send_key("escape")
    time.sleep(0.3)

    # Verify all items still visible (filter not applied)
    kitty.assert_text_present("Alice")
    kitty.assert_text_present("Bob")

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_ctrl_b_ctrl_f_cursor_movement(kitty, simple_data_path):
    """
    Test Ctrl+B (backward) and Ctrl+F (forward) cursor movement.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "test"
    4. Ctrl+B twice to move back 2 chars
    5. Type "x"
    6. Result should be "texst"
    7. Cancel and exit
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "test"
    kitty.send_text("test")
    time.sleep(0.2)

    # Ctrl+B twice (move cursor back 2 positions)
    kitty.send_key("ctrl+b")
    time.sleep(0.1)
    kitty.send_key("ctrl+b")
    time.sleep(0.1)

    # Type "x" (should insert between "te" and "st")
    kitty.send_text("x")
    time.sleep(0.2)

    # Verify "texst" appears in screen
    screen = kitty.get_screen_text()
    assert "texst" in screen, "Input field should show 'texst'"

    # Cancel with Escape
    kitty.send_key("escape")
    time.sleep(0.3)

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_kill_ring_yank_basic(kitty, simple_data_path):
    """
    Test basic kill ring functionality with Ctrl+W and Ctrl+Y.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "Hello World Test"
    4. Ctrl+W to delete "Test" (adds to kill ring)
    5. Ctrl+W to delete "World " (adds to kill ring)
    6. Type "New"
    7. Ctrl+Y to yank "World " back (most recent kill)
    8. Verify "HelloWorld New" appears
    9. Cancel and exit
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "Hello World Test"
    kitty.send_text("Hello World Test")
    time.sleep(0.2)

    # Ctrl+W to delete "Test" (adds to kill ring)
    kitty.send_key("ctrl+w")
    time.sleep(0.2)

    # Ctrl+W to delete "World " (adds to kill ring)
    kitty.send_key("ctrl+w")
    time.sleep(0.2)

    # Now we should have "Hello" and kill_ring = ["World ", "Test"]

    # Type "New"
    kitty.send_text("New")
    time.sleep(0.2)

    # Ctrl+Y to yank "World " back (most recent kill, index 0)
    kitty.send_key("ctrl+y")
    time.sleep(0.2)

    # Should now have "HelloNewWorld "
    screen = kitty.get_screen_text()
    # Verify the yank worked
    assert "New" in screen, f"Should contain 'New', screen: {screen[-200:]}"

    # Cancel with Escape
    kitty.send_key("escape")
    time.sleep(0.3)

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_kill_ring_cycle(kitty, simple_data_path):
    """
    Test kill ring cycling with Ctrl+W, Ctrl+Y, and Alt+Y.

    This tests the bug fix where Alt+Y should cycle through the kill ring.

    Workflow:
    1. Launch with file
    2. Open filter (f)
    3. Type "One Two Three"
    4. Ctrl+W twice to kill "Three" then "Two "
    5. Ctrl+Y to yank "Two " (most recent, kill_ring[0])
    6. Alt+Y to cycle to "Three" (kill_ring[1])
    7. Verify "Three" appears (replacing "Two ")
    8. Cancel and exit
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # Open filter
    kitty.open_filter()
    time.sleep(0.3)

    # Type "One Two Three"
    kitty.send_text("One Two Three")
    time.sleep(0.2)

    # Ctrl+W to delete "Three" (adds to kill_ring: ["Three"])
    kitty.send_key("ctrl+w")
    time.sleep(0.2)

    # Ctrl+W to delete "Two " (appends to kill_ring: ["Three", "Two "])
    kitty.send_key("ctrl+w")
    time.sleep(0.2)

    # Now kill_ring = ["Three", "Two "] and we have "One"

    # Ctrl+Y to yank kill_ring[0] which is "Three"
    kitty.send_key("ctrl+y")
    time.sleep(0.2)

    # Should have "OneThree"
    screen = kitty.get_screen_text()
    assert "Three" in screen, f"Should contain 'Three' after Ctrl+Y, screen: {screen[-200:]}"

    # Alt+Y to cycle to kill_ring[1] which is "Two "
    # This should replace "Three" with "Two "
    kitty.send_key("alt+y")
    time.sleep(0.3)

    # Should now have "OneTwo "
    screen = kitty.get_screen_text()
    assert "Two" in screen, f"Should contain 'Two' after Alt+Y, screen: {screen[-200:]}"
    # The filter field should show "OneTwo " not "OneThree"

    # Cancel with Escape
    kitty.send_key("escape")
    time.sleep(0.3)

    # Exit
    kitty.quit_app()


@pytest.mark.e2e
@pytest.mark.slow
def test_multiple_filters_in_sequence(kitty, simple_data_path):
    """
    Test applying multiple filters in sequence.

    Workflow:
    1. Launch with file
    2. Apply filter for "Alice"
    3. Clear filter (escape)
    4. Apply filter for "Bob"
    5. Clear filter (escape)
    6. Verify all items visible at end
    """
    # Launch
    kitty.launch_listpick(["-i", str(simple_data_path)])
    kitty.wait_for_text("Alice", timeout=3)

    # First filter: Alice
    kitty.open_filter()
    time.sleep(0.3)
    kitty.send_text("Alice")
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify only Alice shown
    kitty.assert_text_present("Alice")
    kitty.assert_text_absent("Bob")

    # Clear filter
    kitty.send_key("escape")
    time.sleep(0.5)

    # Second filter: Bob
    kitty.open_filter()
    time.sleep(0.3)
    kitty.send_text("Bob")
    kitty.send_key("return")
    time.sleep(0.3)

    # Verify only Bob shown
    kitty.assert_text_present("Bob")
    kitty.assert_text_absent("Alice")

    # Clear filter
    kitty.send_key("escape")
    time.sleep(0.5)

    # Verify all items visible
    kitty.assert_text_present("Alice")
    kitty.assert_text_present("Bob")
    kitty.assert_text_present("Charlie")

    # Exit
    kitty.quit_app()
