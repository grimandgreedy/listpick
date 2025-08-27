#!/bin/python
# -*- coding: utf-8 -*-
"""
pane_functions.py
Functions which are run by a listpick Picker to display data in a pane.

Author: GrimAndGreedy
License: MIT
"""

import curses
import os
from listpick.pane.pane_utils import get_file_attributes, get_graph_string, escape_ansi

def right_split_file_attributes(stdscr, x, y, w, h, state, row, cell, past_data: list = [], data: list = [], test: bool = False):
    """
    Display file attributes in right pane.
    """
    if test: return True

    os.chdir(os.path.expanduser("~/Downloads/new"))

    # Title
    title = "File attributes"
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

    # Separator
    for j in range(h):
        stdscr.addstr(j+y, x, ' ', curses.color_pair(state["colours_start"]+16))


    # Filename/cursor cell value
    stdscr.addstr(y+2, x+2, cell[:w-3])

    attributes = get_file_attributes(cell)
    for i, attr in enumerate(attributes):
        stdscr.addstr(y+3+i, x+4, attr[:w-5])

    return []

def right_split_graph(stdscr, x, y, w, h, state, row, cell, past_data: list = [], data: list = [], test: bool = False):
    """
    Display a graph of the data in right pane.

    data[0] = x_vals
    data[1] = y_vals
    data[2] = id
    """
    if test: return True

    # Title
    title = "Graph"
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

    # Separator
    for j in range(h):
        stdscr.addstr(j+y, x, ' ', curses.color_pair(state["colours_start"]+16))

    try:
        import plotille as plt
    except:
        s = f"No module named 'plotille'"
        stdscr.addstr(y+2, x+2, s[:w-2])
        return None


    # x_vals, y_vals = list(range(100)), [x**2 for x in range(100)]
    if data in [[], {}, None]:
        return None
    x_vals, y_vals = data[0], data[1]
    graph_str = get_graph_string(x_vals, y_vals, width=w-3-10, height=h-3)
    for i, s in enumerate(graph_str.split("\n")):
        s = escape_ansi(s)
        stdscr.addstr(y+2+i, x+2, s[:w-2])

    return []




def right_split_display_list(stdscr, x, y, w, h, state, row, cell, past_data: list = [], data: list = [], test: bool = False):
    """
    data[0]:str = title
    data[1]:list[str] = list of strings to display
    """
    if test: return True

    # Title
    title = data[0]
    if len(title) < w: title = f"{title:^{w}}"
    stdscr.addstr(y, x,title[:w], curses.color_pair(state["colours_start"]+4) | curses.A_BOLD)

    # Separator
    for j in range(h):
        stdscr.addstr(j+y, x, ' ', curses.color_pair(state["colours_start"]+16))

    if data in [[], {}, None]:
        return None

    items = data[1]
    number_to_display = min(len(items), h-3)
    for i in range(number_to_display):
        s = items[i]
        stdscr.addstr(y+1+i, x+2, s[:w-2])

    if number_to_display < len(items):
        stdscr.addstr(y+1+number_to_display, x+2, f" ... {len(items)-number_to_display} more"[:w-2])


    return []
