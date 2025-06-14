import curses
from typing import Tuple
from input_field import input_field
from utils import dir_picker

def default_option_input(stdscr: curses.window, refresh_screen_function=None, starting_value:str="", field_name:str="Opts", registers={}) -> Tuple[bool, str]:
    # notification(stdscr, message=f"opt required for {index}")
    usrtxt = f"{starting_value} " if starting_value else ""
    h, w = stdscr.getmaxyx()
    # field_end = w-38 if show_footer else w-3
    field_end = w-3
    usrtxt, return_val = input_field(
        stdscr,
        usrtxt=usrtxt,
        field_name=field_name,
        x=2,
        y=h-1,
        max_length=field_end,
        registers=registers,
    )
    if return_val: return True, usrtxt
    else: return False, starting_value


def default_option_selector(stdscr: curses.window, refresh_screen_function=None, starting_value:str="", field_name:str="Opts", registers={}) -> Tuple[bool, str]:
    # notification(stdscr, message=f"opt required for {index}")
    usrtxt = f"{starting_value} " if starting_value else ""
    h, w = stdscr.getmaxyx()
    # field_end = w-38 if show_footer else w-3
    field_end = w-3
    usrtxt, return_val = input_field(
        stdscr,
        usrtxt=usrtxt,
        field_name=field_name,
        x=2,
        y=h-1,
        max_length=field_end,
        registers=registers,
    )
    if return_val: return True, usrtxt
    else: return False, starting_value


def output_file_option_selector(stdscr:curses.window, refresh_screen_function, registers={}) -> Tuple[bool, str]:
    s = dir_picker()

    stdscr.clear()
    stdscr.refresh()
    refresh_screen_function()
    usrtxt = f"{s}/"
    h, w = stdscr.getmaxyx()
    # field_end = w-38 if show_footer else w-3
    field_end = w-3
    usrtxt, return_val = input_field(
        stdscr,
        usrtxt=usrtxt,
        field_name="Save as",
        x=2,
        y=h-1,
        max_length=field_end,
        registers=registers,
    )
    if return_val: return True, usrtxt
    else: return False, ""
