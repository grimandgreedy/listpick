#!/bin/python
# -*- coding: utf-8 -*-
"""
picker_colours.py
Define colour options for listpick--default, help, and notification colours.

Author: GrimAndGreedy
License: MIT
"""

import curses

def get_colours(pick:int=0) -> dict[str, int]:
    """ Define colour options for listpick. """
    colours = [
        ### (0) Green header, green title, green modes, purple selected, blue cursor
    {
        'background': 232,
        'normal_fg': 253,
        'unselected_bg': 232,
        'unselected_fg': 253,
        'cursor_bg': 25,
        'cursor_fg': 253,
        'selected_bg': 135,
        'selected_fg': 253,
        'header_bg': 253,
        'header_fg': 232,
        'error_bg': 232,
        'error_fg': curses.COLOR_RED,
        'complete_bg': 232,
        'complete_fg': 82,
        'waiting_bg': 232,
        'waiting_fg': curses.COLOR_YELLOW,
        'active_bg': 232,
        'active_fg': 33,
        'paused_bg': 232,
        'paused_fg': 244,
        'search_bg': 162,
        'search_fg': 253,
        'active_input_bg': 253,
        'active_input_fg': 28,
        'modes_selected_bg': 28,
        'modes_selected_fg': 253,
        'modes_unselected_bg': 253,
        'modes_unselected_fg': 232,
        'title_bar': 28,
        'title_bg': 28,
        'title_fg': 253,
        'scroll_bar_bg': 247,
        'selected_header_column_bg': 247,
        'selected_header_column_fg': 232,
        'footer_bg': 28,
        'footer_fg': 253,
        'refreshing_bg': 28,
        'refreshing_fg': 253,
        'refreshing_inactive_bg': 28,
        'refreshing_inactive_fg': 232,
        '40pc_bg': 232,
        '40pc_fg': 166,
        'footer_string_bg': 28,
        'footer_string_fg': 253,
    },
        ### (1) Black and white
    {
        'background': 232,
        'normal_fg': 253,
        'unselected_bg': 232,
        'unselected_fg': 253,
        'cursor_bg': 253,
        'cursor_fg': 232,
        'selected_bg': 253,
        'selected_fg': 232,
        'header_bg': 253,
        'header_fg': 232,
        'error_bg': 232,
        'error_fg': 253,
        'complete_bg': 232,
        'complete_fg': 253,
        'waiting_bg': 232,
        'waiting_fg': 253,
        'active_bg': 232,
        'active_fg': 253,
        'paused_bg': 232,
        'paused_fg': 253,
        'search_bg': 253,
        'search_fg': 232,
        'active_input_bg': 232,
        'active_input_fg': 253,
        'modes_selected_bg': 253,
        'modes_selected_fg': 232,
        'modes_unselected_bg': 232,
        'modes_unselected_fg': 253,
        'title_bar': 232,
        'title_bg': 253,
        'title_fg': 232,
        'scroll_bar_bg': 253,
        'selected_header_column_bg': 232,
        'selected_header_column_fg': 253,
        'footer_bg': 253,
        'footer_fg': 232,
        'refreshing_bg': 253,
        'refreshing_fg': 232,
        'refreshing_inactive_bg': 232,
        'refreshing_inactive_fg': 253,
        '40pc_bg': 232,
        '40pc_fg': 253,
        'footer_string_bg': 253,
        'footer_string_fg': 232,
    },
        ### (2) Blue header, blue title, blue modes, purple selected, green cursor
    {
        'background': 232,
        'normal_fg': 253,
        'unselected_bg': 232,
        'unselected_fg': 253,
        'cursor_bg': 28,
        'cursor_fg': 253,
        'selected_bg': 135,
        'selected_fg': 253,
        'header_bg': 253,
        'header_fg': 232,
        'error_bg': 232,
        'error_fg': curses.COLOR_RED,
        'complete_bg': 232,
        'complete_fg': 82,
        'waiting_bg': 232,
        'waiting_fg': curses.COLOR_YELLOW,
        'active_bg': 232,
        'active_fg': 33,
        'paused_bg': 232,
        'paused_fg': 244,
        'search_bg': 162,
        'search_fg': 253,
        'active_input_bg': 253,
        'active_input_fg': 25,
        'modes_selected_bg': 25,
        'modes_selected_fg': 253,
        'modes_unselected_bg': 253,
        'modes_unselected_fg': 232,
        'title_bar': 25,
        'title_bg': 25,
        'title_fg': 253,
        'scroll_bar_bg': 247,
        'selected_header_column_bg': 247,
        'selected_header_column_fg': 232,
        'footer_bg': 25,
        'footer_fg': 253,
        'refreshing_bg': 25,
        'refreshing_fg': 253,
        'refreshing_inactive_bg': 25,
        'refreshing_inactive_fg': 232,
        '40pc_bg': 232,
        '40pc_fg': 166,
        'footer_string_bg': 25,
        'footer_string_fg': 253,
    },
        ### (3) Purple header, purple title, white modes, green selected, blue cursor
    {
        'background': 232,
        'normal_fg': 253,
        'unselected_bg': 232,
        'unselected_fg': 253,
        'cursor_bg': 57,
        'cursor_fg': 253,
        'selected_bg': 135,
        'selected_fg': 253,
        'header_bg': 253,
        'header_fg': 232,
        'error_bg': 232,
        'error_fg': curses.COLOR_RED,
        'complete_bg': 232,
        'complete_fg': 82,
        'waiting_bg': 232,
        'waiting_fg': curses.COLOR_YELLOW,
        'active_bg': 232,
        'active_fg': 33,
        'paused_bg': 232,
        'paused_fg': 244,
        'search_bg': 162,
        'search_fg': 253,
        'active_input_bg': 253,
        'active_input_fg': 57,
        'modes_selected_bg': 57,
        'modes_selected_fg': 253,
        'modes_unselected_bg': 253,
        'modes_unselected_fg': 232,
        'title_bar': 57,
        'title_bg': 57,
        'title_fg': 253,
        'scroll_bar_bg': 247,
        'selected_header_column_bg': 247,
        'selected_header_column_fg': 232,
        'footer_bg': 57,
        'footer_fg': 253,
        'refreshing_bg': 57,
        'refreshing_fg': 253,
        'refreshing_inactive_bg': 57,
        'refreshing_inactive_fg': 232,
        '40pc_bg': 232,
        '40pc_fg': 166,
        'footer_string_bg': 57,
        'footer_string_fg': 253,
    },
        ## (4) 3-bit colours
    {
        'background': curses.COLOR_BLACK,
        'normal_fg': curses.COLOR_WHITE,
        'unselected_bg': curses.COLOR_BLACK,
        'unselected_fg': curses.COLOR_WHITE,
        'cursor_bg': curses.COLOR_WHITE,
        'cursor_fg': curses.COLOR_BLACK,
        'selected_bg': curses.COLOR_MAGENTA,
        'selected_fg': curses.COLOR_BLACK,
        'header_bg': curses.COLOR_WHITE,
        'header_fg': curses.COLOR_BLACK,
        'error_bg': curses.COLOR_BLACK,
        'error_fg': curses.COLOR_RED,
        'complete_bg': curses.COLOR_BLACK,
        'complete_fg': curses.COLOR_BLUE,
        'waiting_bg': curses.COLOR_BLACK,
        'waiting_fg': curses.COLOR_YELLOW,
        'active_bg': curses.COLOR_BLACK,
        'active_fg': curses.COLOR_CYAN,
        'paused_bg': curses.COLOR_BLACK,
        'paused_fg': curses.COLOR_WHITE,
        'search_bg': curses.COLOR_WHITE,
        'search_fg': curses.COLOR_MAGENTA,
        'active_input_bg': curses.COLOR_BLACK,
        'active_input_fg': curses.COLOR_WHITE,
        'modes_selected_bg': curses.COLOR_WHITE,
        'modes_selected_fg': curses.COLOR_BLACK,
        'modes_unselected_bg': curses.COLOR_BLACK,
        'modes_unselected_fg': curses.COLOR_WHITE,
        'title_bar': curses.COLOR_BLACK,
        'title_bg': curses.COLOR_GREEN,
        'title_fg': curses.COLOR_BLACK,
        'scroll_bar_bg': curses.COLOR_WHITE,
        'selected_header_column_bg': curses.COLOR_BLACK,
        'selected_header_column_fg': curses.COLOR_WHITE,
        'footer_bg': curses.COLOR_GREEN,
        'footer_fg': curses.COLOR_BLACK,
        'refreshing_bg': curses.COLOR_GREEN,
        'refreshing_fg': curses.COLOR_BLACK,
        'refreshing_inactive_bg': curses.COLOR_GREEN,
        'refreshing_inactive_fg': curses.COLOR_WHITE,
        '40pc_bg': curses.COLOR_BLACK,
        '40pc_fg': curses.COLOR_YELLOW,
        'footer_string_bg': curses.COLOR_GREEN,
        'footer_string_fg': curses.COLOR_BLACK,
    },
    ]
    for colour in colours:
        colour["20pc_bg"] = colour["background"]
        colour["40pc_bg"] = colour["background"]
        colour["60pc_bg"] = colour["background"]
        colour["80pc_bg"] = colour["background"]
        colour["100pc_bg"] = colour["background"]
        colour["error_bg"] = colour["background"]
        colour["complete_bg"] = colour["background"]
        colour["waiting_bg"] = colour["background"]
        colour["active_bg"] = colour["background"]
        colour["paused_bg"] = colour["background"]
        colour["paused_bg"] = colour["background"]
        # colour["search_bg"] = colour["background"]
    if pick > len(colours) - 1:
        return colours[0]
    return colours[pick]

def get_help_colours(pick: int=0) -> dict:
    """ Define help colour options for listpick. """
    colours = get_colours(pick)
    # colours = [get_colours(i) for i in range(get_theme_count())]
    # for i in range(len(colours)):

    # 3-bit colours
    colours_3_bit = [4]
    if pick in colours_3_bit:
        colours['cursor_bg'] = curses.COLOR_WHITE
        colours['cursor_fg'] = curses.COLOR_BLACK
        colours['selected_bg'] = curses.COLOR_WHITE
        colours['selected_fg'] = curses.COLOR_BLACK
    else:
        colours['cursor_bg'] = 235
        colours['cursor_fg'] = 253
        colours['selected_bg'] = 25
        colours['selected_fg'] = 253

    return colours


def get_notification_colours(pick:int=0) -> dict:
    """ Define notification colour options for listpick. """
    colours = get_colours(pick)

    # Black and white
    if pick == 1:
        colours['background'] = 237
        colours['unselected_bg'] = 237
        colours['cursor_bg'] = 237
        colours['cursor_fg'] = 253
        colours['selected_bg'] = 237
        colours['selected_fg'] = 253

    # 3-bit colours
    elif pick == 4:
        colours['background'] = curses.COLOR_BLACK
        colours['unselected_bg'] = curses.COLOR_BLACK
        colours['cursor_bg'] = curses.COLOR_WHITE
        colours['cursor_fg'] = curses.COLOR_BLACK
        colours['selected_bg'] = curses.COLOR_WHITE
        colours['selected_fg'] = curses.COLOR_BLACK
    else:
        colours['background'] = 237
        colours['unselected_bg'] = 237
        colours['cursor_bg'] = 237
        colours['selected_bg'] = 237

    return colours

def get_fallback_colours() -> dict:
    get_colours(4)

def get_theme_count() -> int:
    """ Get the number of themes. """
    col_list = []
    i = 0
    for i in range(100):
        x = get_colours(i)
        if x in col_list:
            break
        col_list.append(x)
    return i
