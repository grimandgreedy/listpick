#!/bin/python
# -*- coding: utf-8 -*-
"""
build_help.py

Author: GrimAndGreedy
License: MIT
"""

from keys import picker_keys
from listpick.listpick_app import Picker, start_curses, close_curses

import curses

def build_help_rows(keys_dict: dict) -> list[list[str]]:
    """ Build help rows based on the keys_dict. """
    ## Key names
    special_keys = {

            27: "Escape",
            353: "Shift+Tab",
            curses.KEY_END: "END",
            curses.KEY_HOME: "HOME",
            curses.KEY_PPAGE: "Page Up",
            curses.KEY_NPAGE: "Page Down",
            curses.KEY_UP: "ArrowUp",
            curses.KEY_DOWN: "ArrowDown",
            curses.KEY_RIGHT: "ArrowRight",
            curses.KEY_LEFT: "ArrowLeft",
            ord(' '): "Space",
            curses.KEY_ENTER: "RETURN",
            ord('\n'): "\n",
            curses.KEY_DC: "Delete",
    }

    # Ctrl + [a-z]
    for i in range(26):
        special_keys[i+1] = f"Ctrl+{chr(ord('a')+i)}"

    # F1-F12
    for i in range(12):
        special_keys[curses.KEY_F1+i] = f"F{i+1}"

    ## Key descriptions
    help_descriptions = {
        "refresh":                          "Refresh the screen.",
        "help":                             "Open help.",
        "exit":                             "Exit picker instance.",
        "full_exit":                        "Immediate exit to terminal.",
        "move_column_left":                 "Move column left.",
        "move_column_right":                "Move column right.",
        "cursor_down":                      "Cursor down.",
        "cursor_up":                        "Cursor up.",
        "half_page_up":                     "Half page up.",
        "half_page_down":                   "Half page down.",
        "page_up":                          "Page up.",
        "page_down":                        "Page down.",
        "cursor_bottom":                    "Send cursor to bottom of list.",
        "cursor_top":                       "Send cursor to top of list.",
        "five_up":                          "Five up.",
        "five_down":                        "Five down.",
        "toggle_select":                    "Toggle selection.",
        "select_all":                       "Select all.",
        "select_none":                      "Select none.",
        "visual_selection_toggle":          "Toggle visual selection.",
        "visual_deselection_toggle":        "Toggle visual deselection.",
        "enter":                            "Accept selections.",
        "redraw_screen":                    "Redraw screen.",
        "cycle_sort_method":                "Cycle through sort methods.",
        "cycle_sort_method_reverse":        "Cycle through sort methods (reverse)",
        "cycle_sort_order":                 "Toggle sort order.",
        "delete":                           "Delete dialaogue.",
        "decrease_lines_per_page":          "Decrease lines per page.",
        "increase_lines_per_page":          "Increase lines per page.",
        "increase_column_width":            "Increase column width.",
        "decrease_column_width":            "Decrease column width.",
        "filter_input":                     "Filter rows.",
        "search_input":                     "Search.",
        "settings_input":                   "Settings input.",
        "settings_options":                 "Settings options dialogue.",
        "continue_search_forward":          "Continue search forwards.",
        "continue_search_backward":         "Continue search backwards.",
        "cancel":                           "Cancel; escape.",
        "opts_input":                       "Options input.",
        "opts_select":                      "Options select dialogue.",
        "mode_next":                        "Cycle through modes forwards.",
        "mode_prev":                        "Cycle through modes backwards.",
        "pipe_input":                       "Pipe selected cells from selected rows.",
        "reset_opts":                       "Reset options.",
        "col_select":                       "Select column.",
        "col_select_next":                  "Select next column.",
        "col_select_prev":                  "Select previous column.",
        "col_hide":                         "Hide column.",
        "edit":                             "Edit cell.",
        "edit_picker":                      "Edit cell from options dialogue.",
        "edit_ipython":                     "Edit current data with ipython.",
        "copy":                             "Copy selections.",
        "save":                             "Save selections.",
        "load":                             "Load from file.",
        "open":                             "Open from file.",
        "toggle_footer":                    "Toggle footer.",
        "notification_toggle":              "Toggle empty notification.",
        "redo":                             "Redo.",
        "undo":                             "Undo.",
    }

    # [[key_name, key_function_description], ...]
    items = []
    for val, keys in keys_dict.items():
        row = [[chr(int(key)) if key not in special_keys else special_keys[key] for key in keys], help_descriptions[val]]
        items.append(row)

    return items

items = build_help_rows(picker_keys)
stdscr = start_curses()
x = Picker(
        stdscr,
        items=items
        )
x.run()

close_curses(stdscr)
