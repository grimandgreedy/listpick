#!/bin/python
# -*- coding: utf-8 -*-
"""
Create a Picker with a dynamic footer string that shows the current time, updating once per second.

Author: GrimAndGreedy
License: MIT
"""

from listpick.listpick_app import Picker, close_curses, start_curses
from datetime import datetime


l = [["Time"], ["in"], ["footer"], ["string"]]

stdscr = start_curses()
x = Picker(
        stdscr = stdscr,
        items = l,
        title="Footer string example",
        footer_string_auto_refresh=True,
        footer_timer=1.0,
        footer_string_refresh_function=lambda:str(datetime.now()).split('.')[0],
    )
selected_indices, opts, picker_data = x.run()

close_curses(stdscr)

print(f"Selected: {selected_indices}")
print(f"Opts: {opts}")
