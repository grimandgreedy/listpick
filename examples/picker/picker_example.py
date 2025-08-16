import sys, os
from listpick.listpick_app import Picker, close_curses, start_curses

l = [["The", "many"], ["words", "of"]]
l += [["the", "Athenians"], ["I", "do"]]
l += [["not", "understand."], ["They", "said"]]
l += [["a great", "deal"], ["in praise", "of themselves"]]
l += [["but", "nowhere"], ["denied", "that they"]]
l += [["are", "injuring"], ["our", "allies"]]

header=["Pericles", "Is Dead"]

highlights = [
    {
        "match": "praise",
        "field": 0,
        "color": 8,
    },
    {
        "match": "theni..",
        "field": 1,
        "color": 9,
    },
    {
        "match": ".*",
        "row":   5,
        "field": 1,
        "color": 11,
    },
]

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
