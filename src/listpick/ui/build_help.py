#!/bin/python
# -*- coding: utf-8 -*-
"""
build_help.py

Author: GrimAndGreedy
License: MIT
"""

from listpick.ui.keys import picker_keys

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
            383: "Shift+Delete",
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
        "delete":                           "Delete row.",
        "delete_column":                    "Delete column.",
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
        "scroll_right":                     "Scroll right.",
        "scroll_left":                      "Scroll left.",
        "scroll_far_right":                 "Scroll to the end of the column set.",
        "scroll_far_left":                  "Scroll to the left home.",
        "add_column":                       "Insert column before cursor.",
        "add_row":                          "Insert row before cursor.",
    }
    sections = {
        "Navigation:": [ "cursor_down", "cursor_up", "half_page_up", "half_page_down", "page_up", "page_down", "cursor_bottom", "cursor_top", "five_up", "five_down", "scroll_right", "scroll_left", "scroll_far_right", "scroll_far_left" ],
        "Selection:": [ "toggle_select", "select_all", "select_none", "visual_selection_toggle", "visual_deselection_toggle", "enter" ],
        "UI:": [ "toggle_footer", "redraw_screen", "decrease_lines_per_page", "increase_lines_per_page", "increase_column_width", "decrease_column_width", "notification_toggle" ],
        "Sort:": [ "cycle_sort_method", "cycle_sort_method_reverse", "cycle_sort_order", ] ,
        "Data manipulation:": [ "delete", "delete_column", "edit", "edit_picker", "edit_ipython", "add_column", "add_row" ],
        "Filter and sort:": [ "filter_input", "search_input", "continue_search_forward", "continue_search_backward", ] ,
        "Settings:": [ "settings_input", "settings_options" ],
        "Cancel:": [ "opts_input", "opts_select", "mode_next", "mode_prev", "pipe_input", "reset_opts", "col_select", "col_select_next", "col_select_prev", "col_hide" ],
        "Save, load, and copy:": [ "save", "load", "copy", "open" ],
        "Misc:": [ "redo", "undo", "refresh", "help", "exit", "full_exit", "move_column_left", "move_column_right" ],
    }

    ## Add any keys not in section keys to misc.
    for key, desc in help_descriptions.items():
        found = False
        for section in sections:
            if key in sections[section]:
                found = True
                break
        if not found:
            sections["Misc:"].append(key)

    items = []
    for section_name, section_operations in sections.items():
        section_rows = []
        
        for operation in section_operations:
            try:
                keys = [chr(int(key)) if key not in special_keys else special_keys[key] for key in keys_dict[operation]]
                description = help_descriptions[operation]
                row = [f"    {str(keys)[1:-1]}", description]
                section_rows.append(row)
            except:
                pass
        if section_rows:
            items.append([section_name, ""])
            items += section_rows
            items.append(["",""])

    # [[key_name, key_function_description], ...]
    # for val, keys in keys_dict.items():
    #     try: 
    #         row = [[chr(int(key)) if key not in special_keys else special_keys[key] for key in keys], help_descriptions[val]]
    #         items.append(row)
    #     except:
    #         pass

    return items

if __name__ == "__main__":
    from listpick.listpick_app import Picker, start_curses, close_curses
    items = build_help_rows(picker_keys)
    stdscr = start_curses()
    x = Picker(
        stdscr,
        items=items
    )
    x.run()

    close_curses(stdscr)
