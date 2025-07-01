#!/bin/python
import curses

"""
Define colour options for listpick--default, help, and notification colours.
"""
def get_theme_count() -> int:
    col_list = []
    i = 0
    for i in range(100):
        x = get_colours(i)
        if x in col_list:
            break
        col_list.append(x)
    return i


def get_colours(pick:int=0) -> dict[str, int]:
    """ Define colour options for listpick. """
    colours = [
        ### Green header, green title, green modes, purple selected, blue cursor
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
        ### Black and white
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
        ### Blue header, blue title, blue modes, purple selected, green cursor
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
        ### Purple header, purple title, white modes, green selected, blue cursor
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
    colours = [get_colours(i) for i in range(get_theme_count())]
    for i in range(len(colours)):
        colours[i]['cursor_bg'] = 235
        colours[i]['cursor_fg'] = 253
        colours[i]['selected_bg'] = 25
        colours[i]['selected_fg'] = 253

    if pick > len(colours) - 1:
        return colours[0]
    return colours[pick]


def get_notification_colours(pick:int=0) -> dict:
    colours = [get_colours(i) for i in range(get_theme_count())]
    for i in range(len(colours)):
        colours[i]['background'] = 237
        colours[i]['unselected_bg'] = 237
        colours[i]['cursor_bg'] = 237
        colours[i]['selected_bg'] = 237

    # Black and white
    colours[1]['background'] = 237
    colours[1]['unselected_bg'] = 237
    colours[1]['cursor_bg'] = 237
    colours[1]['cursor_fg'] = 253
    colours[1]['selected_bg'] = 237
    colours[1]['selected_fg'] = 253

    if pick > len(colours) - 1:
        return colours[0]
    return colours[pick]
