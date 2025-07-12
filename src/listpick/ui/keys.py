#!/bin/python
# -*- coding: utf-8 -*-
"""
keys.py
Define key dictionary for Picker object.

Author: GrimAndGreedy
License: MIT
"""

import curses

picker_keys = {
    "refresh":                          [curses.KEY_F5],
    "help":                             [ord('?')],
    "exit":                             [ord('q')],
    "full_exit":                        [3], # Ctrl+c
    "move_column_left":                 [ord('{')],
    "move_column_right":                [ord('}')],
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2], # Ctrl+b
    "page_down":                        [curses.KEY_NPAGE, 6], # Ctrl+f
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "toggle_select":                    [ord(' ')],
    "select_all":                       [ord('m'), 1], # Ctrl-a
    "select_none":                      [ord('M'), 18],   # Ctrl-r
    "visual_selection_toggle":          [ord('v')],
    "visual_deselection_toggle":        [ord('V')],
    "enter":                            [ord('\n'), curses.KEY_ENTER],
    "redraw_screen":                    [12], # Ctrl-l
    "cycle_sort_method":                [ord('s')],
    "cycle_sort_method_reverse":        [ord('S')],
    "cycle_sort_order":                 [ord('t')],
    "delete":                           [curses.KEY_DC],
    "delete_column":                    [383], # Shift+Delete
    "decrease_lines_per_page":          [ord('-')],
    "increase_lines_per_page":          [ord('+')],
    "increase_column_width":            [ord(']')],
    "decrease_column_width":            [ord('[')],
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "settings_input":                   [ord('`')],
    "settings_options":                 [ord('~')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('I')],
    "cancel":                           [27], # Escape key
    "opts_input":                       [ord(':')],
    "opts_select":                      [ord('o')],
    "mode_next":                        [9], # Tab key
    "mode_prev":                        [353], # Shift+Tab key
    "pipe_input":                       [ord('|')],
    "reset_opts":                       [ord('\\')],
    "col_select":                       [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')],
    "col_select_next":                             [ord('>')], 
    "col_select_prev":                             [ord('<')], 
    "col_hide":                         [ord('!'), ord('@'), ord('#'), ord('$'), ord('%'), ord('^'), ord('&'), ord('*'), ord('('), ord(')')],
    "edit":                             [ord('e')],
    "edit_picker":                      [ord('E')],
    "edit_ipython":                     [5], # Ctrl+e
    "copy":                             [ord('y')],
    "save":                             [19, ord('D')],  # Ctrl+s
    "load":                             [15], # Ctrl+o
    "open":                             [ord('O')], 
    "toggle_footer":                    [ord('_')], 
    "notification_toggle":              [ord('z')],
    "redo":                             [ord('.')],
    "undo":                             [26], # Ctrl+z
    "scroll_right":                     [ord('l'), curses.KEY_RIGHT],
    "scroll_left":                      [ord('h'), curses.KEY_LEFT],
    "scroll_far_right":                 [ord('L')],
    "scroll_far_left":                  [ord('H')],
    "add_column":                       [ord('+')],
    "add_row":                          [ord('=')],
}


help_keys = {
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "redraw_screen":                    [12], # Ctrl+l
    "cycle_sort_method":                [ord('s')],
    "cycle_sort_method_reverse":        [ord('S')],
    "cycle_sort_order":                 [ord('t')],
    "increase_column_width":            [ord(']')],
    "decrease_column_width":            [ord('[')],
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "settings_input":                   [ord('`')],
    "settings_options":                 [ord('~')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('I')],
    "cancel":                           [27], # Escape key
    "col_select":                       [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')],
    "col_select_next":                             [ord('>')], 
    "col_select_prev":                             [ord('<')], 
    "col_hide":                         [ord('!'), ord('@'), ord('#'), ord('$'), ord('%'), ord('^'), ord('&'), ord('*'), ord('('), ord(')')],
    "toggle_footer":                    [ord('_')], 
}



notification_keys = {
    "exit":                             [ord('q'), ord('h'), curses.KEY_ENTER, ord('\n'), ord(' '), 27],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "redraw_screen":                    [12], # Ctrl-l
}


menu_keys = {
    "help":                             [ord('?')],
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l')],
    "redraw_screen":                    [12], # Ctrl-l
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('I')],
    "cancel":                           [27], # Escape key
    "opts_input":                       [ord(':')],
    "mode_next":                        [9], # Tab key
    "mode_prev":                        [353], # Shift+Tab key
}


options_keys = {
    "exit":                             [ord('q'), ord('h')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2],
    "page_down":                        [curses.KEY_NPAGE, 6],
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "toggle_select":                    [ord(' ')],
    "select_all":                       [ord('m'), 1], # Ctrl-a
    "select_none":                      [ord('M'), 18],   # Ctrl-r
    "visual_selection_toggle":          [ord('v')],
    "visual_deselection_toggle":        [ord('V')],
    "enter":                            [ord('\n'), curses.KEY_ENTER, ord('l')],
    "redraw_screen":                    [12], # Ctrl-l
    "cycle_sort_method":                [ord('s')],
    "cycle_sort_method_reverse":        [ord('S')],
    "cycle_sort_order":                 [ord('t')],
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "settings_input":                   [ord('`')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('I')],
    "cancel":                           [27], # Escape key
    "col_select":                       [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')],
    "refresh":                          [curses.KEY_F5, curses.KEY_RESIZE],
}



edit_menu_keys = {
    "exit":                             [ord('q')],
    "full_exit":                        [3], # Ctrl+c
    "cursor_down":                      [ord('j'), curses.KEY_DOWN],
    "cursor_up":                        [ord('k'), curses.KEY_UP],
    "half_page_up":                     [ord('u')],
    "half_page_down":                   [ord('d')],
    "page_up":                          [curses.KEY_PPAGE, 2], # Ctrl+b
    "page_down":                        [curses.KEY_NPAGE, 6], # Ctrl+f
    "cursor_bottom":                    [ord('G'), curses.KEY_END],
    "cursor_top":                       [ord('g'), curses.KEY_HOME],
    "five_up":                          [ord('K')],
    "five_down":                        [ord('J')],
    "enter":                            [ord('\n'), curses.KEY_ENTER],
    "redraw_screen":                    [12], # Ctrl-l
    "cycle_sort_method":                [ord('s')],
    "cycle_sort_method_reverse":        [ord('S')],
    "cycle_sort_order":                 [ord('t')],
    "increase_column_width":            [ord(']')],
    "decrease_column_width":            [ord('[')],
    "filter_input":                     [ord('f')],
    "search_input":                     [ord('/')],
    "settings_input":                   [ord('`')],
    "settings_options":                 [ord('~')],
    "continue_search_forward":          [ord('n'), ord('i')],
    "continue_search_backward":         [ord('N'), ord('I')],
    "cancel":                           [27], # Escape key
    "opts_input":                       [ord(':')],
    "opts_select":                      [ord('o')],
    "mode_next":                        [9], # Tab key
    "mode_prev":                        [353], # Shift+Tab key
    "pipe_input":                       [ord('|')],
    "reset_opts":                       [ord('\\')],
    "col_select":                       [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')],
    "col_select_next":                             [ord('>'), ord('l')], 
    "col_select_prev":                             [ord('<'), ord('h')], 
    "col_hide":                         [ord('!'), ord('@'), ord('#'), ord('$'), ord('%'), ord('^'), ord('&'), ord('*'), ord('('), ord(')')],
    "edit":                             [ord('e')],
    "edit_picker":                      [ord('E')],
    "edit_ipython":                     [5], # Ctrl+e
    "copy":                             [ord('y')],
    "save":                             [19, ord('D')],  # Ctrl+s
    "load":                             [ord('L'), 15], # Ctrl+o
    "open":                             [ord('O')], 
    "toggle_footer":                    [ord('_')], 
}
