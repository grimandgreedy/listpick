from listpick.listpick_app import Picker, close_curses, start_curses

l = [["1", "2"], ["3", "4"]]
header=["Pericles", "Is Dead"]

stdscr = start_curses()
x = Picker(
        stdscr = stdscr,
        items = l,
        title="Test Picker",
        header=header,
        highlights=highlights,
    )
selected_indices, opts, picker_data = x.run()

close_curses(stdscr)

print(f"Selected: {selected_indices}")
print(f"Opts: {opts}")
