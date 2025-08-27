#!/bin/python
# -*- coding: utf-8 -*-
"""
listpick_app.py
Set up environment to parse command-line arguments and run a Picker.

Author: GrimAndGreedy
License: MIT
"""

import curses
import re
import os
import subprocess
import argparse
import time
from wcwidth import wcswidth
from typing import Callable, Optional, Tuple, Dict
import json
import threading
import string
import logging
import tty
import select

from listpick.ui.picker_colours import get_colours, get_help_colours, get_notification_colours, get_theme_count, get_fallback_colours
from listpick.utils.options_selectors import default_option_input, output_file_option_selector, default_option_selector
from listpick.utils.table_to_list_of_lists import *
from listpick.utils.utils import *
from listpick.utils.sorting import *
from listpick.utils.filtering import *
from listpick.ui.input_field import *
from listpick.utils.clipboard_operations import *
from listpick.utils.paste_operations import *
from listpick.utils.searching import search
from listpick.ui.help_screen import help_lines
from listpick.ui.keys import picker_keys, notification_keys, options_keys, help_keys
from listpick.utils.generate_data import generate_picker_data
from listpick.utils.dump import dump_state, load_state, dump_data
from listpick.ui.build_help import build_help_rows
from listpick.ui.footer import StandardFooter, CompactFooter, NoFooter
from listpick.utils.picker_log import setup_logger
from listpick.utils.user_input import get_char, open_tty
from listpick.pane.pane_functions import right_split_file_attributes, right_split_graph, right_split_display_list
from listpick.pane.get_data import *


try:
    from tmp.data_stuff import test_items, test_highlights, test_header
except:
    test_items, test_highlights, test_header = [], [], []

COLOURS_SET = False
help_colours, notification_colours = {}, {}

class Command:
    def __init__(self, command_type, command_value):
        self.command_type = command_type
        self.command_value = command_value

class Picker:
    def __init__(self,
        stdscr: curses.window, 
        items: list[list[str]] = [],
        cursor_pos: int = 0,
        colours: dict = get_colours(0),
        colour_theme_number: int = 3,
        max_selected: int = -1,
        top_gap: int =0,
        title: str ="Picker",
        header: list =[],
        max_column_width: int =70,
        clear_on_start: bool = False,
        
        auto_refresh: bool =False,
        timer: float = 5,

        get_new_data: bool =False,                          # Whether we can get new data
        refresh_function: Optional[Callable] = lambda: [],  # The function with which we get new data
        get_data_startup: bool =False,                      # Whether we should get data at statrup
        track_entries_upon_refresh: bool = True,
        pin_cursor: bool = False,
        id_column: int = 0,

        unselectable_indices: list =[],
        highlights: list =[],
        highlights_hide: bool =False,
        number_columns: bool =True,
        column_widths: list = [],
        column_indices: list = [],


        current_row : int = 0,
        current_page : int = 0,
        is_selecting : bool = False,
        is_deselecting : int = False,
        start_selection: int = -1,
        start_selection_col: int = -1,
        end_selection: int = -1,
        user_opts : str = "",
        options_list: list[str] = [],
        user_settings : str = "",
        separator : str = "    ",
        search_query : str = "",
        search_count : int = 0,
        search_index : int = 0,
        filter_query : str = "",
        hidden_columns: list = [],
        indexed_items: list[Tuple[int, list[str]]] = [],
        scroll_bar : int = True,

        selections: dict = {},
        cell_selections: dict[tuple[int,int], bool] = {},
        selected_cells_by_row: dict = {},
        highlight_full_row: bool =False,
        cell_cursor: bool = True,

        items_per_page : int = -1,
        sort_method : int = 0,
        SORT_METHODS: list[str] = ['Orig', 'lex', 'LEX', 'alnum', 'ALNUM', 'time', 'num', 'size'],
        sort_reverse: list[bool] = [False],
        selected_column: int = 0,
        sort_column : int = 0,

        columns_sort_method: list[int] = [0],
        key_chain: str = "",
        last_key: Optional[str] = None,

        paginate: bool =False,
        cancel_is_back: bool = False,
        mode_index: int = 0,
        modes: list[dict] = [],
        display_modes: bool =False,
        require_option: list=[],
        require_option_default: list=[],
        option_functions: list[Callable[..., Tuple[bool, str]]] = [],
        default_option_function: Callable[..., Tuple[bool, str]] = default_option_input,
        disabled_keys: list=[],

        show_header: bool = True,
        show_row_header: bool = False,
        show_footer: bool =True,
        footer_style: int = 0,
        footer_string: str="",
        footer_string_auto_refresh: bool=False,
        footer_string_refresh_function: Optional[Callable] = None,
        footer_timer: float=1,
        get_footer_string_startup=False,
        unicode_char_width: bool = True,

        colours_start: int =0,
        colours_end: int =-1,
        reset_colours: bool = True,
        key_remappings: dict = {},
        keys_dict:dict = picker_keys,
        display_infobox : bool = False,
        infobox_items: list[list[str]] = [],
        infobox_title: str = "",
        display_only: bool = False,

        editable_columns: list[int] = [],
        editable_by_default: bool = True,
        
        centre_in_terminal: bool = False,
        centre_in_terminal_vertical: bool = False,
        centre_in_cols: bool = False,

        startup_notification:str = "",

        leftmost_char: int = 0,

        history_filter_and_search: list[str] = [],
        history_opts: list[str] = [],
        history_settings: list[str] = [],
        history_edits: list[str] = [],
        history_pipes: list[str] = [],
        debug: bool = False,
        debug_level: int = 1,

        command_stack: list = [],

        loaded_file: str = "Untitled",
        loaded_files: list[str] = ["Untitled"],
        loaded_file_index: int = 0,
        loaded_file_states: list[dict] = [{}],


        sheets = ["Untitled"],
        sheet_name = "Untitled",
        sheet_index = 0,
        sheet_states: list = [{}],

        split_right: bool = False,
        split_right_proportion: float = 1/2,
        split_right_function: Callable = lambda stdscr, x, y, w, h, state, row, cell, data, test: False,
        split_right_auto_refresh: bool = False,
        split_right_refresh_data: Callable = lambda old_data, arg_dict: [],
        split_right_refresh_data_timer: float = 1.0,
        split_right_data: list = [],
        



    ):
        self.stdscr = stdscr
        self.items = items
        self.cursor_pos = cursor_pos
        self.colours = colours
        self.colour_theme_number = colour_theme_number
        self.max_selected = max_selected
        self.top_gap = top_gap
        self.title = title
        self.header = header
        self.max_column_width = max_column_width
        self.clear_on_start = clear_on_start
        
        self.auto_refresh = auto_refresh
        self.timer = timer

        self.get_new_data = get_new_data
        self.refresh_function = refresh_function
        self.get_data_startup = get_data_startup
        self.track_entries_upon_refresh = track_entries_upon_refresh
        self.pin_cursor = pin_cursor
        self.id_column = id_column

        self.unselectable_indices = unselectable_indices
        self.highlights = highlights
        self.highlights_hide = highlights_hide
        self.number_columns = number_columns
        self.column_widths, = [],
        self.column_indices, = [],


        self.current_row  = current_row
        self.current_page = current_page
        self.is_selecting = is_selecting
        self.is_deselecting = is_deselecting
        self.start_selection = start_selection
        self.start_selection_col = start_selection_col
        self.end_selection = end_selection
        self.user_opts = user_opts
        self.options_list = options_list
        self.user_settings = user_settings
        self.separator = separator
        self.search_query = search_query
        self.search_count = search_count
        self.search_index = search_index
        self.filter_query = filter_query
        self.hidden_columns = hidden_columns
        self.indexed_items = indexed_items
        self.scroll_bar = scroll_bar

        self.selections = selections
        self.cell_selections = cell_selections
        self.selected_cells_by_row = selected_cells_by_row
        self.highlight_full_row = highlight_full_row
        self.cell_cursor = cell_cursor

        self.items_per_page = items_per_page
        self.sort_method = sort_method
        self.sort_reverse = sort_reverse
        self.selected_column = selected_column
        self.sort_column = sort_column
        self.columns_sort_method = columns_sort_method
        self.key_chain = key_chain
        self.last_key = last_key

        self.paginate = paginate
        self.cancel_is_back = cancel_is_back
        self.mode_index = mode_index
        self.modes = modes
        self.display_modes = display_modes
        self.require_option = require_option
        self.require_option_default = require_option_default
        self.option_functions = option_functions
        self.default_option_function = default_option_function
        self.disabled_keys = disabled_keys

        self.show_header = show_header
        self.show_row_header = show_row_header
        self.show_footer = show_footer
        self.footer_style = footer_style
        self.footer_string = footer_string
        self.footer_string_auto_refresh = footer_string_auto_refresh
        self.footer_string_refresh_function = footer_string_refresh_function
        self.footer_timer = footer_timer
        self.get_footer_string_startup = get_footer_string_startup,
        self.unicode_char_width = unicode_char_width


        self.colours_start = colours_start
        self.colours_end = colours_end
        self.reset_colours = reset_colours
        self.key_remappings = key_remappings
        self.keys_dict = keys_dict
        self.display_infobox = display_infobox
        self.infobox_items = infobox_items
        self.infobox_title = infobox_title
        self.display_only = display_only

        self.editable_columns = editable_columns
        self.editable_by_default = editable_by_default

        self.centre_in_terminal = centre_in_terminal
        self.centre_in_terminal_vertical = centre_in_terminal_vertical
        self.centre_in_cols = centre_in_cols

        self.startup_notification = startup_notification


        self.registers = {}
        
        self.SORT_METHODS = SORT_METHODS
        self.command_stack = command_stack
        self.leftmost_char = leftmost_char


        # Refresh function variables
        self.data_refreshed = False
        self.refreshing_data = False
        self.data_lock = threading.Lock()
        self.data_ready = False
        self.cursor_pos_id = 0
        self.cursor_pos_prev = 0
        self.ids = []
        self.ids_tuples = []

        # History variables
        self.history_filter_and_search = history_filter_and_search
        self.history_pipes = history_pipes
        self.history_opts = history_opts
        self.history_settings = history_settings
        self.history_edits = history_edits


        self.debug = debug
        self.debug_level = debug_level

        # Multiple file support
        self.loaded_files = loaded_files
        self.loaded_file = loaded_file
        self.loaded_file_index = loaded_file_index
        self.loaded_file_states = loaded_file_states

        # Multiple sheet support
        self.sheet_index = sheet_index
        self.sheet_name = sheet_name
        self.sheet_states = sheet_states
        self.sheets = sheets

        self.split_right = split_right
        self.split_right_proportion = split_right_proportion
        self.split_right_function = split_right_function
        self.split_right_auto_refresh = split_right_auto_refresh
        self.split_right_refresh_data = split_right_refresh_data
        self.split_right_refresh_data_timer = split_right_refresh_data_timer
        self.split_right_data = split_right_data

        self.initialise_picker_state(reset_colours=self.reset_colours)

        # Note: We have to set the footer after initialising the picker state so that the footer can use the get_function_data method
        self.footer_options = [StandardFooter(self.stdscr, colours_start, self.get_function_data), CompactFooter(self.stdscr, colours_start, self.get_function_data), NoFooter(self.stdscr, colours_start, self.get_function_data)]
        self.footer = self.footer_options[self.footer_style]
        self.__version__ = "1.0"

    def __sizeof__(self):

        size = super().__sizeof__()
        
        # Add the size of each attribute directly owned by the object
        for attr_name in dir(self):
            if not attr_name.startswith('__') and not callable(getattr(self, attr_name)):
                size += sys.getsizeof(getattr(self, attr_name))
        return size
    
    def set_config(self, path: str ="~/.config/listpick/config.toml") -> bool:
        """ Set config from toml file. """
        path = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(path):
            return False
        try:
            config = self.get_config(path)
        except Exception as e:
            self.logger.error(f"get_config({path}) load error. {e}")
            return False

        if "general" in config:
            if "colour_theme_number" in config["general"] and config["general"]["colour_theme_number"] != self.colour_theme_number:
                global COLOURS_SET 
                COLOURS_SET = False
                self.colours_end = set_colours(pick=config["general"]["colour_theme_number"], start=1)

        self.logger.info(f"function: set_config()")
        if "general" in config:
            for key, val in config["general"].items():
                self.logger.info(f"set_config: key={key}, val={val}.")
                try:
                    setattr(self, key, val)
                except Exception as e:
                    self.logger.error(f"set_config: key={key}, val={val}. {e}")
                    
        return True

    def get_config(self, path: str ="~/.config/listpick/config.toml") -> dict:
        """ Get config from file. """
        self.logger.info(f"function: get_config()")
        import toml
        with open(os.path.expanduser(path), "r") as f:
            config = toml.load(f)
            return config

    def calculate_section_sizes(self):
        """
        Calculte the following for the Picker:
        self.items_per_page: the number of entry rows displayed
        self.bottom_space: the size of the footer + the bottom buffer space
        self.top_space: the size of the space at the top of the picker: title + modes + header + top_gap
        """

        self.logger.debug(f"function: calculate_section_sizes()")

        # self.bottom_space
        self.bottom_space = self.footer.height if self.show_footer else 0

        ## self.top_space
        h, w = self.stdscr.getmaxyx()
        self.term_h, self.term_w = self.stdscr.getmaxyx()
        if self.split_right and self.split_right_function(self.stdscr, 0,0,0,0,{},[],[],"",test=True):
            self.rows_w, self.rows_h = int(self.term_w*self.split_right_proportion), self.term_h
        else:
            self.rows_w, self.rows_h = self.term_w, self.term_h

        self.top_space = self.top_gap
        if self.title: self.top_space+=1
        if self.modes and self.display_modes: self.top_space+=1
        if self.header and self.show_header: self.top_space += 1

        # self.items_per_page
        self.items_per_page = self.term_h - self.top_space - self.bottom_space
        if not self.show_footer and self.footer_string: self.items_per_page-=1
        self.items_per_page = min(self.term_h-self.top_space-1, self.items_per_page)


        # Adjust top space if centring vertically and we have fewer rows than terminal lines
        if self.centre_in_terminal_vertical and len(self.indexed_items) < self.items_per_page:
            self.top_space += ((self.term_h-(self.top_space+self.bottom_space))-len(self.indexed_items))//2

        # self.column_widths
        visible_column_widths = [c for i,c in enumerate(self.column_widths) if i not in self.hidden_columns]
        visible_columns_total_width = sum(visible_column_widths) + len(self.separator)*(len(visible_column_widths)-1)

        # self.startx
        self.startx = 1 if self.highlight_full_row else 2
        if self.show_row_header: self.startx += len(str(len(self.items))) + 2
        if visible_columns_total_width < self.rows_w and self.centre_in_terminal:
            self.startx += (self.rows_w - visible_columns_total_width) // 2

    def get_visible_rows(self) -> list[list[str]]:

        self.logger.debug(f"function: get_visible_rows()")
        ## Scroll with column select
        if self.paginate:
            start_index = (self.cursor_pos//self.items_per_page) * self.items_per_page
            end_index = min(start_index + self.items_per_page, len(self.indexed_items))
        ## Scroll
        else:
            scrolloff = self.items_per_page//2
            start_index = max(0, min(self.cursor_pos - (self.items_per_page-scrolloff), len(self.indexed_items)-self.items_per_page))
            end_index = min(start_index + self.items_per_page, len(self.indexed_items))
        if len(self.indexed_items) == 0: start_index, end_index = 0, 0

        rows = [v[1] for v in self.indexed_items[start_index:end_index]] if len(self.indexed_items) else self.items
        return rows

    def initialise_picker_state(self, reset_colours=False) -> None:
        """ Initialise state variables for the picker. These are: debugging and colours. """

        if curses.has_colors() and self.colours != None:
            # raise Exception("Terminal does not support color")
            curses.start_color()
            if reset_colours:
                global COLOURS_SET
                COLOURS_SET = False
                self.colours_end = set_colours(pick=self.colour_theme_number, start=self.colours_start)
            if curses.COLORS >= 255 and curses.COLOR_PAIRS >= 150:
                self.colours_start = self.colours_start
                self.notification_colours_start = self.colours_start+50
                self.help_colours_start = self.colours_start+100
            else:
                self.colours_start = 0
                self.notification_colours_start = 0
                self.help_colours_start = 0
        else:
                self.colours_start = 0
                self.notification_colours_start = 0
                self.help_colours_start = 0


        debug_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        dbglvl =  debug_levels[self.debug_level]
        self.logger = setup_logger(name="picker_log", log_file="picker.log", log_enabled=self.debug, level =dbglvl)
        self.logger.info(f"Initialiasing Picker.")
        # self.notification(self.stdscr, message=repr(self.logger))


        #                     1              2             3                4              5
        # logger = logging.getLogger(__file__)
        # if self.debug_level == 0:
        #     logger = logging.getLogger()
        #     logger.disabled = True
        # else:
        #
        #     file_handler = logging.FileHandler(f"{self.title}.log", mode='w')
        #     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%m-%d-%Y %H:%M:%S')
        #     file_handler.setFormatter(formatter)
        #     logger.addHandler(file_handler)
        #     logger.setLevel(debug_levels[self.debug_level-1])

            # logging.basicConfig(
            #     level=debug_levels[self.debug_level-1],
            #     format='%(asctime)s - %(levelname)s - %(message)s',
            #     datefmt='%m-%d-%Y %H:%M:%S',
            #     filename=f"{self.title}.log",
            #     filemode="w",
            # )
        #
        # self.logger.info(f"Starging log. Log level {logger.getEffectiveLevel()}")
        # self.logger.info(f"Starging log. Log level {repr(debug_levels)}, {self.debug_level}, {debug_levels[self.debug_level-1]}")
        # self.notification(self.stdscr, f"Starging log. Log level {repr(debug_levels)}, {self.debug_level}, {debug_levels[self.debug_level-1]}")
        # self.notification(self.stdscr, f"{__file__}")

        ## Logging level plan
        # DEBUG: loop functions, draw screen, etc.
        # INFO: main functions 
        # WARNING: any try-except fails 

        # No set_escdelay function on windows.
        try:
            curses.set_escdelay(25)
        except:
            logging.warning("Error trying to set curses.set_escdelay")

        # self.stdscr.clear()
        # self.stdscr.refresh()
        # self.draw_screen(self.indexed_items, self.highlights)

    def initialise_variables(self, get_data: bool = False) -> None:
        """ Initialise the variables that keep track of the data. """

        self.logger.info(f"function: initialise_variables()")

        tracking = False

        ## Get data synchronously
        if get_data and self.refresh_function != None:
            if self.track_entries_upon_refresh and len(self.items) > 0:
                tracking = True
                selected_indices = get_selected_indices(self.selections)
                self.selected_cells_by_row = get_selected_cells_by_row(self.cell_selections)
                self.ids = [item[self.id_column] for i, item in enumerate(self.items) if i in selected_indices]
                self.ids_tuples = [(i, item[self.id_column]) for i, item in enumerate(self.items) if i in selected_indices]
        
                if len(self.indexed_items) > 0 and len(self.indexed_items) >= self.cursor_pos and len(self.indexed_items[0][1]) >= self.id_column:
                    self.cursor_pos_id = self.indexed_items[self.cursor_pos][1][self.id_column]
                    self.cursor_pos_prev = self.cursor_pos
        
            self.items, self.header = self.refresh_function()

        self.items = pad_lists_to_same_length(self.items)
                    
        if self.items == []: self.items = [[]]
        ## Ensure that items is a List[List[Str]] object
        if len(self.items) > 0 and not isinstance(self.items[0], list):
            self.items = [[item] for item in self.items]
        self.items = [[str(cell) for cell in row] for row in self.items]


        # Ensure that header is of the same length as the rows
        if self.header and len(self.items) > 0 and len(self.header) != len(self.items[0]):
            self.header = [str(self.header[i]) if i < len(self.header) else "" for i in range(len(self.items[0]))]

        # Constants
        # DEFAULT_ITEMS_PER_PAGE = os.get_terminal_size().lines - top_gap*2-2-int(bool(header))

        self.calculate_section_sizes()

        # Initial states
        if len(self.selections) != len(self.items):
            self.selections = {i : False if i not in self.selections else bool(self.selections[i]) for i in range(len(self.items))}

        if len(self.items) and len(self.cell_selections) != len(self.items)*len(self.items[0]):
            self.cell_selections = {(i, j) : False if (i, j) not in self.cell_selections else self.cell_selections[(i, j)] for i in range(len(self.items)) for j in range(len(self.items[0]))}
            self.selected_cells_by_row = get_selected_cells_by_row(self.cell_selections)
        elif len(self.items) == 0:
            self.cell_selections = {}
            self.selected_cells_by_row = {}

        

        if len(self.require_option) < len(self.items):
            self.require_option += [self.require_option_default for i in range(len(self.items)-len(self.require_option))]
        if len(self.option_functions) < len(self.items):
            self.option_functions += [self.default_option_function for i in range(len(self.items)-len(self.option_functions))]
        if len(self.items)>0 and len(self.columns_sort_method) < len(self.items[0]):
            self.columns_sort_method = self.columns_sort_method + [0 for i in range(len(self.items[0])-len(self.columns_sort_method))]
        if len(self.items)>0 and len(self.sort_reverse) < len(self.items[0]):
            self.sort_reverse = self.sort_reverse + [False for i in range(len(self.items[0])-len(self.sort_reverse))]
        if len(self.items)>0 and len(self.editable_columns) < len(self.items[0]):
            self.editable_columns = self.editable_columns + [self.editable_by_default for i in range(len(self.items[0])-len(self.editable_columns))]
        if len(self.items)>0 and len(self.column_indices) < len(self.items[0]):
            self.column_indices = self.column_indices + [i for i in range(len(self.column_indices), len(self.items[0]))]


        
        # items2 = [[row[self.column_indices[i]] for i in range(len(row))] for row in self.items]
        # self.indexed_items = list(enumerate(items2))
        if self.items == [[]]: self.indexed_items = []
        else: self.indexed_items = list(enumerate(self.items))

        # If a filter is passed then refilter
        if self.filter_query:
            # prev_index = self.indexed_items[cursor_pos][0] if len(self.indexed_items)>0 else 0
            # prev_index = self.indexed_items[cursor_pos][0] if len(self.indexed_items)>0 else 0
            self.indexed_items = filter_items(self.items, self.indexed_items, self.filter_query)
            if self.cursor_pos in [x[0] for x in self.indexed_items]: self.cursor_pos = [x[0] for x in self.indexed_items].index(self.cursor_pos)
            else: self.cursor_pos = 0
        if self.search_query:
            return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                query=self.search_query,
                indexed_items=self.indexed_items,
                highlights=self.highlights,
                cursor_pos=self.cursor_pos,
                unselectable_indices=self.unselectable_indices,
                continue_search=True,
            )
            if return_val:
                self.cursor_pos, self.search_index, self.search_count, self.highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights
        # If a sort is passed
        if len(self.indexed_items) > 0:
            sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column


        # Adjust variables to ensure correctness if errors
        ## Move to a selectable row (if applicable)
        if len(self.items) <= len(self.unselectable_indices): self.unselectable_indices = []
        new_pos = (self.cursor_pos)%len(self.items)
        while new_pos in self.unselectable_indices and new_pos != self.cursor_pos:
            new_pos = (new_pos + 1) % len(self.items)

        assert new_pos < len(self.items)
        self.cursor_pos = new_pos

        # Sheets and files
        if len(self.sheet_states) < len(self.sheets):
            self.sheet_states += [{} for _ in range(len(self.sheets) - len(self.sheet_states))]
        if len(self.sheets):
            if self.sheet_index >= len(self.sheets):
                self.sheet_index = 0
            self.sheet_name = self.sheets[self.sheet_index]

        if len(self.loaded_file_states) < len(self.loaded_files):
            self.loaded_file_states += [{} for _ in range(len(self.loaded_files) - len(self.loaded_file_states))]
        if len(self.loaded_files):
            if self.loaded_file_index >= len(self.loaded_files):
                self.loaded_file_index = 0
            self.loaded_file = self.loaded_files[self.loaded_file_index]

        # if tracking and len(self.items) > 1:
        # Ensure that selected indices are tracked upon data refresh
        if self.track_entries_upon_refresh and (self.data_ready or tracking) and len(self.items) > 1:
            selected_indices = []
            all_ids = [item[self.id_column] for item in self.items]
            self.selections = {i: False for i in range(len(self.items))}
            if len(self.items) > 0:
                self.cell_selections = {(i, j): False for i in range(len(self.items)) for j in range(len(self.items[0]))}
            else:
                self.cell_selections = {}

            for id in self.ids:
                if id in all_ids:
                    selected_indices.append(all_ids.index(id))
                    self.selections[all_ids.index(id)] = True

            for i, id in self.ids_tuples:
                if id in all_ids:
                    # rows_with_selected_cells
                    for j in self.selected_cells_by_row[i]:
                        self.cell_selections[(all_ids.index(id), j)] = True



            if len(self.indexed_items):
                if self.pin_cursor:
                    self.cursor_pos = min(self.cursor_pos_prev, len(self.indexed_items)-1)
                else:
                    if self.cursor_pos_id in all_ids:
                        cursor_pos_x = all_ids.index(self.cursor_pos_id)
                        if cursor_pos_x in [i[0] for i in self.indexed_items]:
                            self.cursor_pos = [i[0] for i in self.indexed_items].index(cursor_pos_x)
            else:
                self.cursor_pos = 0

        


    def move_column(self, direction: int) -> None:
        """ 
        Cycles the column $direction places. 
        E.g., If $direction == -1 and the sort column is 3, then column 3 will swap with column 2
            in each of the rows in $items and 2 will become the new sort column.

        sort_column = 3, direction = -1
            [[0,1,2,*3*,4],
             [5,6,7,*8*,9]]
                -->
            [[0,1,*3*,2,4],
             [5,6,*8*,7,9]]

        returns:
            adjusted items, header, sort_column and column_widths
        """
        self.logger.info(f"function: move_column(direction={direction})")
        if len(self.items) < 1: return None
        if (self.selected_column+direction) < 0 or (self.selected_column+direction) >= len(self.items[0]): return None

        new_index = self.selected_column + direction

        # Swap columns in each row
        for row in self.items:
            row[self.selected_column], row[new_index] = row[new_index], row[self.selected_column]
        if self.header:
            self.header[self.selected_column], self.header[new_index] = self.header[new_index], self.header[self.selected_column]

        # Swap column widths
        self.column_widths[self.selected_column], self.column_widths[new_index] = self.column_widths[new_index], self.column_widths[self.selected_column]

        # Update current column index
        self.selected_column = new_index

    def test_screen_size(self) -> bool:
        """ 
        Determine if the terminal is large enough to display the picker. 
        If the terminal is too small then display a message saying so.

        Returns: True if terminal is large enough to display the Picker.

        """
        self.logger.debug("function: test_screen_size()")
        h, w = self.stdscr.getmaxyx()
        ## Terminal too small to display Picker
        if h<3 or w<len("Terminal"): return False
        if (self.show_footer or self.footer_string) and (h<12 or w<35) or (h<12 and w<10):
            self.stdscr.addstr(h//2-1, (w-len("Terminal"))//2, "Terminal")
            self.stdscr.addstr(h//2, (w-len("Too"))//2, "Too")
            self.stdscr.addstr(h//2+1, (w-len("Small"))//2, "Small")
            return False
        return True

    def splash_screen(self, message="") -> None:
        """ Display a splash screen with a message. Useful when loading a large data set. """

        self.logger.info(f"function: splash_screen({message})")
        h, w =self.stdscr.getmaxyx()
        self.stdscr.bkgd(' ', curses.color_pair(2))
        try:
            self.stdscr.addstr(h//2, (w-len(message))//2, message, curses.color_pair(2))
        except:
            pass
        self.stdscr.refresh()

    def draw_screen(self, indexed_items: list[Tuple[int, list[str]]], highlights: list[dict] = [{}], clear: bool = True) -> None:
        """ Try-except wrapper for the draw_screen_ function. """
        try:
            self.draw_screen_(self.indexed_items, self.highlights)
        except Exception as e:
            self.logger.warning(f"self.draw_screen_() error. {e}")
            pass

    def draw_screen_(self, indexed_items: list[Tuple[int, list[str]]], highlights: list[dict] = [{}], clear: bool = True) -> None:
        """ Draw Picker screen. """

        self.logger.debug("Draw screen.")

        if clear:
            self.stdscr.erase()

        h, w = self.stdscr.getmaxyx()
        self.term_h, self.term_w = self.stdscr.getmaxyx()
        if self.split_right and self.split_right_function(self.stdscr, 0,0,0,0,{},[],[],"",test=True):
            self.rows_w, self.rows_h = int(self.term_w*self.split_right_proportion), self.term_h
        else:
            self.rows_w, self.rows_h = self.term_w, self.term_h

        # The height of the footer may need to be adjusted if the file changes.
        self.footer.adjust_sizes(self.term_h,self.term_w)
        self.calculate_section_sizes()

        # Test if the terminal is of a sufficient size to display the picker
        if not self.test_screen_size(): return None

        # Determine which rows are to be displayed on the current screen
        ## Paginate
        if self.paginate:
            start_index = (self.cursor_pos//self.items_per_page) * self.items_per_page
            end_index = min(start_index + self.items_per_page, len(self.indexed_items))
        ## Scroll
        else:
            scrolloff = self.items_per_page//2
            start_index = max(0, min(self.cursor_pos - (self.items_per_page-scrolloff), len(self.indexed_items)-self.items_per_page))
            end_index = min(start_index + self.items_per_page, len(self.indexed_items))
        if len(self.indexed_items) == 0: start_index, end_index = 0, 0

        # self.column_widths = get_column_widths(self.items, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=w)
        # Determine widths based only on the currently indexed rows
        # rows = [v[1] for v in self.indexed_items] if len(self.indexed_items) else self.items
        # Determine widths based only on the currently displayed indexed rows
        rows = [v[1] for v in self.indexed_items[start_index:end_index]] if len(self.indexed_items) else self.items
        self.column_widths = get_column_widths(rows, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=self.rows_w, unicode_char_width=self.unicode_char_width)
        visible_column_widths = [c for i,c in enumerate(self.column_widths) if i not in self.hidden_columns]
        visible_columns_total_width = sum(visible_column_widths) + len(self.separator)*(len(visible_column_widths)-1)

        # Determine the number of items_per_page, top_size and bottom_size
        # self.calculate_section_sizes()
        
        # top_space = self.top_gap

        ## Display title (if applicable)
        if self.title:
            padded_title = f" {self.title.strip()} "
            self.stdscr.addstr(self.top_gap, 0, f"{' ':^{self.term_w}}", curses.color_pair(self.colours_start+16))
            title_x = (self.term_w-wcswidth(padded_title))//2
            self.stdscr.addstr(self.top_gap, title_x, padded_title, curses.color_pair(self.colours_start+16) | curses.A_BOLD)
            # top_space += 1

        ## Display modes
        if self.display_modes and self.modes not in [[{}], []]:
            self.stdscr.addstr(self.top_gap+1, 0, ' '*self.term_w, curses.A_REVERSE)
            modes_list = [f"{mode['name']}" if 'name' in mode else f"{i}. " for i, mode in enumerate(self.modes)]
            # mode_colours = [mode["colour"] for mode ]
            mode_widths = get_mode_widths(modes_list)
            split_space = (self.term_w-sum(mode_widths))//len(self.modes)
            xmode = 0
            for i, mode in enumerate(modes_list):
                if i == len(modes_list)-1:
                    mode_str = f"{mode:^{mode_widths[i]+split_space+(self.term_w-sum(mode_widths))%len(self.modes)}}"
                else:
                    mode_str = f"{mode:^{mode_widths[i]+split_space}}"
                # current mode
                if i == self.mode_index:
                    self.stdscr.addstr(self.top_gap+1, xmode, mode_str, curses.color_pair(self.colours_start+14) | curses.A_BOLD)
                # other modes
                else:
                    self.stdscr.addstr(self.top_gap+1, xmode, mode_str, curses.color_pair(self.colours_start+15) | curses.A_UNDERLINE)
                xmode += split_space+mode_widths[i]
            # top_space += 1

        ## Display header
        if self.header and self.show_header:
            header_str = ""
            up_to_selected_col = ""
            selected_col_str = ""
            for i in range(len(self.header)):
                if i == self.selected_column: up_to_selected_col = header_str
                if i in self.hidden_columns: continue
                number = f"{i}. " if self.number_columns else ""
                # number = f"{intStringToExponentString(str(i))}. " if self.number_columns else ""
                header_str += number
                header_str += f"{self.header[i]:^{self.column_widths[i]-len(number)}}"
                header_str += self.separator

            header_str = header_str[self.leftmost_char:]
            header_ypos = self.top_gap + bool(self.title) + bool(self.display_modes and self.modes)
            self.stdscr.addstr(header_ypos, 0, ' '*self.rows_w, curses.color_pair(self.colours_start+4) | curses.A_BOLD)
            self.stdscr.addstr(header_ypos, self.startx, header_str[:min(self.rows_w-self.startx, visible_columns_total_width+1)], curses.color_pair(self.colours_start+4) | curses.A_BOLD)

            # Highlight sort column
            try:
                if self.selected_column != None and self.selected_column not in self.hidden_columns:
                    if len(self.header) > 1 and (len(up_to_selected_col)-self.leftmost_char) < self.rows_w:
                        number = f"{self.selected_column}. " if self.number_columns else ""
                        # number = f"{intStringToExponentString(self.selected_column)}. " if self.number_columns else ""
                        # self.startx + len(up_to_selected_col) - self.leftmost_char
                        highlighed_col_startx = max(self.startx, self.startx + len(up_to_selected_col) - self.leftmost_char)
                        highlighted_col_str = (number+f"{self.header[self.selected_column]:^{self.column_widths[self.selected_column]-len(number)}}") + self.separator
                        end_of_highlighted_col_str = self.rows_w-(highlighed_col_startx+len(highlighted_col_str)) if (highlighed_col_startx+len(highlighted_col_str)) > self.rows_w else len(highlighted_col_str)
                        start_of_highlighted_col_str = max(self.leftmost_char - len(up_to_selected_col), 0)
                        self.stdscr.addstr(header_ypos, highlighed_col_startx , highlighted_col_str[start_of_highlighted_col_str:end_of_highlighted_col_str], curses.color_pair(self.colours_start+19) | curses.A_BOLD)
            except:
                pass
                
        # Display row header 
        if self.show_row_header:
            for idx in range(start_index, end_index):
                y = idx - start_index + self.top_space
                if idx == self.cursor_pos:
                    self.stdscr.addstr(y, 0, f" {self.indexed_items[idx][0]} ", curses.color_pair(self.colours_start+19) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, 0, f" {self.indexed_items[idx][0]} ", curses.color_pair(self.colours_start+4) | curses.A_BOLD)

        def highlight_cell(row: int, col:int, visible_column_widths, colour_pair_number: int = 5):
            cell_pos = sum(visible_column_widths[:col])+col*len(self.separator)-self.leftmost_char + self.startx
            # cell_width = self.column_widths[self.selected_column]
            cell_width = visible_column_widths[col] + len(self.separator)
            cell_max_width = self.rows_w-cell_pos
            try:
                # Start of cell is on screen
                if self.startx <= cell_pos <= self.rows_w:
                    self.stdscr.addstr(y, cell_pos, (' '*cell_width)[:cell_max_width], curses.color_pair(self.colours_start+colour_pair_number))
                    if self.centre_in_cols:
                        cell_value = f"{self.indexed_items[row][1][col]:^{cell_width-len(self.separator)}}" + self.separator
                    else:
                        cell_value = self.indexed_items[row][1][col] + self.separator
                    # cell_value = cell_value[:min(cell_width, cell_max_width)-len(self.separator)]
                    cell_value = truncate_to_display_width(cell_value, min(cell_width, cell_max_width)-len(self.separator), self.centre_in_cols, self.unicode_char_width)
                    cell_value = cell_value + self.separator
                    # cell_value = cell_value
                    cell_value = truncate_to_display_width(cell_value, min(cell_width, cell_max_width), self.centre_in_cols, self.unicode_char_width)
                    self.stdscr.addstr(y, cell_pos, cell_value, curses.color_pair(self.colours_start+colour_pair_number) | curses.A_BOLD)
                # Part of the cell is on screen
                elif self.startx <= cell_pos+cell_width <= self.rows_w:
                    cell_start = self.startx - cell_pos
                    self.stdscr.addstr(y, self.startx, ' '*(cell_width-cell_start), curses.color_pair(self.colours_start+colour_pair_number))
                    cell_value = self.indexed_items[row][1][col][cell_start:visible_column_widths[col]]
                    self.stdscr.addstr(y, self.startx, cell_value, curses.color_pair(self.colours_start+colour_pair_number) | curses.A_BOLD)
            except:
                pass


        def sort_highlights(highlights):
            """ 
            Sort highlights into lists based on their display level.
            Highlights with no level defined will be displayed at level 0.
            """
            l0 = []
            l1 = []
            l2 = []
            for highlight in highlights:
                if "level" in highlight:
                    if highlight["level"] == 0: l0.append(highlight)
                    elif highlight["level"] == 1: l1.append(highlight)
                    elif highlight["level"] == 2: l2.append(highlight)
                    else: l0.append(highlight)
                else:
                    l0.append(highlight)
            return l0, l1, l2

        def draw_highlights(highlights: list[dict], idx: int, y: int, item: tuple[int, list[str]]):
            self.logger.debug(f"function: draw_highlights()")
            if len(highlights) == 0: return None
            full_row_str = format_row(item[1], self.hidden_columns, self.column_widths, self.separator, self.centre_in_cols, self.unicode_char_width)
            row_str = full_row_str[self.leftmost_char:]
            for highlight in highlights:
                if "row" in highlight:
                    if highlight["row"] != self.indexed_items[idx][0]:
                        continue
                try:
                    if highlight["field"] == "all":
                        match = re.search(highlight["match"], full_row_str, re.IGNORECASE)
                        if not match: continue
                        highlight_start = match.start()
                        highlight_end = match.end()
                        if highlight_end - self.leftmost_char < 0:
                            continue

                    elif type(highlight["field"]) == type(0) and highlight["field"] not in self.hidden_columns:
                        match = re.search(highlight["match"], truncate_to_display_width(item[1][highlight["field"]], self.column_widths[highlight["field"]], centre=False, unicode_char_width=self.unicode_char_width), re.IGNORECASE)
                        if not match: continue
                        field_start = sum([width for i, width in enumerate(self.column_widths[:highlight["field"]]) if i not in self.hidden_columns]) + sum([1 for i in range(highlight["field"]) if i not in self.hidden_columns])*wcswidth(self.separator)

                        ## We want to search the non-centred values but highlight the centred values.
                        if self.centre_in_cols:
                            tmp = truncate_to_display_width(item[1][highlight["field"]], self.column_widths[highlight["field"]], self.centre_in_cols, self.unicode_char_width)
                            field_start += (len(tmp) - len(tmp.lstrip()))

                        highlight_start = field_start + match.start()
                        highlight_end = match.end() + field_start
                        if highlight_end - self.leftmost_char < 0:
                            continue
                    else:
                        continue
                    highlight_start -= self.leftmost_char
                    highlight_end -= self.leftmost_char
                    self.stdscr.addstr(y, max(self.startx, self.startx+highlight_start), row_str[max(highlight_start,0):min(self.rows_w-self.startx, highlight_end)], curses.color_pair(self.colours_start+highlight["color"]) | curses.A_BOLD)
                except:
                    pass

        # Draw:
        #    1. standard row
        #    2. highlights l0
        #    3. selected
        #    4. above-selected highlights l1
        #    5. cursor
        #    6. top-level highlights l2
        ## Display rows and highlights

        l0_highlights, l1_highlights, l2_highlights = sort_highlights(self.highlights)


        for idx in range(start_index, end_index):
            item = self.indexed_items[idx]
            y = idx - start_index + self.top_space

            # row_str = format_row(item[1], self.hidden_columns, self.column_widths, self.separator, self.centre_in_cols)[self.leftmost_char:]
            # row_str = truncate_to_display_width(row_str, min(w-self.startx, visible_columns_total_width))
            row_str_orig = format_row(item[1], self.hidden_columns, self.column_widths, self.separator, self.centre_in_cols, self.unicode_char_width)
            row_str_left_adj = clip_left(row_str_orig, self.leftmost_char)
            row_str = truncate_to_display_width(row_str_left_adj, min(self.rows_w-self.startx, visible_columns_total_width), self.unicode_char_width)
            # row_str = truncate_to_display_width(row_str, min(w-self.startx, visible_columns_total_width))[self.leftmost_char:]

            ## Display the standard row
            self.stdscr.addstr(y, self.startx, row_str[:min(self.rows_w-self.startx, visible_columns_total_width)], curses.color_pair(self.colours_start+2))
            

            # Draw the level 0 highlights
            if not self.highlights_hide:
                draw_highlights(l0_highlights, idx, y, item)

            # Higlight cursor cell and selected cells
            if self.cell_cursor:
                # self.selected_cells_by_row = get_selected_cells_by_row(self.cell_selections)
                if item[0] in self.selected_cells_by_row:
                    for j in self.selected_cells_by_row[item[0]]:
                        highlight_cell(idx, j, visible_column_widths, colour_pair_number=25)

                # Visually selected
                if self.is_selecting:
                    if self.start_selection <= idx <= self.cursor_pos or self.start_selection >= idx >= self.cursor_pos:
                        x_interval = range(min(self.start_selection_col, self.selected_column), max(self.start_selection_col, self.selected_column)+1)
                        for col in x_interval:
                            highlight_cell(idx, col, visible_column_widths, colour_pair_number=25)

                # Visually deslected
                if self.is_deselecting:
                    if self.start_selection >= idx >= self.cursor_pos or self.start_selection <= idx <= self.cursor_pos:
                        x_interval = range(min(self.start_selection_col, self.selected_column), max(self.start_selection_col, self.selected_column)+1)
                        for col in x_interval:
                            highlight_cell(idx, col, visible_column_widths, colour_pair_number=26)
            # Higlight cursor row and selected rows
            elif self.highlight_full_row:
                if self.selections[item[0]]:
                    self.stdscr.addstr(y, self.startx, row_str[:min(self.rows_w-self.startx, visible_columns_total_width)], curses.color_pair(self.colours_start+25) | curses.A_BOLD)
                # Visually selected
                if self.is_selecting:
                    if self.start_selection <= idx <= self.cursor_pos or self.start_selection >= idx >= self.cursor_pos:
                        self.stdscr.addstr(y, self.startx, row_str[:min(self.rows_w-self.startx, visible_columns_total_width)], curses.color_pair(self.colours_start+25))
                # Visually deslected
                elif self.is_deselecting:
                    if self.start_selection >= idx >= self.cursor_pos or self.start_selection <= idx <= self.cursor_pos:
                        self.stdscr.addstr(y, self.startx, row_str[:min(self.rows_w-self.startx, visible_columns_total_width)], curses.color_pair(self.colours_start+26))

            # Highlight the cursor row and the first char of the selected rows.
            else:
                if self.selections[item[0]]:
                    self.stdscr.addstr(y, max(self.startx-2,0), ' ', curses.color_pair(self.colours_start+1))
                # Visually selected
                if self.is_selecting:
                    if self.start_selection <= idx <= self.cursor_pos or self.start_selection >= idx >= self.cursor_pos:
                        self.stdscr.addstr(y, max(self.startx-2,0), ' ', curses.color_pair(self.colours_start+1))
                # Visually deslected
                if self.is_deselecting:
                    if self.start_selection >= idx >= self.cursor_pos or self.start_selection <= idx <= self.cursor_pos:
                        self.stdscr.addstr(y, max(self.startx-2,0), ' ', curses.color_pair(self.colours_start+10))

            if not self.highlights_hide:
                draw_highlights(l1_highlights, idx, y, item)

            # Draw cursor
            if idx == self.cursor_pos:
                if self.cell_cursor:
                    highlight_cell(idx, self.selected_column, visible_column_widths)
                else:
                    self.stdscr.addstr(y, self.startx, row_str[:min(self.rows_w-self.startx, visible_columns_total_width)], curses.color_pair(self.colours_start+5) | curses.A_BOLD)
            
            if not self.highlights_hide:
                draw_highlights(l2_highlights, idx, y, item)

        ## Display scrollbar
        if self.scroll_bar and len(self.indexed_items) and len(self.indexed_items) > (self.items_per_page):
            scroll_bar_length = int(self.items_per_page*self.items_per_page/len(self.indexed_items))
            if self.cursor_pos <= self.items_per_page//2:
                scroll_bar_start=self.top_space
            elif self.cursor_pos + self.items_per_page//2 >= len(self.indexed_items):
                scroll_bar_start = self.term_h - int(bool(self.show_footer))*self.footer.height - scroll_bar_length
            else:
                scroll_bar_start = int(((self.cursor_pos)/len(self.indexed_items))*self.items_per_page)+self.top_space - scroll_bar_length//2
            scroll_bar_start = min(scroll_bar_start, self.term_h-self.top_space-1)
            scroll_bar_length = min(scroll_bar_length, self.term_h - scroll_bar_start-1)
            scroll_bar_length = max(1, scroll_bar_length)
            for i in range(scroll_bar_length):
                v = max(self.top_space+int(bool(self.header)), scroll_bar_start-scroll_bar_length//2)
                self.stdscr.addstr(scroll_bar_start+i, self.rows_w-1, ' ', curses.color_pair(self.colours_start+18))

        # Display refresh symbol
        if self.auto_refresh:
            if self.refreshing_data:
                self.stdscr.addstr(0,self.term_w-3,"  ", curses.color_pair(self.colours_start+21) | curses.A_BOLD)
            else:
                self.stdscr.addstr(0,self.term_w-3,"  ", curses.color_pair(self.colours_start+23) | curses.A_BOLD)

        ## Display footer
        if self.show_footer:
            # self.footer = NoFooter(self.stdscr, self.colours_start, self.get_function_data)
            h, w = self.stdscr.getmaxyx()
            try:
                self.footer.draw(self.term_h, self.term_w)
            except:
                pass
        elif self.footer_string:
            footer_string_width = min(self.term_w-1, len(self.footer_string)+2)
            disp_string = f" {self.footer_string[:footer_string_width]:>{footer_string_width-2}} "
            self.stdscr.addstr(self.term_h - 1, self.term_w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(self.term_h - 1, self.term_w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))

        if self.split_right and self.split_right_function(self.stdscr, 0,0,0,0,{},[],[],"",test=True):
            self.right_pane_previous_data = self.split_right_function(
                self.stdscr, 
                x = self.rows_w,
                y = self.top_space - int(bool(self.show_header and self.header)),
                w = self.term_w-self.rows_w,
                h = self.items_per_page + int(bool(self.show_header and self.header)),
                state = self.get_function_data(),
                row = self.indexed_items[self.cursor_pos] if self.indexed_items else [],
                cell = self.indexed_items[self.cursor_pos][1][self.selected_column] if self.indexed_items else "",
                data=self.split_right_data,
            )
        
        self.stdscr.refresh()
        ## Display infobox
        if self.display_infobox:
            self.infobox(self.stdscr, message=self.infobox_items, title=self.infobox_title)
            # self.stdscr.timeout(2000)  # timeout is set to 50 in order to get the infobox to be displayed so here we reset it to 2000



    def infobox(self, stdscr: curses.window, message: str ="", title: str ="Infobox",  colours_end: int = 0, duration: int = 4) -> curses.window:
        """ Display non-interactive infobox window. """

        self.logger.info(f"function: infobox()")
        h, w = stdscr.getmaxyx()
        notification_width, notification_height = w//2, 3*h//5
        message_width = notification_width-5

        if not message: message = "!!"
        if isinstance(message, str):
            submenu_items = ["  "+message[i*message_width:(i+1)*message_width] for i in range(len(message)//message_width+1)]
        else:
            submenu_items = message

        notification_remap_keys = { 
            curses.KEY_RESIZE: curses.KEY_F5,
            27: ord('q')
        }
        if len(submenu_items) > notification_height - 2:
            submenu_items = submenu_items[:notification_height-3] + [f"{'....':^{notification_width}}"]
        while True:
            h, w = stdscr.getmaxyx()

            submenu_win = curses.newwin(notification_height, notification_width, 3, w - (notification_width+4))
            infobox_data = {
                "items": submenu_items,
                "colours": notification_colours,
                "colours_start": self.notification_colours_start,
                "disabled_keys": [ord('z'), ord('c')],
                "show_footer": False,
                "top_gap": 0,
                "key_remappings": notification_remap_keys,
                "display_only": True,
                "hidden_columns": [],
                "title": title,
                "reset_colours": False,
                "cell_cursor": False,
                "split_right": False,
            }

            OptionPicker = Picker(submenu_win, **infobox_data)
            s, o, f = OptionPicker.run()
            if o != "refresh": break

        return submenu_win

    def get_function_data(self) -> dict:
        self.logger.debug(f"function: get_function_data()")
        """ Returns a dict of the main variables needed to restore the state of list_pikcer. """
        function_data = {
            "selections":                       self.selections,
            "cell_selections":                  self.cell_selections,
            "selected_cells_by_row":            self.selected_cells_by_row,
            "items_per_page":                   self.items_per_page,
            "current_row":                      self.current_row,
            "current_page":                     self.current_page,
            "cursor_pos":                       self.cursor_pos,
            "colours":                          self.colours,
            "colour_theme_number":              self.colour_theme_number,
            "selected_column":                  self.selected_column,
            "sort_column":                      self.sort_column,
            "sort_method":                      self.sort_method,
            "sort_reverse":                     self.sort_reverse,
            "SORT_METHODS":                     self.SORT_METHODS,
            "hidden_columns":                   self.hidden_columns,
            "is_selecting":                     self.is_selecting,
            "is_deselecting":                   self.is_deselecting,
            "user_opts":                        self.user_opts,
            "options_list":                     self.options_list,
            "user_settings":                    self.user_settings,
            "separator":                        self.separator,
            "search_query":                     self.search_query,
            "search_count":                     self.search_count,
            "search_index":                     self.search_index,
            "filter_query":                     self.filter_query,
            "indexed_items":                    self.indexed_items,
            "start_selection":                  self.start_selection,
            "start_selection_col":              self.start_selection_col,
            "end_selection":                    self.end_selection,
            "highlights":                       self.highlights,
            "max_column_width":                 self.max_column_width,
            "column_indices":                   self.column_indices,
            "mode_index":                       self.mode_index,
            "modes":                            self.modes,
            "title":                            self.title,
            "display_modes":                    self.display_modes,
            "require_option":                   self.require_option,
            "require_option_default":           self.require_option_default,
            "option_functions":                 self.option_functions,
            "top_gap":                          self.top_gap,
            "number_columns":                   self.number_columns,
            "items":                            self.items,
            "indexed_items":                    self.indexed_items,
            "header":                           self.header,
            "scroll_bar":                       self.scroll_bar,
            "columns_sort_method":              self.columns_sort_method,
            "disabled_keys":                    self.disabled_keys,
            "show_footer":                      self.show_footer,
            "footer_string":                    self.footer_string,
            "footer_string_auto_refresh":       self.footer_string_auto_refresh,
            "footer_string_refresh_function":   self.footer_string_refresh_function,
            "footer_timer":                     self.footer_timer,
            "footer_style":                     self.footer_style,
            "colours_start":                    self.colours_start,
            "colours_end":                      self.colours_end,
            "display_only":                     self.display_only,
            "infobox_items":                    self.infobox_items,
            "display_infobox":                  self.display_infobox,
            "infobox_title":                    self.infobox_title,
            "key_remappings":                   self.key_remappings,
            "auto_refresh":                     self.auto_refresh,
            "get_new_data":                     self.get_new_data,
            "refresh_function":                 self.refresh_function,
            "timer":                            self.timer,
            "get_data_startup":                 self.get_data_startup,
            "get_footer_string_startup":        self.get_footer_string_startup,
            "editable_columns":                 self.editable_columns,
            "last_key":                         self.last_key,
            "centre_in_terminal":               self.centre_in_terminal,
            "centre_in_terminal_vertical":      self.centre_in_terminal_vertical,
            "centre_in_cols":                   self.centre_in_cols,
            "highlight_full_row":               self.highlight_full_row,
            "cell_cursor":                      self.cell_cursor,
            "column_widths":                    self.column_widths,
            "track_entries_upon_refresh":       self.track_entries_upon_refresh,
            "pin_cursor":                       self.pin_cursor,
            "id_column":                        self.id_column,
            "startup_notification":             self.startup_notification,
            "keys_dict":                        self.keys_dict,
            "cancel_is_back":                   self.cancel_is_back,
            "paginate":                         self.paginate,
            "leftmost_char":                    self.leftmost_char,
            "history_filter_and_search" :       self.history_filter_and_search,
            "history_pipes" :                   self.history_pipes,
            "history_opts" :                    self.history_opts,
            "history_edits" :                   self.history_edits,
            "history_settings":                 self.history_settings,
            "show_header":                      self.show_header,
            "show_row_header":                  self.show_row_header,
            "debug":                            self.debug,
            "debug_level":                      self.debug_level,
            "reset_colours":                    self.reset_colours,
            "unicode_char_width":               self.unicode_char_width,
            "command_stack":                    self.command_stack,
            "loaded_file":                      self.loaded_file,
            "loaded_files":                     self.loaded_files,
            "loaded_file_index":                self.loaded_file_index,
            "loaded_file_states":               self.loaded_file_states,
            "sheet_index":                      self.sheet_index,
            "sheets":                           self.sheets,
            "sheet_name":                       self.sheet_name,
            "sheet_states":                     self.sheet_states,
            "split_right":                      self.split_right,
            "split_right_proportion":           self.split_right_proportion,
            "split_right_function":             self.split_right_function,
            "split_right_auto_refresh":         self.split_right_auto_refresh,
            "split_right_refresh_data_timer":   self.split_right_refresh_data_timer,
            "split_right_refresh_data":         self.split_right_refresh_data,
            "split_right_data":                 self.split_right_data,
        }
        return function_data

    def set_function_data(self, function_data: dict, reset_absent_variables: bool = False, do_not_set: list=[]) -> None:
        """ Set variables from state dict containing core variables."""
        self.logger.info(f"function: set_function_data()")
        variables = self.get_function_data().keys()

        x = Picker(self.stdscr, reset_colours=False)


        common_picker_vars = [
            "loaded_file_index",
            "loaded_file_states",
            "loaded_files",
            "loaded_file",
            "command_stack",
            "colour_theme_number",
            "reset_colours",
            "show_footer",
            "show_header",
            "history_filter_and_search",
            "history_settings",
            "history_opts",
            "history_edits",
            "history_pipes",
            "reset_colours",
            "cell_cursor",
            "top_gap",
            "unicode_char_width",
            "show_row_header",
            "centre_in_terminal_vertical",
            "centre_in_cols",
            "centre_in_terminal",
            "split_right",
            "split_right_proportion",
            "split_right_function",
        ]

        for var in variables:
            if var in function_data:
                setattr(self, var, function_data[var])
            elif reset_absent_variables and var not in common_picker_vars and var not in do_not_set:
                # Set value to the default for an empty picker
                setattr(self, var, getattr(x, var))


        reset_colours = bool("colour_theme_number" in function_data)
        self.initialise_picker_state(reset_colours=reset_colours)

        self.initialise_variables()
        # if "colour_theme_number" in function_data:
        #     global COLOURS_SET
        #     COLOURS_SET = False
        #     colours_end = set_colours(pick=self.colour_theme_number, start=self.colours_start)
                
        # if "items" in function_data: self.items = function_data["items"]
        # if "header" in function_data: self.header = function_data["header"]
        # self.indexed_items = function_data["indexed_items"] if "indexed_items" in function_data else []



    def delete_entries(self) -> None:
        """ Delete entries from view. """

        self.logger.info(f"function: delete_entries()")
        # Remove selected items from the list
        selected_indices = [index for index, selected in self.selections.items() if selected]
        if not selected_indices:
            # Remove the currently focused item if nothing is selected
            selected_indices = [self.indexed_items[self.cursor_pos][0]]

        self.items = [item for i, item in enumerate(self.items) if i not in selected_indices]
        self.indexed_items = [(i, item) for i, item in enumerate(self.items)]
        self.selections = {i:False for i in range(len(self.indexed_items))}
        self.cursor_pos = min(self.cursor_pos, len(self.indexed_items)-1)
        self.initialise_variables()
        self.draw_screen(self.indexed_items, self.highlights)


    def choose_option(
            self,
            stdscr: curses.window,
            options: list[list[str]] =[],
            title: str = "Choose option",
            x:int=0,
            y:int=0,
            literal:bool=False,
            colours_start:int=0,
            header: list[str] = [],
            require_option:list = [],
            option_functions: list = [],
    ) -> Tuple[dict, str, dict]:
        """
        Display input field at x,y

        ---Arguments
            stdscr: curses screen
            usrtxt (str): text to be edited by the user
            title (str): The text to be displayed at the start of the text option picker
            x (int): prompt begins at (x,y) in the screen given
            y (int): prompt begins at (x,y) in the screen given
            colours_start (bool): start index of curses init_pair.

        ---Returns
            usrtxt, return_code
            usrtxt: the text inputted by the user
            return_code: 
                            0: user hit escape
                            1: user hit return
        """
        self.logger.info(f"function: choose_option()")
        if options == []: options = [[f"{i}"] for i in range(10)]
        cursor = 0

        
        option_picker_data = {
            "items": options,
            "colours": notification_colours,
            "colours_start": self.notification_colours_start,
            "title":title,
            "header":header,
            "hidden_columns":[],
            "require_option":require_option,
            "keys_dict": options_keys,
            "show_footer": False,
            "cancel_is_back": True,
            "number_columns": False,
            "reset_colours": False,
            "split_right": False,
        }
        while True:
            h, w = stdscr.getmaxyx()

            choose_opts_widths = get_column_widths(options, unicode_char_width=self.unicode_char_width)
            window_width = min(max(sum(choose_opts_widths) + 6, 50) + 6, w)
            window_height = min(h//2, max(6, len(options)+3))

            submenu_win = curses.newwin(window_height, window_width, (h-window_height)//2, (w-window_width)//2)
            submenu_win.keypad(True)
            OptionPicker = Picker(submenu_win, **option_picker_data)
            s, o, f = OptionPicker.run()

            if o == "refresh": 
                self.draw_screen(self.indexed_items, self.highlights)
                continue
            if s:
                return {x: options[x] for x in s}, o, f
            return {}, "", f
            


    def notification(self, stdscr: curses.window, message: str="", title:str="Notification", colours_end: int=0, duration:int=4) -> None:

        self.logger.info(f"function: notification()")
        """ Notification box. """
        notification_width, notification_height = 50, 7
        message_width = notification_width-5

        if not message: message = "!!"
        submenu_items = ["  "+message[i*message_width:(i+1)*message_width] for i in range(len(message)//message_width+1)]

        notification_remap_keys = { 
            curses.KEY_RESIZE: curses.KEY_F5,
            27: ord('q')
        }
        while True:
            h, w = stdscr.getmaxyx()

            submenu_win = curses.newwin(notification_height, notification_width, 3, w - (notification_width+4))
            notification_data = {
                "items": submenu_items,
                "title": title,
                "colours_start": self.notification_colours_start,
                "show_footer": False,
                "centre_in_terminal": True,
                "centre_in_terminal_vertical": True,
                "centre_in_cols": True,
                "hidden_columns": [],
                "keys_dict": notification_keys,
                "disabled_keys": [ord('z'), ord('c')],
                "highlight_full_row": True,
                "top_gap": 0,
                "cancel_is_back": True,
                "reset_colours": False,
                "split_right": False,

            }
            OptionPicker = Picker(submenu_win, **notification_data)
            s, o, f = OptionPicker.run()

            if o != "refresh": break
            submenu_win.clear()
            submenu_win.refresh()
            del submenu_win
            stdscr.clear()
            stdscr.refresh()
            self.draw_screen(self.indexed_items, self.highlights)
        # set_colours(colours=get_colours(0))

    def toggle_column_visibility(self, col_index:int) -> None:
        """ Toggle the visibility of the column at col_index. """
        self.logger.info(f"function: toggle_column_visibility()")
        if 0 <= col_index < len(self.items[0]):
            if col_index in self.hidden_columns:
                self.hidden_columns.remove(col_index)
            else:
                self.hidden_columns.append(col_index)

    def apply_settings(self) -> None:
        """ 
        The users settings will be stored in the user_settings variable. This function applies those settings.

        ![0-9]+ show/hide column
        s[0-9]+ set column focus for sort
        g[0-9]+ go to index
        p[0-9]+ go to page
        nohl    hide search highlights
        """
        self.logger.info(f"function: apply_settings()")
        if self.user_settings:
            settings = re.split(r'\s+', self.user_settings)
            for setting in settings:
                if len(setting) == 0: continue

                if setting[0] == "!" and len(setting) > 1:
                    if setting[1:].isnumeric():
                        cols = setting[1:].split(",")
                        for col in cols:
                            self.toggle_column_visibility(int(col))
                    elif setting[1] == "r":
                        self.auto_refresh = not self.auto_refresh
                    elif setting[1] == "h":
                        self.highlights_hide = not self.highlights_hide
                elif setting.isnumeric():
                    self.cursor_pos = max(0, min(int(setting), len(self.indexed_items)-1))
                elif setting.startswith("col") and setting[3:].isnumeric():
                    col = int(setting[3:])
                    if 0 <= col < len(self.column_widths):
                        self.selected_column = col

                elif setting in ["nhl", "nohl", "nohighlights"]:
                    # highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]
                    
                    self.highlights_hide = not self.highlights_hide
                elif setting.startswith("s") and setting[1:].isnumeric():
                    if 0 <= int(setting[1:]) < len(self.items[0]):
                        self.sort_column = int(setting[1:])
                        if len(self.indexed_items):
                            current_pos = self.indexed_items[self.cursor_pos][0]
                        sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort items based on new column
                        if len(self.indexed_items):
                            new_pos = [row[0] for row in self.indexed_items].index(current_pos)
                            self.cursor_pos = new_pos
                elif setting == "ct":
                    self.centre_in_terminal = not self.centre_in_terminal
                elif setting == "cc":
                    self.centre_in_cols = not self.centre_in_cols
                elif setting == "cv":
                    self.centre_in_terminal_vertical = not self.centre_in_terminal_vertical
                elif setting == "arb":
                    self.insert_row(self.cursor_pos)
                elif setting == "ara":
                    self.insert_row(self.cursor_pos+1)
                elif setting == "aca":
                    self.insert_column(self.selected_column+1)
                elif setting == "acb":
                    self.insert_column(self.selected_column)
                elif setting.startswith("ir"):
                    if setting[2:].isnumeric():
                        num = int(setting[2:])
                    else:
                        num = self.cursor_pos
                    self.insert_row(num)
                elif setting.startswith("ic"):
                    if setting[2:].isnumeric():
                        num = int(setting[2:])
                    else:
                        num = self.selected_column
                    self.insert_column(num)

                elif setting == "modes":
                    self.display_modes = not self.display_modes
                elif setting == "cell":
                    self.cell_cursor = not self.cell_cursor
                elif setting == "rh":
                    self.show_row_header = not self.show_row_header
                elif setting == "header":
                    self.show_header = not self.show_header
                elif setting[0] == "":
                    cols = setting[1:].split(",")
                elif setting == "footer":
                    self.show_footer = not self.show_footer
                    self.initialise_variables()
                elif setting == "pc":
                    self.pin_cursor = not self.pin_cursor
                elif setting == "unicode":
                    self.unicode_char_width = not self.unicode_char_width
                elif setting == "file_next":
                    self.command_stack.append(Command("setting", self.user_settings))
                    self.switch_file(increment=1)
                elif setting == "file_prev":
                    self.command_stack.append(Command("setting", self.user_settings))
                    self.switch_file(increment=-1)
                    # self.draw_screen(self.indexed_items, self.highlights)
                    # self.stdscr.refresh()

                elif setting == "sheet_next":
                    self.command_stack.append(Command("setting", self.user_settings))
                    self.switch_sheet(increment=1)
                elif setting == "sheet_prev":
                    self.command_stack.append(Command("setting", self.user_settings))
                    self.switch_sheet(increment=-1)

                elif setting.startswith("ft"):
                    if len(setting) > 2 and setting[2:].isnumeric():
                        num = int(setting[2:])
                        self.footer_style = max(len(self.footer_options)-1, num)
                        self.footer = self.footer_options[self.footer_style]
                    else:
                        self.footer_style = (self.footer_style+1)%len(self.footer_options)
                        self.footer = self.footer_options[self.footer_style]
                    self.initialise_variables()
                elif setting == "pane":
                    self.toggle_right_pane()

                elif setting.startswith("cwd="):
                    os.chdir(os.path.expandvars(os.path.expanduser(setting[len("cwd="):])))
                elif setting.startswith("hl"):
                    hl_list = setting.split(",")
                    if len(hl_list) > 1:
                        hl_list = hl_list[1:]
                        match = hl_list[0]
                        if len(hl_list) > 1: 
                            field = hl_list[1]
                            if field.isnumeric() and field != "-1":
                                field = int(field)
                            else:
                                field = "all"
                        else:
                            field = "all"
                        if len(hl_list) > 2 and hl_list[2].isnumeric():
                            colour_pair = int(hl_list[2])
                        else:
                            colour_pair = 10

                        highlight = {
                            "match": match,
                            "field": field,
                            "color": colour_pair
                        }
                        self.highlights.append(highlight)
                        
                        
                elif setting.startswith("th"):
                    global COLOURS_SET
                    if curses.COLORS < 255:
                        self.notification(self.stdscr, message=f"Theme 4 applied.")

                    elif setting[2:].strip().isnumeric():
                        COLOURS_SET = False
                        try:
                            theme_number = int(setting[2:].strip())
                            self.colour_theme_number = min(get_theme_count()-1, theme_number)
                            set_colours(self.colour_theme_number)
                            self.draw_screen(self.indexed_items, self.highlights)
                            self.notification(self.stdscr, message=f"Theme {self.colour_theme_number} applied.")
                        except:
                            pass
                    else:
                        COLOURS_SET = False
                        self.colour_theme_number = (self.colour_theme_number + 1)%get_theme_count()
                        # self.colour_theme_number = int(not bool(self.colour_theme_number))
                        set_colours(self.colour_theme_number)
                        self.draw_screen(self.indexed_items, self.highlights)
                        self.notification(self.stdscr, message=f"Theme {self.colour_theme_number} applied.")

                else:
                    self.user_settings = ""
                    return None

            if self.user_settings:
                self.command_stack.append(Command("setting", self.user_settings))
                self.user_settings = ""

    def apply_command(self, command: Command):
        self.logger.info(f"function: apply_command()")
        if command.command_type == "setting":
            self.user_settings = command.command_value
            self.apply_settings()

    def redo(self):
        self.logger.info(f"function: redo()")
        if len(self.command_stack):
            self.apply_command(self.command_stack[-1])

    def toggle_item(self, index: int) -> None:
        """ Toggle selection of item at index. """
        self.logger.info(f"function: toggle_item()")
        self.selections[index] = not self.selections[index]
        self.draw_screen(self.indexed_items, self.highlights)

    def select_all(self) -> None:
        """ Select all in indexed_items. """
        self.logger.info(f"function: select_all()")
        for i in range(len(self.indexed_items)):
            self.selections[self.indexed_items[i][0]] = True
        for i in self.cell_selections.keys():
            self.cell_selections[i] = True
        for row in range(len(self.indexed_items)):
            self.selected_cells_by_row[row] = list(range(len(self.indexed_items[row][1])))
        self.draw_screen(self.indexed_items, self.highlights)

    def deselect_all(self) -> None:
        """ Deselect all items in indexed_items. """
        self.logger.info(f"function: deselect_all()")
        for i in range(len(self.selections)):
            self.selections[i] = False
        for i in self.cell_selections.keys():
            self.cell_selections[i] = False
        self.selected_cells_by_row = {}
        self.draw_screen(self.indexed_items, self.highlights)

    def handle_visual_selection(self, selecting:bool = True) -> None:
        """ Toggle visual selection or deselection. """
        self.logger.info(f"function: handle_visual_selection()")
        if not self.is_selecting and not self.is_deselecting and len(self.indexed_items) and len(self.indexed_items[0][1]):
            self.start_selection = self.cursor_pos
            self.start_selection_col = self.selected_column
            if selecting:
                self.is_selecting = True
            else:
                self.is_deselecting = True
        elif self.is_selecting:
            # end_selection = indexed_items[current_page * items_per_page + current_row][0]
            self.end_selection = self.cursor_pos
            if self.start_selection != -1:
                start = max(min(self.start_selection, self.end_selection), 0)
                end = min(max(self.start_selection, self.end_selection), len(self.indexed_items)-1)
                for i in range(start, end + 1):
                    if self.indexed_items[i][0] not in self.unselectable_indices:
                        self.selections[self.indexed_items[i][0]] = True
            if self.start_selection != -1:
                ystart = max(min(self.start_selection, self.end_selection), 0)
                yend = min(max(self.start_selection, self.end_selection), len(self.indexed_items)-1)
                xstart = min(self.start_selection_col, self.selected_column)
                xend = max(self.start_selection_col, self.selected_column)
                for i in range(ystart, yend + 1):
                    if self.indexed_items[i][0] not in self.unselectable_indices:
                        row = self.indexed_items[i][0]
                        if row not in self.selected_cells_by_row:
                            self.selected_cells_by_row[row] = []

                        for col in range(xstart, xend+1):
                            cell_index = (row, col)
                            self.cell_selections[cell_index] = True

                            self.selected_cells_by_row[row].append(col)
                        # Remove duplicates
                        self.selected_cells_by_row[row] = list(set(self.selected_cells_by_row[row]))

            self.start_selection = -1
            self.end_selection = -1
            self.is_selecting = False

            self.draw_screen(self.indexed_items, self.highlights)

        elif self.is_deselecting:
            self.end_selection = self.indexed_items[self.cursor_pos][0]
            self.end_selection = self.cursor_pos
            if self.start_selection != -1:
                start = max(min(self.start_selection, self.end_selection), 0)
                end = min(max(self.start_selection, self.end_selection), len(self.indexed_items)-1)
                for i in range(start, end + 1):
                    # selections[i] = False
                    self.selections[self.indexed_items[i][0]] = False
            if self.start_selection != -1:
                ystart = max(min(self.start_selection, self.end_selection), 0)
                yend = min(max(self.start_selection, self.end_selection), len(self.indexed_items)-1)
                xstart = min(self.start_selection_col, self.selected_column)
                xend = max(self.start_selection_col, self.selected_column)
                for i in range(ystart, yend + 1):
                    row = self.indexed_items[i][0]
                    if self.indexed_items[i][0] not in self.unselectable_indices:
                        if row in self.selected_cells_by_row:
                            for col in range(xstart, xend+1):
                                try:
                                    self.selected_cells_by_row[row].remove(col)
                                except:
                                    pass
                                cell_index = (row, col)
                                self.cell_selections[cell_index] = False
                            if self.selected_cells_by_row[row] == []:
                                del self.selected_cells_by_row[row]

            self.start_selection = -1
            self.end_selection = -1
            self.is_deselecting = False
            self.draw_screen(self.indexed_items, self.highlights)

    def cursor_down(self, count=1) -> bool:
        """ Move cursor down. """
        self.logger.info(f"function: cursor_down()")
        if len(self.indexed_items) == 0 or self.cursor_pos == len(self.indexed_items) -1:
            return False
        # Returns: whether page is turned
        new_pos = self.cursor_pos + 1
        new_pos = min(self.cursor_pos+count, len(self.indexed_items)-1)
        while True:
            if self.indexed_items[new_pos][0] in self.unselectable_indices: new_pos+=1
            else: break
        self.cursor_pos = new_pos
        return True

    def cursor_up(self, count=1) -> bool:
        """ Move cursor up. """
        self.logger.info(f"function: cursor_up()")
        # Returns: whether page is turned

        new_pos = max(self.cursor_pos - count, 0)
        while True:
            if new_pos < 0: return False
            elif new_pos in self.unselectable_indices: new_pos -= 1
            else: break
        self.cursor_pos = new_pos
        return True

    def remapped_key(self, key: int, val: int, key_remappings: dict) -> bool:
        """ Check if key has been remapped to val in key_remappings. """
        # self.logger.info(f"function: remapped_key()")
        if key in key_remappings:
            if key_remappings[key] == val or (isinstance(key_remappings[key], list) and val in key_remappings[key]):
                return True
        return False

    def check_key(self, function: str, key: int,  keys_dict: dict) -> bool:
        """
        Check if $key is assigned to $function in the keys_dict. 
            Allows us to redefine functions to different keys in the keys_dict.

        E.g., keys_dict = { $key, "help": ord('?') }, 
        """
        if function in keys_dict and key in keys_dict[function]:
            return True
        return False

    def copy_dialogue(self) -> None:
        """ Display dialogue to select how rows/cells should be copied. """
        self.logger.info(f"function: copy_dialogue()")
        copy_header = [
            "Representation",
            "Columns",
        ]
        options = [
            ["Python list of lists", "Exclude hidden"],
            ["Python list of lists", "Include hidden"],
            ["Tab-separated values", "Exclude hidden"],
            ["Tab-separated values", "Include hidden"],
            ["Comma-separated values", "Exclude hidden"],
            ["Comma-separated values", "Include hidden"],
            ["Custom separator", "Exclude hidden"],
            ["Custom separator", "Include hidden"],
        ]
        require_option = [False, False, False, False, False, False, True, True]
        s, o, f = self.choose_option(self.stdscr, options=options, title="Copy selected", header=copy_header, require_option=require_option)


        funcs = [
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="python", copy_hidden_cols=False, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="python", copy_hidden_cols=True, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="tsv", copy_hidden_cols=False, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="tsv", copy_hidden_cols=True, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="csv", copy_hidden_cols=False, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="csv", copy_hidden_cols=True, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="custom_sv", copy_hidden_cols=False, separator=o, cellwise=cell_cursor),
            lambda items, indexed_items, selections, cell_selections, hidden_columns, cell_cursor: copy_to_clipboard(items, indexed_items, selections, cell_selections, hidden_columns, representation="custom_sv", copy_hidden_cols=True, separator=o, cellwise=cell_cursor),
        ]

        # Copy items based on selection
        if s:
            for idx in s.keys():
                funcs[idx](self.items, self.indexed_items, self.selections, self.cell_selections, self.hidden_columns, self.cell_cursor)
    def paste_dialogue(self) -> None:
        """ Display dialogue to select how to paste from the clipboard. """
        self.logger.info(f"function: paste_dialogue()")
        paste_header = [
            "Representation",
            "Columns",
        ]
        options = [
            ["Paste values", ""],
        ]
        require_option = [False]
        s, o, f = self.choose_option(self.stdscr, options=options, title="Paste values", header=paste_header, require_option=require_option)


        funcs = [
            lambda items, pasta, paste_row, paste_col: paste_values(items, pasta, paste_row, paste_col)
        ]

        try:
            pasta = eval(pyperclip.paste())
            if type(pasta) == type([]):
                acceptable_data_type = True
                for row in pasta:
                    if type(row) != type([]):
                        acceptable_data_type = False
                        break

                    for cell in row:
                        if cell != None and type(cell) != type(""):
                            acceptable_data_type = False
                            break
                    if not acceptable_data_type:
                        break
                if not acceptable_data_type:
                    self.draw_screen(self.indexed_items, self.highlights)
                    self.notification(self.stdscr, message="Error pasting data.")
                    return None

        except:
            self.draw_screen(self.indexed_items, self.highlights)
            self.notification(self.stdscr, message="Error pasting data.")
            return None
        if type(pasta) == type([]) and len(pasta) > 0 and type(pasta[0]) == type([]):
            if s:
                for idx in s.keys():
                    return_val, tmp_items = funcs[idx](self.items, pasta, self.cursor_pos, self.selected_column)
                    if return_val:
                        cursor_pos = self.cursor_pos
                        self.items = tmp_items
                        self.initialise_variables()
                        self.cursor_pos = cursor_pos

    def save_dialog(self) -> None:
        """ Display dialogue to select how to save the picker data. """
        self.logger.info(f"function: save_dialog()")
        
        dump_header = []
        options = [ 
            ["Save data (pickle)."],
            ["Save data (csv)."],
            ["Save data (tsv)."],
            ["Save data (json)."],
            ["Save data (feather)."],
            ["Save data (parquet)."],
            ["Save data (msgpack)."],
            ["Save state"]
        ]
        # require_option = [True, True, True, True, True, True, True, True]
        s, o, f = self.choose_option(self.stdscr, options=options, title="Save...", header=dump_header)


        funcs = [
            lambda opts: dump_data(self.get_function_data(), opts),
            lambda opts: dump_data(self.get_function_data(), opts, format="csv"),
            lambda opts: dump_data(self.get_function_data(), opts, format="tsv"),
            lambda opts: dump_data(self.get_function_data(), opts, format="json"),
            lambda opts: dump_data(self.get_function_data(), opts, format="feather"),
            lambda opts: dump_data(self.get_function_data(), opts, format="parquet"),
            lambda opts: dump_data(self.get_function_data(), opts, format="msgpack"),
            lambda opts: dump_state(self.get_function_data(), opts),
        ]
        
        if s:
            for idx in s.keys():
                save_path_entered, save_path = output_file_option_selector(
                    self.stdscr,
                    refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights)
                )
                if save_path_entered:
                    return_val = funcs[idx](save_path)
                    if return_val:
                        self.notification(self.stdscr, message=return_val, title="Error")

    def load_dialog(self) -> None:
        """ Display dialogue to select which file to load and in what way it should be loaded. """
        self.logger.info(f"function: load_dialog()")
        
        dump_header = []
        options = [ 
            ["Load data (pickle)."],
        ]
        s, o, f = self.choose_option(self.stdscr, options=options, title="Open file...", header=dump_header)


        funcs = [
            lambda opts: load_state(opts)
        ]

        if s:
            restrict_curses(self.stdscr)
            files_to_load = file_picker()
            unrestrict_curses(self.stdscr)
            if files_to_load:
                index = list(s.keys())[0]
                file_to_load = files_to_load[0]
                return_val = funcs[index](file_to_load)

                self.loaded_file_states[self.loaded_file_index] = self.get_function_data()

                self.stdscr.clear()
                self.draw_screen(self.indexed_items, self.highlights)

                tmp = self.stdscr

                self.loaded_files += files_to_load
                self.loaded_file_states += [{} for _ in files_to_load]
                self.loaded_file = file_to_load
                self.loaded_file_index = len(self.loaded_files)-len(files_to_load)


                self.stdscr = tmp

                self.notification(self.stdscr, f"{repr(file_to_load)} has been loaded!")

                self.set_function_data({}, reset_absent_variables=True)
                self.load_file(self.loaded_file)
                # items = return_val["items"]
                # header = return_val["header"]
                self.stdscr.clear()
                # self.initialise_variables()
                self.draw_screen(self.indexed_items, self.highlights)
                # self.stdscr.refresh()

                # if return_val:
                #     notification(stdscr, message=return_val, title="Error")

    def set_registers(self):
        """ Set registers to be sent to the input field. """
        self.logger.info(f"function: set_registers()")
        self.registers = {"*": self.indexed_items[self.cursor_pos][1][self.selected_column]} if len(self.indexed_items) and len(self.indexed_items[0][1]) else {}


    def fetch_data(self) -> None:
        """ Refesh data asynchronously. When data has been fetched self.data_ready is set to True. """
        self.logger.info(f"function: fetch_data()")
        tmp_items, tmp_header = self.refresh_function()
        if self.track_entries_upon_refresh:
            selected_indices = get_selected_indices(self.selections)
            self.ids = [item[self.id_column] for i, item in enumerate(self.items) if i in selected_indices]
            self.ids_tuples = [(i, item[self.id_column]) for i, item in enumerate(self.items) if i in selected_indices]
            self.selected_cells_by_row = get_selected_cells_by_row(self.cell_selections)

            if len(self.indexed_items) > 0 and len(self.indexed_items) >= self.cursor_pos and len(self.indexed_items[0][1]) >= self.id_column:
                try:
                    self.cursor_pos_id = self.indexed_items[self.cursor_pos][1][self.id_column]
                except:
                    self.logger.warning(f"fetch_data() len(indexed_items)={len(self.indexed_items)}, cusor_pos={self.cursor_pos}")
                    self.cursor_pos_id = -1
                self.cursor_pos_prev = self.cursor_pos
        with self.data_lock:
            self.items, self.header = tmp_items, tmp_header
            self.data_ready = True

    def save_input_history(self, file_path: str, force_save: bool=True) -> bool:
        """ Save input field history. Returns True if successful save. """
        self.logger.info(f"function: save_input_history()")
        file_path = os.path.expanduser(file_path)
        file_path = os.path.expandvars(file_path)
        directory = os.path.dirname(file_path)
        history_dict = {
            "history_filter_and_search" :       self.history_filter_and_search,
            "history_pipes" :                   self.history_pipes,
            "history_opts" :                    self.history_opts,
            "history_edits" :                   self.history_edits,
            "history_settings":                 self.history_settings,
        }
        if os.path.exists(directory) or force_save:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(history_dict, f)

        return True

    def load_input_history(self, file_path:str) -> bool:
        """ Load command history. Returns true if successful load. """
        self.logger.info(f"function: load_input_history()")
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'r') as f:
                history_dict = json.load(f)

            if "history_filter_and_search" in history_dict:
                self.history_filter_and_search = history_dict["history_filter_and_search"]
            if "history_pipes" in history_dict:
                self.history_pipes = history_dict["history_pipes"]
            if "history_opts" in history_dict:
                self.history_opts = history_dict["history_opts"]
            if "history_edits" in history_dict:
                self.history_edits = history_dict["history_edits"]
            if "history_settings" in history_dict:
                self.history_settings = history_dict["history_settings"]

        except:
            return False

        return True


    def get_word_list(self) -> list[str]:
        """ Get a list of all words used in any cell of the picker. Used for completion in search/filter input_field. """
        self.logger.info(f"function: get_word_list()")
        translator = str.maketrans('', '', string.punctuation)
        
        words = []
        # Extract words from lists
        for row in [x[1] for x in self.indexed_items]:
            for i, cell in enumerate(row):
                if i != (self.id_column%len(row)):
                # Split the item into words and strip punctuation from each word
                    words.extend(word.strip(string.punctuation) for word in cell.split())
        for cell in self.header:
            # Split the item into words and strip punctuation from each word
            words.extend(word.strip(string.punctuation) for word in cell.split())
        def key_f(s):
            if len(s):
                starts_with_char = s[0].isalpha()
            else:
                starts_with_char = False
            return (not starts_with_char, s.lower())
        # key = lambda s: (s != "" or not s[0].isalpha(), s)
        words = sorted(list(set(words)), key=key_f)
        return words

    def insert_row(self, pos: int):
        """ Insert a blank row at position `pos` """
        self.logger.info(f"function: insert_row(pos={pos})")

        if self.items != [[]]:
            row_len = 1
            if self.header: row_len = len(self.header)
            elif len(self.items): row_len  = len(self.items[0])
            # if len(self.indexed_items) == 0:
            #     insert_at_pos = 0
            # else:
            #     insert_at_pos = self.indexed_items[self.cursor_pos][0]
            self.items = self.items[:pos] + [["" for x in range(row_len)]] + self.items[pos:]
            if pos <= self.cursor_pos:
                self.cursor_pos += 1
            # We are adding a row before so we have to move the cursor down
            # If there is a filter then we know that an empty row doesn't match
            current_cursor_pos = self.cursor_pos
            self.initialise_variables()
            self.cursor_pos = current_cursor_pos
        else:
            self.items = [[""]]
            self.initialise_variables()

    def insert_column(self, pos:int):
        """ Insert blank column at `pos`"""
        self.logger.info(f"function: insert_column(pos={pos})")
        self.items = [row[:pos]+[""]+row[pos:] for row in self.items]
        self.header = self.header[:pos] + [""] + self.header[pos:]
        self.editable_columns = self.editable_columns[:pos] + [self.editable_by_default] + self.editable_columns[pos:]
        if pos <= self.selected_column:
            self.selected_column += 1
        current_cursor_pos = self.cursor_pos
        self.initialise_variables()
        self.cursor_pos = current_cursor_pos


    def load_file(self, filename: str) -> None:
        if not os.path.exists(filename):
            self.notification(self.stdscr, message = f"File not found: {filename}")
            return None

        try:
            filetype = guess_file_type(filename)
            items, header, sheets = table_to_list(filename, file_type=filetype)

            if items != None:
                self.items = items
                self.header = header if header != None else []
                self.sheets = sheets


                self.initialise_variables()
        except Exception as e:
            self.notification(self.stdscr, message=f"Error loading {filename}: {e}")

    def load_sheet(self, filename: str, sheet_number: int = 0):
        filetype = guess_file_type(filename)
        try:
            items, header, sheets = table_to_list(filename, file_type=filetype, sheet_number=sheet_number)
            if items != None:
                self.items = items
                self.header = header if header != None else []
                self.sheets = sheets

                self.initialise_variables()
        except Exception as e:
            self.notification(self.stdscr, message=f"Error loading {filename}, sheet {sheet_number}: {e}")

    def switch_file(self, increment=1) -> None:
        """ Go to the next file. """
        if len(self.loaded_files) <= 1:
            return None

        # Cache file state
        self.loaded_file_states[self.loaded_file_index] = self.get_function_data()

        self.loaded_file_index = (self.loaded_file_index + increment) % len(self.loaded_files)
        self.loaded_file = self.loaded_files[self.loaded_file_index]

        idx, file = self.loaded_file_index, self.loaded_file
        # If we already have a loaded state for this file
        if self.loaded_file_states[self.loaded_file_index]:
            self.set_function_data(self.loaded_file_states[self.loaded_file_index])
        else:
            self.set_function_data({}, reset_absent_variables=True)
            self.load_file(self.loaded_file)

        self.loaded_file_index, self.loaded_file = idx, file

    def switch_sheet(self, increment=1) -> None:
        if not os.path.exists(self.loaded_file):
            self.notification(self.stdscr, message=f"File {repr(self.loaded_file)} not found.")
            return None
        if len(self.sheets) <= 1:
            return None

        # Cache sheet state
        self.sheet_states[self.sheet_index] = self.get_function_data()

        self.sheet_index = (self.sheet_index + increment) % len(self.sheets)
        self.sheet_name = self.sheets[self.sheet_index]

        # If we already have a loaded state for this file
        if self.sheet_states[self.sheet_index]:
            self.set_function_data(self.sheet_states[self.sheet_index])
        else:
            function_data = {
                "sheet_index": self.sheet_index,
                "sheet_name":  self.sheet_name,
                "sheet_states":self.sheet_states,
                "sheets":       self.sheets,
            }
            self.set_function_data(function_data, reset_absent_variables=True)
            self.load_sheet(self.loaded_file, sheet_number=self.sheet_index)

    def toggle_right_pane(self):
        if self.split_right_function(self.stdscr, 0,0,0,0,{},[],[],"",test=True):
            self.split_right = not self.split_right


    def run(self) -> Tuple[list[int], str, dict]:
        """ Run the picker. """
        self.logger.info(f"function: run()")

        if self.get_footer_string_startup and self.footer_string_refresh_function != None:
            self.footer_string = self.footer_string_refresh_function()

        self.initialise_variables(get_data=self.get_data_startup)

        self.draw_screen(self.indexed_items, self.highlights)

        initial_time = time.time()
        initial_time_footer = time.time()-self.footer_timer
        initial_split_time = time.time()-self.split_right_refresh_data_timer

        if self.startup_notification:
            self.notification(self.stdscr, message=self.startup_notification)
            self.startup_notification = ""

        # curses.curs_set(0)
        # stdscr.nodelay(1)  # Non-blocking input
        # stdscr.timeout(2000)  # Set a timeout for getch() to ensure it does not block indefinitely
        self.stdscr.timeout(max(min(2000, int(self.timer*1000)//2, int(self.footer_timer*1000))//2, 20))  # Set a timeout for getch() to ensure it does not block indefinitely
        
        if self.clear_on_start:
            self.stdscr.clear()
            self.clear_on_start = False
        else:
            self.stdscr.erase()

        self.stdscr.refresh()

        # Initialize colours
        # Check if terminal supports color

        # Set terminal background color
        self.stdscr.bkgd(' ', curses.color_pair(self.colours_start+3))  # Apply background color
        self.draw_screen(self.indexed_items, self.highlights)

        if self.display_only:
            self.stdscr.refresh()
            function_data = self.get_function_data()
            return [], "", function_data

        # Open tty to accept input
        tty_fd = open_tty()

        h, w = self.stdscr.getmaxyx()
        self.term_h, self.term_w = self.stdscr.getmaxyx()
        if self.split_right and self.split_right_function(self.stdscr, 0,0,0,0,{},[],[],"",test=True):
            self.rows_w, self.rows_h = int(self.term_w*self.split_right_proportion), self.term_h
        else:
            self.rows_w, self.rows_h = self.term_w, self.term_h
        def terminal_resized(old_w, old_h) -> bool:
            w, h = os.get_terminal_size()
            if old_h != h or old_w != w: return True
            else: return False

        COLS, LINES = os.get_terminal_size()
        # Main loop
        while True:
            # key = self.stdscr.getch()

            key = get_char(tty_fd, timeout=0.2)
            if key != -1:
                self.logger.info(f"key={key}")

            self.term_resize_event = terminal_resized(COLS, LINES)
            COLS, LINES = os.get_terminal_size()
            if self.term_resize_event: 
                key = curses.KEY_RESIZE

            h, w = self.stdscr.getmaxyx()
            self.term_h, self.term_w = self.stdscr.getmaxyx()
            if self.split_right and self.split_right_function(self.stdscr, 0,0,0,0,{},[],[],"",test=True):
                self.rows_w, self.rows_h = int(self.term_w*self.split_right_proportion), self.term_h
            else:
                self.rows_w, self.rows_h = self.term_w, self.term_h

            if key in self.disabled_keys: continue
            clear_screen=True

            ## Refresh data asyncronously.
            if self.refreshing_data:
                self.logger.debug(f"Data refresh check")
                with self.data_lock:
                    if self.data_ready:
                        self.logger.debug(f"Data ready after refresh")
                        self.initialise_variables()

                        initial_time = time.time()

                        self.draw_screen(self.indexed_items, self.highlights, clear=False)

                        self.refreshing_data = False
                        self.data_ready = False

            elif self.check_key("refresh", key, self.keys_dict) or self.remapped_key(key, curses.KEY_F5, self.key_remappings) or (self.auto_refresh and (time.time() - initial_time) >= self.timer):
                self.logger.debug(f"Get new data (refresh).")
                self.stdscr.addstr(0,self.term_w-3,"  ", curses.color_pair(self.colours_start+21) | curses.A_BOLD)
                self.stdscr.refresh()
                if self.get_new_data and self.refresh_function:
                    self.refreshing_data = True

                    t = threading.Thread(target=self.fetch_data)
                    t.start()
                else:
                    function_data = self.get_function_data()
                    return [], "refresh", function_data

            # Refresh data synchronously
            # if self.check_key("refresh", key, self.keys_dict) or self.remapped_key(key, curses.KEY_F5, self.key_remappings) or (self.auto_refresh and (time.time() - initial_time) > self.timer):
            #     self.stdscr.addstr(0,w-3,"  ", curses.color_pair(self.colours_start+21) | curses.A_BOLD)
            #     self.stdscr.refresh()
            #     if self.get_new_data and self.refresh_function:
            #         self.initialise_variables(get_data=True)
            #
            #         initial_time = time.time()
            #         self.draw_screen(self.indexed_items, self.highlights, clear=False)
            #     else:
            #
            #         function_data = self.get_function_data()
            #         return [], "refresh", function_data

            if self.footer_string_auto_refresh and ((time.time() - initial_time_footer) > self.footer_timer):
                self.logger.debug(f"footer_string_auto_refresh")
                self.footer_string = self.footer_string_refresh_function()
                initial_time_footer = time.time()
                self.draw_screen(self.indexed_items, self.highlights)

            if self.split_right and self.split_right_auto_refresh and ((time.time() - initial_split_time) > self.split_right_refresh_data_timer):
                self.split_right_data = self.split_right_refresh_data(self.split_right_data, self.get_function_data())
                initial_split_time = time.time()

            if self.check_key("help", key, self.keys_dict):
                self.logger.info(f"key_function help")
                self.stdscr.clear()
                self.stdscr.refresh()
                help_data = {
                    # "items": help_lines,
                    "items": build_help_rows(self.keys_dict),
                    "title": f"{self.title} Help",
                    "colours_start": self.help_colours_start,
                    "colours": help_colours,
                    "show_footer": True,
                    "max_selected": 1,
                    "keys_dict": help_keys,
                    "disabled_keys": [ord('?'), ord('v'), ord('V'), ord('m'), ord('M'), ord('l'), curses.KEY_ENTER, ord('\n')],
                    "highlight_full_row": True,
                    "top_gap": 0,
                    "paginate": self.paginate,
                    "centre_in_terminal": False,
                    "centre_in_terminal_vertical": True,
                    "hidden_columns": [],
                    "reset_colours": False,
                    "cell_cursor": False,
                    "split_right": False,

                }
                OptionPicker = Picker(self.stdscr, **help_data)
                s, o, f = OptionPicker.run()
                self.draw_screen(self.indexed_items, self.highlights)

            if self.check_key("info", key, self.keys_dict):
                self.logger.info(f"key_function help")
                self.stdscr.clear()
                self.stdscr.refresh()
                import importlib.metadata as metadata
                version = metadata.version('listpick')

                info_items = [
                    ["  Listpick info", "-*"*30],
                    ["",""],
                    ["listpick version", f"{version}"],

                    ["",""],
                    ["  Global", "-*"*30],
                    ["",""],
                    ["current_file", self.loaded_file],
                    ["loaded_files", repr(self.loaded_files)],
                    ["auto_refresh", f"{repr(self.auto_refresh)}"],
                    ["timer", f"{repr(self.timer)}"],
                    ["pin_cursor", f"{repr(self.pin_cursor)}"],
                    ["cwd", f"{os.getcwd()}"],
                    ["Picker memory", f"{format_size(sys.getsizeof(self))}"],
                    ["debug", f"{repr(self.debug)}"],
                    ["debug level", f"{repr(self.debug_level)}"],

                    ["",""],
                    ["  Current File", "-*"*30],
                    ["",""],
                    # ["row/row count", f"{self.cursor_pos}/{len(self.indexed_items)}"],
                    ["Current row", f"{self.cursor_pos}/{len(self.indexed_items)}"],
                    ["Total rows", f"{len(self.items)}"],
                    ["Selection count", f"{self.selected_cells_by_row}"],
                    ["current_sheet", self.sheet_name],
                    ["sheets", repr(self.sheets)],
                    ["current column/column_count", f"{self.selected_column}/{len(self.column_widths)}"],
                    ["hidden columns", f"{self.hidden_columns}"],
                    ["sort column", f"{self.sort_column}"],
                    ["sort method", f"{self.SORT_METHODS[self.columns_sort_method[self.sort_column]]}"],
                    ["sort order", f"{'Descending' if self.sort_reverse[self.sort_column] else 'Ascending'}"],
                    ["id_column", f"{self.id_column}"],

                    ["",""],
                    ["  Display options", "-*"*30],
                    ["",""],
                    ["show_header", str(self.show_header)],
                    ["show_footer", repr(self.show_footer)],
                    ["show_row_header", repr(self.show_row_header)],
                    ["max_column_width", str(self.max_column_width)],
                    ["colour_theme_number", str(self.colour_theme_number)],
                    ["top_gap", str(self.top_gap)],
                    ["highlight_full_row", repr(self.highlight_full_row)],
                    ["cell_cursor", repr(self.cell_cursor)],
                    ["items_per_page", repr(self.items_per_page)],
                    ["paginate", repr(self.paginate)],
                    ["display_modes", repr(self.display_modes)],
                    ["footer_style", repr(self.footer_style)],
                    ["unicode_char_width", repr(self.unicode_char_width)],
                    ["centre_in_terminal", repr(self.centre_in_terminal)],
                    ["centre_in_cols", repr(self.centre_in_cols)],
                    ["centre_in_terminal_vertical", repr(self.centre_in_terminal_vertical)],
                ]
                
                data = self.get_function_data()
                data["indexed_items"] = f"[...] length = {len(data['indexed_items'])}"
                data["selections"] = f"[...] length = {len(data['selections'])}"
                data["selected_cells_by_row"] = f"[...] length = {len(data['selected_cells_by_row'])}"
                data["cell_selections"] = f"[...] length = {len(data['cell_selections'])}"
                data["items"] = f"[...] length = {len(data['items'])}"
                data["require_option"] = f"[...] length = {len(data['require_option'])}"
                data["option_functions"] = f"[...] length = {len(data['option_functions'])}"
                data["loaded_file_states"] = f"[...] length = {len(data['loaded_file_states'])}"
                data["sheet_states"] = f"[...] length = {len(data['sheet_states'])}"
                info_items += [
                    ["",""],
                    ["  get_function_data()", "-*"*30],
                    ["",""],
                    ["show_header", str(self.show_header)],
                ]
                info_items += [[key, repr(value)] for key, value in data.items()]


                for row in info_items:
                    if row[1] == "-*"*30:
                        continue
                    row[0] = "      " + row[0]

                info_header = ["Option", "Value"]
                info_data = {
                    "items": info_items,
                    "header": info_header,
                    "title": f"{self.title} Info",
                    "colours_start": self.help_colours_start,
                    "colours": help_colours,
                    "show_footer": True,
                    "max_selected": 1,
                    "keys_dict": help_keys,
                    "disabled_keys": [ord('?'), ord('v'), ord('V'), ord('m'), ord('M'), ord('l'), curses.KEY_ENTER, ord('\n')],
                    "highlight_full_row": True,
                    "top_gap": 0,
                    "paginate": self.paginate,
                    "centre_in_terminal": False,
                    "centre_in_terminal_vertical": True,
                    "hidden_columns": [],
                    "reset_colours": False,
                    "cell_cursor": False,
                    "split_right": False,

                }
                OptionPicker = Picker(self.stdscr, **info_data)
                s, o, f = OptionPicker.run()
                
                self.draw_screen(self.indexed_items, self.highlights)

            elif self.check_key("exit", key, self.keys_dict):
                self.stdscr.clear()
                if len(self.loaded_files) <= 1:
                    function_data = self.get_function_data()
                    function_data["last_key"] = key
                    return [], "", function_data
                else:
                    del self.loaded_files[self.loaded_file_index]
                    del self.loaded_file_states[self.loaded_file_index]
                    self.loaded_file_index = min(self.loaded_file_index, len(self.loaded_files)-1)
                    self.loaded_file = self.loaded_files[self.loaded_file_index]
                    idx, file = self.loaded_file_index, self.loaded_file


                    # If we already have a loaded state for this file
                    if self.loaded_file_states[self.loaded_file_index]:
                        self.set_function_data(self.loaded_file_states[self.loaded_file_index])
                    else:
                        self.set_function_data({}, reset_absent_variables=True)
                        self.load_file(self.loaded_file)
                    self.loaded_file_index, self.loaded_file = idx, file
                    self.draw_screen(self.indexed_items, self.highlights)

            elif self.check_key("full_exit", key, self.keys_dict):
                close_curses(self.stdscr)
                exit()

            elif self.check_key("settings_input", key, self.keys_dict):
                self.logger.info(f"Settings input")
                usrtxt = f"{self.user_settings.strip()} " if self.user_settings else ""
                field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                if self.show_footer and self.footer.height >= 2: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                self.set_registers()
                usrtxt, return_val = input_field(
                    self.stdscr,
                    usrtxt=usrtxt,
                    field_prefix=" Settings: ",
                    x=lambda:2,
                    y=lambda: self.stdscr.getmaxyx()[0]-1,
                    max_length=field_end_f,
                    registers=self.registers,
                    refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                    history=self.history_settings,
                    path_auto_complete=True,
                    formula_auto_complete=False,
                    function_auto_complete=False,
                    word_auto_complete=True,
                    auto_complete_words=["ft", "ct", "cv"],
                )
                if return_val:
                    self.user_settings = usrtxt
                    self.apply_settings()
                    self.history_settings.append(usrtxt)
                    self.user_settings = ""
            elif self.check_key("toggle_footer", key, self.keys_dict):
                self.logger.info(f"toggle footer")
                self.user_settings = "footer"
                self.apply_settings()

            elif self.check_key("settings_options", key, self.keys_dict):
                options = []
                if len(self.items) > 0:
                    options += [["cv", "Centre rows vertically"]]
                    options += [["pc", "Pin cursor to row number when data refreshes"]]
                    options += [["ct", "Centre column-set in terminal"]]
                    options += [["cc", "Centre values in cells"]]
                    options += [["!r", "Toggle auto-refresh"]]
                    options += [["th", "Cycle between themes. (accepts th#)"]]
                    options += [["nohl", "Toggle highlights"]]
                    options += [["footer", "Toggle footer"]]
                    options += [["header", "Toggle header"]]
                    options += [["rh", "Toggle row header"]]
                    options += [["modes", "Toggle modes"]]
                    options += [["ft", "Cycle through footer styles (accepts ft#)"]]
                    options += [["file_next", "Go to the next open file."]]
                    options += [["file_prev", "Go to the previous open file."]]
                    options += [["sheet_next", "Go to the next sheet."]]
                    options += [["sheet_prev", "Go to the previous sheet."]]
                    options += [["unicode", "Toggle b/w using len and wcwidth to calculate char width."]]
                    options += [["ara", "Add empty row after cursor."]]
                    options += [["arb", "Add empty row before the cursor."]]
                    options += [["aca", "Add empty column after the selected column."]]
                    options += [["acb", "Add empty column before the selected column."]]
                    options += [[f"col{i}", f"Select column {i}"] for i in range(len(self.items[0]))]
                    options += [[f"s{i}", f"Sort by column {i}"] for i in range(len(self.items[0]))]
                    options += [[f"!{i}", f"Toggle visibility of column {i}"] for i in range(len(self.items[0]))]


                settings_options_header = ["Key", "Setting"]

                s, o, f = self.choose_option(self.stdscr, options=options, title="Settings", header=settings_options_header)
                if s:
                    self.user_settings = " ".join([x[0] for x in s.values()])
                    self.apply_settings()

            elif self.check_key("redo", key, self.keys_dict):
                self.redo()
            # elif self.check_key("move_column_left", key, self.keys_dict):
            #     tmp1 = self.column_indices[self.selected_column]
            #     tmp2 = self.column_indices[(self.selected_column-1)%len(self.column_indices)]
            #     self.column_indices[self.selected_column] = tmp2
            #     self.column_indices[(self.selected_column-1)%(len(self.column_indices))] = tmp1
            #     self.selected_column = (self.selected_column-1)%len(self.column_indices)
            #     # self.notification(self.stdscr, f"{str(self.column_indices)}, {tmp1}, {tmp2}")
            #     self.initialise_variables()
            #     self.column_widths = get_column_widths([v[1] for v in self.indexed_items], header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=w)
            #     self.draw_screen(self.indexed_items, self.highlights)
            #     # self.move_column(direction=-1)
            #
            # elif self.check_key("move_column_right", key, self.keys_dict):
            #     tmp1 = self.column_indices[self.selected_column]
            #     tmp2 = self.column_indices[(self.selected_column+1)%len(self.column_indices)]
            #     self.column_indices[self.selected_column] = tmp2
            #     self.column_indices[(self.selected_column+1)%(len(self.column_indices))] = tmp1
            #     self.selected_column = (self.selected_column+1)%len(self.column_indices)
            #     self.initialise_variables()
            #     self.draw_screen(self.indexed_items, self.highlights)
            #     # self.move_column(direction=1)

            elif self.check_key("cursor_down", key, self.keys_dict):
                page_turned = self.cursor_down()
                if not page_turned: clear_screen = False
            elif self.check_key("half_page_down", key, self.keys_dict):
                self.cursor_down(count=self.items_per_page//2)
                clear_screen = True
            elif self.check_key("five_down", key, self.keys_dict):
                clear_screen = False
                self.cursor_down(count=5)
                clear_screen = True
            elif self.check_key("cursor_up", key, self.keys_dict):
                page_turned = self.cursor_up()
                if not page_turned: clear_screen = False
            elif self.check_key("five_up", key, self.keys_dict):
                # if self.cursor_up(count=5): clear_screen = True
                self.cursor_up(count=5)
                clear_screen = True
            elif self.check_key("half_page_up", key, self.keys_dict):
                self.cursor_up(count=self.items_per_page//2)
                clear_screen = True

            elif self.check_key("toggle_select", key, self.keys_dict):
                if len(self.indexed_items) > 0:
                    item_index = self.indexed_items[self.cursor_pos][0]
                    cell_index = (self.indexed_items[self.cursor_pos][0], self.selected_column)
                    row, col = cell_index
                    selected_count = sum(self.selections.values())
                    if self.max_selected == -1 or selected_count >= self.max_selected:
                        self.toggle_item(item_index)

                        self.cell_selections[cell_index] = not self.cell_selections[cell_index]
                        ## Set self.selected_cells_by_row
                        # If any cells in the current row are selected
                        if row in self.selected_cells_by_row:
                            # If the current cell is selected then remove it
                            if col in self.selected_cells_by_row[row]:
                                # If the current cell is the only cell in the row that is selected then remove the row from the dict
                                if len(self.selected_cells_by_row[row]) == 1:

                                    del self.selected_cells_by_row[row]
                                # else remove only the index of the current cell
                                else:
                                    self.selected_cells_by_row[row].remove(col)
                            # If there are cells in the row that are selected then append the current cell to the row
                            else:
                                self.selected_cells_by_row[row].append(col)
                        # Add the a list containing only the current column
                        else:
                            self.selected_cells_by_row[row] = [col]

                self.cursor_down()
            elif self.check_key("select_all", key, self.keys_dict):  # Select all (m or ctrl-a)
                self.select_all()

            elif self.check_key("select_none", key, self.keys_dict):  # Deselect all (M or ctrl-r)
                self.deselect_all()

            elif self.check_key("cursor_top", key, self.keys_dict):
                new_pos = 0
                while True:
                    if new_pos in self.unselectable_indices: new_pos+=1
                    else: break
                if new_pos < len(self.indexed_items):
                    self.cursor_pos = new_pos

                self.draw_screen(self.indexed_items, self.highlights)

            elif self.check_key("cursor_bottom", key, self.keys_dict):
                new_pos = len(self.indexed_items)-1
                while True:
                    if new_pos in self.unselectable_indices: new_pos-=1
                    else: break
                if new_pos < len(self.items) and new_pos >= 0:
                    self.cursor_pos = new_pos
                self.draw_screen(self.indexed_items, self.highlights)
                # current_row = items_per_page - 1
                # if current_page + 1 == (len(self.indexed_items) + items_per_page - 1) // items_per_page:
                #
                #     current_row = (len(self.indexed_items) +items_per_page - 1) % items_per_page
                # self.draw_screen(self.indexed_items, self.highlights)
            elif self.check_key("enter", key, self.keys_dict):
                self.logger.info(f"key_function enter")
                # Print the selected indices if any, otherwise print the current index
                if self.is_selecting or self.is_deselecting: self.handle_visual_selection()
                if len(self.items) == 0:
                    function_data = self.get_function_data()
                    function_data["last_key"] = key
                    return [], "", function_data
                selected_indices = get_selected_indices(self.selections)
                if not selected_indices and len(self.indexed_items):
                    selected_indices = [self.indexed_items[self.cursor_pos][0]]
                
                options_sufficient = True
                usrtxt = self.user_opts
                for index in selected_indices:
                    if self.require_option[index]:
                        if self.option_functions[index] != None:
                            options_sufficient, usrtxt = self.option_functions[index](
                                stdscr=self.stdscr,
                                refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights)
                            )
                        else:
                            self.set_registers()
                            options_sufficient, usrtxt = default_option_input(
                                self.stdscr,
                                starting_value=self.user_opts,
                                registers = self.registers
                            )

                if options_sufficient:
                    self.user_opts = usrtxt
                    self.stdscr.clear()
                    self.stdscr.refresh()
                    function_data = self.get_function_data()
                    function_data["last_key"] = key
                    return selected_indices, usrtxt, function_data
            elif self.check_key("page_down", key, self.keys_dict):  # Next page
                self.cursor_pos = min(len(self.indexed_items) - 1, self.cursor_pos+self.items_per_page)

            elif self.check_key("page_up", key, self.keys_dict):
                self.cursor_pos = max(0, self.cursor_pos-self.items_per_page)

            elif self.check_key("redraw_screen", key, self.keys_dict):
                self.logger.info(f"key_function redraw_screen")
                self.stdscr.clear()
                self.stdscr.refresh()
                restrict_curses(self.stdscr)
                unrestrict_curses(self.stdscr)
                self.stdscr.clear()
                self.stdscr.refresh()

                self.draw_screen(self.indexed_items, self.highlights)

            elif self.check_key("cycle_sort_method", key, self.keys_dict):
                if self.sort_column == self.selected_column:
                    self.columns_sort_method[self.sort_column] = (self.columns_sort_method[self.sort_column]+1) % len(self.SORT_METHODS)
                else:
                    self.sort_column = self.selected_column
                if len(self.indexed_items) > 0:
                    current_index = self.indexed_items[self.cursor_pos][0]
                    sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
                    self.cursor_pos = [row[0] for row in self.indexed_items].index(current_index)

                self.logger.info(f"key_function cycle_sort_method. (sort_column, sort_method) = ({self.sort_column}, {self.columns_sort_method[self.sort_column]})")
            elif self.check_key("cycle_sort_method_reverse", key, self.keys_dict):  # Cycle sort method
                old_sort_column = self.sort_column
                self.sort_column = self.selected_column
                self.columns_sort_method[self.sort_column] = (self.columns_sort_method[self.sort_column]-1) % len(self.SORT_METHODS)
                if len(self.indexed_items) > 0:
                    current_index = self.indexed_items[self.cursor_pos][0]
                    sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
                    self.cursor_pos = [row[0] for row in self.indexed_items].index(current_index)
                self.logger.info(f"key_function cycle_sort_method. (sort_column, sort_method) = ({self.sort_column}, {self.columns_sort_method[self.sort_column]})")

            elif self.check_key("cycle_sort_order", key, self.keys_dict):  # Toggle sort order
                self.sort_reverse[self.sort_column] = not self.sort_reverse[self.sort_column]
                if len(self.indexed_items) > 0:
                    current_index = self.indexed_items[self.cursor_pos][0]
                    sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
                    self.draw_screen(self.indexed_items, self.highlights)
                    self.cursor_pos = [row[0] for row in self.indexed_items].index(current_index)
                self.logger.info(f"key_function cycle_sort_order. (sort_column, sort_method, sort_reverse) = ({self.sort_column}, {self.columns_sort_method[self.sort_column]}, {self.sort_reverse[self.sort_column]})")
            elif self.check_key("col_select", key, self.keys_dict):
                col_index = key - ord('0')
                self.logger.info(f"key_function col_select {col_index}")
                if 0 <= col_index < len(self.items[0]):
                    self.sort_column = col_index
                    if len(self.indexed_items) > 0:
                        current_index = self.indexed_items[self.cursor_pos][0]
                        sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
                        self.cursor_pos = [row[0] for row in self.indexed_items].index(current_index)
            elif self.check_key("col_select_next", key, self.keys_dict):
                if len(self.items) > 0 and len(self.items[0]) > 0:
                    col_index = (self.selected_column +1) % (len(self.items[0]))
                    self.selected_column = col_index
                # Flash when we loop back to the first column
                # if self.selected_column == 0:
                #     curses.flash()
                self.logger.info(f"key_function col_select_next {self.selected_column}")


                ## Scroll with column select
                rows = self.get_visible_rows()
                self.column_widths = get_column_widths(rows, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=self.rows_w, unicode_char_width=self.unicode_char_width)
                visible_column_widths = [c for i,c in enumerate(self.column_widths) if i not in self.hidden_columns]
                column_set_width = sum(visible_column_widths)+len(self.separator)*len(visible_column_widths)
                start_of_cell = sum(visible_column_widths[:self.selected_column])+len(self.separator)*self.selected_column
                end_of_cell = sum(visible_column_widths[:self.selected_column+1])+len(self.separator)*(self.selected_column+1)
                display_width = self.rows_w-self.startx
                # If the full column is within the current display then don't do anything
                if start_of_cell >= self.leftmost_char and end_of_cell <= self.leftmost_char + display_width:
                    pass
                # Otherwise right-justify the cell
                else:
                    self.leftmost_char = end_of_cell - display_width

                self.leftmost_char = max(0, min(column_set_width - display_width + 5, self.leftmost_char))

            elif self.check_key("col_select_prev", key, self.keys_dict):
                if len(self.items) > 0 and len(self.items[0]) > 0:
                    col_index = (self.selected_column -1) % (len(self.items[0]))
                    self.selected_column = col_index

                self.logger.info(f"key_function col_select_prev {self.selected_column}")
                # Flash when we loop back to the last column
                # if self.selected_column == len(self.column_widths)-1:
                #     curses.flash()

                ## Scroll with column select
                rows = self.get_visible_rows()
                self.column_widths = get_column_widths(rows, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=self.rows_w, unicode_char_width=self.unicode_char_width)
                visible_column_widths = [c for i,c in enumerate(self.column_widths) if i not in self.hidden_columns]
                column_set_width = sum(visible_column_widths)+len(self.separator)*len(visible_column_widths)
                start_of_cell = sum(visible_column_widths[:self.selected_column])+len(self.separator)*self.selected_column
                end_of_cell = sum(visible_column_widths[:self.selected_column+1])+len(self.separator)*(self.selected_column+1)
                display_width = self.rows_w-self.startx

                # If the entire column is within the current display then don't do anything
                if start_of_cell >= self.leftmost_char and end_of_cell <= self.leftmost_char + display_width:
                    pass
                # Otherwise left-justify the cell
                else:
                    self.leftmost_char = start_of_cell

                self.leftmost_char = max(0, min(column_set_width - display_width + 5, self.leftmost_char))

            elif self.check_key("scroll_right", key, self.keys_dict):
                self.logger.info(f"key_function scroll_right")
                if len(self.indexed_items):
                    row_width = sum(self.column_widths) + len(self.separator)*(len(self.column_widths)-1)
                    if row_width-self.leftmost_char >= self.rows_w-self.startx:
                        self.leftmost_char = self.leftmost_char+5

            elif self.check_key("scroll_left", key, self.keys_dict):
                self.logger.info(f"key_function scroll_left")
                self.leftmost_char = max(self.leftmost_char-5, 0)

            elif self.check_key("scroll_far_left", key, self.keys_dict):
                self.logger.info(f"key_function scroll_far_left")
                self.leftmost_char = 0
                self.selected_column = 0
            
            elif self.check_key("scroll_far_right", key, self.keys_dict):
                self.logger.info(f"key_function scroll_far_right")
                longest_row_str_len = 0
                rows = self.get_visible_rows()
                for i in range(len(rows)):
                    item = rows[i]
                    row_str = format_row(item, self.hidden_columns, self.column_widths, self.separator, self.centre_in_cols, self.unicode_char_width)
                    if len(row_str) > longest_row_str_len: longest_row_str_len=len(row_str)
                # for i in range(len(self.indexed_items)):
                #     item = self.indexed_items[i]
                #     row_str = format_row(item[1], self.hidden_columns, self.column_widths, self.separator, self.centre_in_cols)
                #     if len(row_str) > longest_row_str_len: longest_row_str_len=len(row_str)
                # self.notification(self.stdscr, f"{longest_row_str_len}")
                self.leftmost_char = max(0, longest_row_str_len-self.rows_w+2+self.startx)
                if len(self.items):
                    self.selected_column = len(self.items[0])-1

            elif self.check_key("add_column_before", key, self.keys_dict):
                self.logger.info(f"key_function add_column_before")
                # self.add_column_before()
                self.insert_column(self.selected_column)

            elif self.check_key("add_column_after", key, self.keys_dict):
                self.logger.info(f"key_function add_column_after")
                # self.add_column_after()
                self.insert_column(self.selected_column+1)

            elif self.check_key("add_row_before", key, self.keys_dict):
                self.logger.info(f"key_function add_row_before")
                # self.add_row_before()
                self.insert_row(self.cursor_pos)

            elif self.check_key("add_row_after", key, self.keys_dict):
                self.logger.info(f"key_function add_row_after")
                # self.add_row_after()
                self.insert_row(self.cursor_pos+1)

            elif self.check_key("col_hide", key, self.keys_dict):
                self.logger.info(f"key_function col_hide")
                d = {'!': 0, '@': 1, '#': 2, '$': 3, '%': 4, '^': 5, '&': 6, '*': 7, '(': 8, ')': 9}
                d = {s:i for i,s in enumerate(")!@#$%^&*(")}
                col_index = d[chr(key)]
                self.toggle_column_visibility(col_index)
            elif self.check_key("copy", key, self.keys_dict):
                self.copy_dialogue()
            elif self.check_key("paste", key, self.keys_dict):
                self.paste_dialogue()
            elif self.check_key("save", key, self.keys_dict):
                self.save_dialog()
            elif self.check_key("load", key, self.keys_dict):
                self.load_dialog()

            elif self.check_key("delete", key, self.keys_dict):  # Delete key
                self.delete_entries()

            elif self.check_key("delete_column", key, self.keys_dict):  # Delete key
                self.logger.info(f"key_function delete_column")
                row_len = 1
                if self.header: row_len = len(self.header)
                elif len(self.items): row_len  = len(self.items[0])
                if row_len > 1:
                    self.items = [row[:self.selected_column] + row[self.selected_column+1:] for row in self.items]
                    self.header = self.header[:self.selected_column] + self.header[self.selected_column+1:]
                    self.editable_columns = self.editable_columns[:self.selected_column] + self.editable_columns[self.selected_column+1:]
                    self.selected_column = min(self.selected_column, row_len-2)
                elif row_len == 1:
                    self.items = [[""] for _ in range(len(self.items))]
                    self.header = [""] if self.header else []
                    self.editable_columns = []
                    self.selected_column = min(self.selected_column, row_len-2)
                self.initialise_variables()




            # elif self.check_key("increase_lines_per_page", key, self.keys_dict):
            #     self.items_per_page += 1
            #     self.draw_screen(self.indexed_items, self.highlights)
            # elif self.check_key("decrease_lines_per_page", key, self.keys_dict):
            #     if self.items_per_page > 1:
            #         self.items_per_page -= 1
            #     self.draw_screen(self.indexed_items, self.highlights)
            elif self.check_key("decrease_column_width", key, self.keys_dict):
                self.logger.info(f"key_function decrease_column_width")
                if self.max_column_width > 10:
                    self.max_column_width -= 10
                    # self.column_widths = get_column_widths(self.items, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=2)
                    self.draw_screen(self.indexed_items, self.highlights)
            elif self.check_key("increase_column_width", key, self.keys_dict):
                self.logger.info(f"key_function increase_column_width")
                if self.max_column_width < 1000:
                    self.max_column_width += 10
                    # self.column_widths = get_column_widths(self.items, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=w)
                    self.draw_screen(self.indexed_items, self.highlights)
            elif self.check_key("visual_selection_toggle", key, self.keys_dict):
                self.logger.info(f"key_function visual_selection_toggle")
                self.handle_visual_selection()
                self.draw_screen(self.indexed_items, self.highlights)

            elif self.check_key("visual_deselection_toggle", key, self.keys_dict):
                self.logger.info(f"key_function visual_deselection_toggle")
                self.handle_visual_selection(selecting=False)
                self.draw_screen(self.indexed_items, self.highlights)

            elif key == curses.KEY_RESIZE:  # Terminal resize signal

                self.calculate_section_sizes()
                self.column_widths = get_column_widths(self.items, header=self.header, max_column_width=self.max_column_width, number_columns=self.number_columns, max_total_width=self.rows_w, unicode_char_width=self.unicode_char_width)

                self.draw_screen(self.indexed_items, self.highlights)


            elif self.check_key("filter_input", key, self.keys_dict):
                self.logger.info(f"key_function filter_input")
                self.draw_screen(self.indexed_items, self.highlights)
                usrtxt = f"{self.filter_query} " if self.filter_query else ""
                field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                if self.show_footer and self.footer.height >= 2: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                self.set_registers()
                words = self.get_word_list()
                usrtxt, return_val = input_field(
                    self.stdscr,
                    usrtxt=usrtxt,
                    field_prefix=" Filter: ",
                    x=lambda:2,
                    y=lambda: self.stdscr.getmaxyx()[0]-2,
                    # max_length=field_end,
                    max_length=field_end_f,
                    registers=self.registers,
                    refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                    history=self.history_filter_and_search,
                    path_auto_complete=True,
                    formula_auto_complete=False,
                    function_auto_complete=False,
                    word_auto_complete=True,
                    auto_complete_words=words,
                )
                if return_val:
                    self.filter_query = usrtxt
                    self.history_filter_and_search.append(usrtxt)

                    # If the current mode filter has been changed then go back to the first mode
                    if self.modes and "filter" in self.modes[self.mode_index] and self.modes[self.mode_index]["filter"] not in self.filter_query:
                        self.mode_index = 0
                    # elif "filter" in modes[mode_index] and modes[mode_index]["filter"] in filter_query:
                    #     filter_query.split(modes[mode_index]["filter"])

                    prev_index = self.indexed_items[self.cursor_pos][0] if len(self.indexed_items)>0 else 0
                    self.indexed_items = filter_items(self.items, self.indexed_items, self.filter_query)
                    if prev_index in [x[0] for x in self.indexed_items]: new_index = [x[0] for x in self.indexed_items].index(prev_index)
                    else: new_index = 0
                    self.cursor_pos = new_index
                    # Re-sort self.items after applying filter
                    if self.columns_sort_method[self.selected_column] != 0:
                        sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column

            elif self.check_key("search_input", key, self.keys_dict):
                self.logger.info(f"key_function search_input")
                self.draw_screen(self.indexed_items, self.highlights)
                usrtxt = f"{self.search_query} " if self.search_query else ""
                field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                if self.show_footer and self.footer.height >= 3: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                self.set_registers()
                words = self.get_word_list()
                usrtxt, return_val = input_field(
                    self.stdscr,
                    usrtxt=usrtxt,
                    field_prefix=" Search: ",
                    x=lambda:2,
                    y=lambda: self.stdscr.getmaxyx()[0]-3,
                    max_length=field_end_f,
                    registers=self.registers,
                    refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                    history=self.history_filter_and_search,
                    path_auto_complete=True,
                    formula_auto_complete=False,
                    function_auto_complete=False,
                    word_auto_complete=True,
                    auto_complete_words=words,
                )
                if return_val:
                    self.search_query = usrtxt
                    self.history_filter_and_search.append(usrtxt)
                    return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                        query=self.search_query,
                        indexed_items=self.indexed_items,
                        highlights=self.highlights,
                        cursor_pos=self.cursor_pos,
                        unselectable_indices=self.unselectable_indices,
                    )
                    if return_val:
                        self.cursor_pos, self.search_index, self.search_count, self.highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights
                    else:
                        self.search_index, self.search_count = 0, 0

            elif self.check_key("continue_search_forward", key, self.keys_dict):
                self.logger.info(f"key_function continue_search_forward")
                return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                    query=self.search_query,
                    indexed_items=self.indexed_items,
                    highlights=self.highlights,
                    cursor_pos=self.cursor_pos,
                    unselectable_indices=self.unselectable_indices,
                    continue_search=True,
                )
                if return_val:
                    self.cursor_pos, self.search_index, self.search_count, self.highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights
            elif self.check_key("continue_search_backward", key, self.keys_dict):
                self.logger.info(f"key_function continue_search_backward")
                return_val, tmp_cursor, tmp_index, tmp_count, tmp_highlights = search(
                    query=self.search_query,
                    indexed_items=self.indexed_items,
                    highlights=self.highlights,
                    cursor_pos=self.cursor_pos,
                    unselectable_indices=self.unselectable_indices,
                    continue_search=True,
                    reverse=True,
                )
                if return_val:
                    self.cursor_pos, self.search_index, self.search_count, self.highlights = tmp_cursor, tmp_index, tmp_count, tmp_highlights
            elif self.check_key("cancel", key, self.keys_dict):  # ESC key
                # order of escapes:
                # 1. selecting/deslecting
                # 2. search
                # 3. filter
                # 4. if self.cancel_is_back (e.g., notification) then we exit
                # 4. selecting

                pass
                # Cancel visual de/selection
                if self.is_selecting or self.is_deselecting:
                    self.start_selection = -1
                    self.end_selection = -1
                    self.is_selecting = False
                    self.is_deselecting = False
                # Cancel search
                elif self.search_query:
                    self.search_query = ""
                    self.highlights = [highlight for highlight in self.highlights if "type" not in highlight or highlight["type"] != "search" ]
                # Remove filter
                elif self.filter_query:
                    if self.modes and "filter" in self.modes[self.mode_index] and self.modes[self.mode_index]["filter"] in self.filter_query and self.filter_query.strip() != self.modes[self.mode_index]["filter"]:
                        self.filter_query = self.modes[self.mode_index]["filter"]
                    # elif "filter" in modes[mode_index]:
                    else:
                        self.filter_query = ""
                        self.mode_index = 0
                    prev_index = self.indexed_items[self.cursor_pos][0] if len(self.indexed_items)>0 else 0
                    self.indexed_items = filter_items(self.items, self.indexed_items, self.filter_query)
                    if prev_index in [x[0] for x in self.indexed_items]: new_index = [x[0] for x in self.indexed_items].index(prev_index)
                    else: new_index = 0
                    self.cursor_pos = new_index
                    # Re-sort self.items after applying filter
                    if self.columns_sort_method[self.selected_column] != 0:
                        sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
                elif self.cancel_is_back:
                    function_data = self.get_function_data()
                    function_data["last_key"] = key
                    return [], "escape", function_data


                # else:
                #     self.search_query = ""
                #     self.mode_index = 0
                #     self.highlights = [highlight for highlight in self.highlights if "type" not in highlight or highlight["type"] != "search" ]
                #     continue
                self.draw_screen(self.indexed_items, self.highlights)

            elif self.check_key("opts_input", key, self.keys_dict):
                self.logger.info(f"key_function opts_input")
                usrtxt = f"{self.user_opts} " if self.user_opts else ""
                field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                if self.show_footer and self.footer.height >= 1: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                self.set_registers()
                words = self.get_word_list()
                usrtxt, return_val = input_field(
                    self.stdscr,
                    usrtxt=usrtxt,
                    field_prefix=" Opts: ",
                    x=lambda:2,
                    y=lambda: self.stdscr.getmaxyx()[0]-1,
                    max_length=field_end_f,
                    registers=self.registers,
                    refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                    history=self.history_opts,
                    path_auto_complete=True,
                    formula_auto_complete=False,
                    function_auto_complete=True,
                    word_auto_complete=True,
                    auto_complete_words=words,
                )
                if return_val:
                    self.user_opts = usrtxt
                    self.history_opts.append(usrtxt)
            elif self.check_key("opts_select", key, self.keys_dict):
                self.logger.info(f"key_function opts_select")
                s, o, f = self.choose_option(self.stdscr, self.options_list)
                if self.user_opts.strip(): self.user_opts += " "
                self.user_opts += " ".join([x[0] for x in s.values()])
            elif self.check_key("notification_toggle", key, self.keys_dict):
                self.logger.info(f"key_function notification_toggle")
                self.notification(self.stdscr, colours_end=self.colours_end)

            elif self.check_key("mode_next", key, self.keys_dict): # tab key
                self.logger.info(f"key_function mode_next")
                if len(self.modes):
                    prev_mode_index = self.mode_index
                    self.mode_index = (self.mode_index+1)%len(self.modes)
                    mode = self.modes[self.mode_index]
                    for key, val in mode.items():
                        if key == 'filter':
                            if 'filter' in self.modes[prev_mode_index]:
                                self.filter_query = self.filter_query.replace(self.modes[prev_mode_index]['filter'], '')
                            self.filter_query = f"{self.filter_query.strip()} {val.strip()}".strip()

                            if len(self.indexed_items) == 0:
                                prev_index = -1
                            else:
                                prev_index = self.indexed_items[self.cursor_pos][0] if len(self.indexed_items)>0 else 0

                            self.indexed_items = filter_items(self.items, self.indexed_items, self.filter_query)
                            if prev_index >= 0 and prev_index in [x[0] for x in self.indexed_items]:
                                new_index = [x[0] for x in self.indexed_items].index(prev_index)
                            else:
                                new_index = 0
                            self.cursor_pos = new_index
                            # Re-sort self.items after applying filter
                            if len(self.items) and self.items != [[]]:
                                sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
            elif self.check_key("mode_prev", key, self.keys_dict): # shift+tab key
                self.logger.info(f"key_function mode_prev")
                if len(self.modes):
                    prev_mode_index = self.mode_index
                    self.mode_index = (self.mode_index-1)%len(self.modes)
                    mode = self.modes[self.mode_index]
                    for key, val in mode.items():
                        if key == 'filter':
                            if 'filter' in self.modes[prev_mode_index]:
                                self.filter_query = self.filter_query.replace(self.modes[prev_mode_index]['filter'], '')
                            self.filter_query = f"{self.filter_query.strip()} {val.strip()}".strip()
                            prev_index = self.indexed_items[self.cursor_pos][0] if len(self.indexed_items)>0 else 0

                            # if len(self.items) and self.items != [[]]:
                            self.indexed_items = filter_items(self.items, self.indexed_items, self.filter_query)
                            if prev_index in [x[0] for x in self.indexed_items]: new_index = [x[0] for x in self.indexed_items].index(prev_index)
                            else: new_index = 0
                            self.cursor_pos = new_index
                            # Re-sort self.items after applying filter
                            sort_items(self.indexed_items, sort_method=self.columns_sort_method[self.sort_column], sort_column=self.sort_column, sort_reverse=self.sort_reverse[self.sort_column])  # Re-sort self.items based on new column
            elif self.check_key("file_next", key, self.keys_dict):
                self.switch_file(increment=1)

            elif self.check_key("file_prev", key, self.keys_dict):
                self.switch_file(increment=-1)

            elif self.check_key("toggle_right_pane", key, self.keys_dict):
                self.toggle_right_pane()

            elif self.check_key("pipe_input", key, self.keys_dict):
                self.logger.info(f"key_function pipe_input")
                # usrtxt = "xargs -d '\n' -I{}  "
                usrtxt = "xargs "
                field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                if self.show_footer and self.footer.height >= 2: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                self.set_registers()
                
                # Get list of available shell commands
                try:
                    # result = subprocess.run(['compgen', '-c'], capture_output=True, text=True, check=True)
                    # shell_commands = result.stdout.splitlines()
                    result = subprocess.run(['ls', '/usr/bin'], capture_output=True, text=True, check=True)
                    shell_commands = result.stdout.splitlines()
                except:
                    shell_commands = []
                usrtxt, return_val = input_field(
                    self.stdscr,
                    usrtxt=usrtxt,
                    field_prefix=" Command: ",
                    x=lambda:2,
                    y=lambda: self.stdscr.getmaxyx()[0]-2,
                    literal=True,
                    max_length=field_end_f,
                    registers=self.registers,
                    refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                    history=self.history_pipes,
                    path_auto_complete=True,
                    formula_auto_complete=False,
                    function_auto_complete=False,
                    word_auto_complete=True,
                    auto_complete_words=shell_commands,
                )

                if return_val:
                    selected_indices = get_selected_indices(self.selections)
                    self.history_pipes.append(usrtxt)

                    if not selected_indices:
                        if len(self.indexed_items):
                            pos = self.indexed_items[self.cursor_pos][0]
                            if " " in self.items[pos][self.selected_column]:
                                full_values = [repr(self.items[pos][self.selected_column])]
                            else:
                                full_values = [self.items[pos][self.selected_column]]

                        else:
                            return None
                    elif self.cell_cursor:
                        
                        full_values = []
                        for row in self.selected_cells_by_row.keys():
                            selected_cell_row_str = ""
                            for cell in self.selected_cells_by_row[row]:
                                if " " in self.items[row][cell]:
                                    selected_cell_row_str += repr(self.items[row][cell])
                                else:
                                    selected_cell_row_str += self.items[row][cell]
                                selected_cell_row_str += "\t"
                            full_values.append(selected_cell_row_str.strip())

                    else:
                        full_values = []
                        for i in selected_indices:
                            selected_cell_row_str = ""
                            if " " in self.items[i][self.selected_column]:
                                selected_cell_row_str += repr(self.items[i][self.selected_column])
                            else:
                                selected_cell_row_str += str(self.items[i][self.selected_column])
                            full_values.append(selected_cell_row_str)

                    if full_values:
                        # command = usrtxt.split()
                        command = usrtxt
                        # command = ['xargs', '-d' , '"\n"' '-I', '{}', 'mpv', '{}']
                        # command = ['xargs', '-d' , '"\n"' '-I', '{}', 'mpv', '{}']
                        # command = "xargs -d '\n' -I{} mpv {}"

                        try:
                            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

                            if process.stdin != None:
                                for value in full_values:
                                    process.stdin.write((value + '\n').encode())
                                    # process.stdin.write((value + '\n').encode())

                                process.stdin.close()

                                self.notification(self.stdscr, message=f"{len(full_values)} strings piped to {repr(usrtxt)}")
                        except Exception as e:
                            self.notification(self.stdscr, message=f"{e}")
                            # self.notification(self.stdscr, message=f"Error: {str(e)}")


            elif self.check_key("open", key, self.keys_dict):
                self.logger.info(f"key_function open")
                selected_indices = get_selected_indices(self.selections)
                if not selected_indices:
                    selected_indices = [self.indexed_items[self.cursor_pos][0]]

                file_names = [self.items[i][self.selected_column] for i in selected_indices]
                response = openFiles(file_names)
                if response:
                    self.notification(self.stdscr, message=response)


            elif self.check_key("reset_opts", key, self.keys_dict):
                self.logger.info(f"key_function reset_opts")
                self.user_opts = ""

            elif self.check_key("edit", key, self.keys_dict):
                self.logger.info(f"key_function edit")
                if len(self.indexed_items) > 0 and self.selected_column >=0 and self.editable_columns[self.selected_column]:
                    current_val = self.indexed_items[self.cursor_pos][1][self.selected_column]
                    usrtxt = f"{current_val}"
                    field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                    if self.show_footer and self.footer.height >= 2: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                    else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                    self.set_registers()
                    words = self.get_word_list()
                    usrtxt, return_val = input_field(
                        self.stdscr,
                        usrtxt=usrtxt,
                        field_prefix=" Edit value: ",
                        x=lambda:2,
                        y=lambda: self.stdscr.getmaxyx()[0]-2,
                        max_length=field_end_f,
                        registers=self.registers,
                        refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                        history = self.history_edits,
                        path_auto_complete=True,
                        formula_auto_complete=True,
                        function_auto_complete=True,
                        word_auto_complete=True,
                        auto_complete_words=words,
                    )
                    if return_val:
                        if usrtxt.startswith("```"):
                            usrtxt = str(eval(usrtxt[3:]))
                        self.indexed_items[self.cursor_pos][1][self.selected_column] = usrtxt
                        self.history_edits.append(usrtxt)

            elif self.check_key("edit_picker", key, self.keys_dict):
                self.logger.info(f"key_function edit_picker")
                if len(self.indexed_items) > 0 and self.selected_column >=0 and self.editable_columns[self.selected_column]:
                    current_val = self.indexed_items[self.cursor_pos][1][self.selected_column]
                    usrtxt = f"{current_val}"
                    field_end_f = lambda: self.stdscr.getmaxyx()[1]-38 if self.show_footer else lambda: self.stdscr.getmaxyx()[1]-3
                    if self.show_footer and self.footer.height >= 2: field_end_f = lambda: self.stdscr.getmaxyx()[1]-38
                    else: field_end_f = lambda: self.stdscr.getmaxyx()[1]-3
                    self.set_registers()
                    words = self.get_word_list()
                    usrtxt, return_val = input_field(
                        self.stdscr,
                        usrtxt=usrtxt,
                        field_prefix=" Edit value: ",
                        x=lambda:2,
                        y=lambda: self.stdscr.getmaxyx()[0]-2,
                        max_length=field_end_f,
                        registers=self.registers,
                        refresh_screen_function=lambda: self.draw_screen(self.indexed_items, self.highlights),
                        history = self.history_edits,
                        path_auto_complete=True,
                        formula_auto_complete=True,
                        function_auto_complete=True,
                        word_auto_complete=True,
                        auto_complete_words=words,
                    )
                    if return_val:
                        self.indexed_items[self.cursor_pos][1][self.selected_column] = usrtxt
                        self.history_edits.append(usrtxt)
            elif self.check_key("edit_ipython", key, self.keys_dict):
                self.logger.info(f"key_function edit_picker")
                import IPython, termios
                self.stdscr.clear()
                restrict_curses(self.stdscr)
                self.stdscr.clear()
                os.system('cls' if os.name == 'nt' else 'clear')
                globals()['self'] = self  # make the instance available in IPython namespace

                from traitlets.config import Config
                c = Config()
                # Doesn't work; Config only works with start_ipython, not embed... but start_ipython causes errors
                # c.InteractiveShellApp.exec_lines = [
                #     '%clear'
                # ]
                msg = "The active Picker object has variable name self.\n"
                msg += "\te.g., self.items will display the items in Picker"
                tty_in = open("/dev/tty", "r")
                tty_out = open("/dev/tty", "w")

                fd = tty_in.fileno()
                old_attrs = termios.tcgetattr(fd)
                new_attrs = termios.tcgetattr(fd)
                new_attrs[3] |= termios.ECHO  # lflags
                termios.tcsetattr(fd, termios.TCSADRAIN, new_attrs)

                sys.stdin = tty_in
                sys.stdout = tty_out
                sys.stderr = tty_out
                IPython.embed(header=msg, config=c)

                unrestrict_curses(self.stdscr)

                tty_in.close()
                tty_out.close()
                self.stdscr.clear()
                self.stdscr.refresh()
                self.initialise_variables()
                self.draw_screen(self.indexed_items, self.highlights)



            self.draw_screen(self.indexed_items, self.highlights, clear=clear_screen)



def set_colours(pick: int = 0, start: int = 0) -> Optional[int]:
    """ Initialise curses colour pairs from dictionary. """
    
    global COLOURS_SET, notification_colours, help_colours
    if COLOURS_SET: return None
    if start == None: start = 0
    

    if curses.COLORS >= 255:
        colours = get_colours(pick)
        notification_colours = get_notification_colours(pick)
        help_colours = get_help_colours(pick)
        standard_colours_start, notification_colours_start, help_colours_start = 0, 50, 100
    else:
        colours = get_fallback_colours()
        notification_colours = get_fallback_colours()
        help_colours = get_fallback_colours()
        standard_colours_start, help_colours_start, notification_colours_start = 0, 0, 0

    if not colours: return 0

    try:
        start = standard_colours_start
        curses.init_pair(start+1, colours['selected_fg'], colours['selected_bg'])
        curses.init_pair(start+2, colours['unselected_fg'], colours['unselected_bg'])
        curses.init_pair(start+3, colours['normal_fg'], colours['background'])
        curses.init_pair(start+4, colours['header_fg'], colours['header_bg'])
        curses.init_pair(start+5, colours['cursor_fg'], colours['cursor_bg'])
        curses.init_pair(start+6, colours['normal_fg'], colours['background'])
        curses.init_pair(start+7, colours['error_fg'], colours['error_bg'])
        curses.init_pair(start+8, colours['complete_fg'], colours['complete_bg'])
        curses.init_pair(start+9, colours['active_fg'], colours['active_bg'])
        curses.init_pair(start+10, colours['search_fg'], colours['search_bg'])
        curses.init_pair(start+11, colours['waiting_fg'], colours['waiting_bg'])
        curses.init_pair(start+12, colours['paused_fg'], colours['paused_bg'])
        curses.init_pair(start+13, colours['active_input_fg'], colours['active_input_bg'])
        curses.init_pair(start+14, colours['modes_selected_fg'], colours['modes_selected_bg'])
        curses.init_pair(start+15, colours['modes_unselected_fg'], colours['modes_unselected_bg'])
        curses.init_pair(start+16, colours['title_fg'], colours['title_bg'])
        curses.init_pair(start+17, colours['normal_fg'], colours['title_bar'])
        curses.init_pair(start+18, colours['normal_fg'], colours['scroll_bar_bg'])
        curses.init_pair(start+19, colours['selected_header_column_fg'], colours['selected_header_column_bg'])
        curses.init_pair(start+20, colours['footer_fg'], colours['footer_bg'])
        curses.init_pair(start+21, colours['refreshing_fg'], colours['refreshing_bg'])
        curses.init_pair(start+22, colours['40pc_fg'], colours['40pc_bg'])
        curses.init_pair(start+23, colours['refreshing_inactive_fg'], colours['refreshing_inactive_bg'])
        curses.init_pair(start+24, colours['footer_string_fg'], colours['footer_string_bg'])
        curses.init_pair(start+25, colours['selected_cell_fg'], colours['selected_cell_bg'])
        curses.init_pair(start+26, colours['deselecting_cell_fg'], colours['deselecting_cell_bg'])


        # notifications 50, infobox 100, help 150
        # Notification colours
        colours = notification_colours
        start = notification_colours_start
        curses.init_pair(start+1, colours['selected_fg'], colours['selected_bg'])
        curses.init_pair(start+2, colours['unselected_fg'], colours['unselected_bg'])
        curses.init_pair(start+3, colours['normal_fg'], colours['background'])
        curses.init_pair(start+4, colours['header_fg'], colours['header_bg'])
        curses.init_pair(start+5, colours['cursor_fg'], colours['cursor_bg'])
        curses.init_pair(start+6, colours['normal_fg'], colours['background'])
        curses.init_pair(start+7, colours['error_fg'], colours['error_bg'])
        curses.init_pair(start+8, colours['complete_fg'], colours['complete_bg'])
        curses.init_pair(start+9, colours['active_fg'], colours['active_bg'])
        curses.init_pair(start+10, colours['search_fg'], colours['search_bg'])
        curses.init_pair(start+11, colours['waiting_fg'], colours['waiting_bg'])
        curses.init_pair(start+12, colours['paused_fg'], colours['paused_bg'])
        curses.init_pair(start+13, colours['active_input_fg'], colours['active_input_bg'])
        curses.init_pair(start+14, colours['modes_selected_fg'], colours['modes_selected_bg'])
        curses.init_pair(start+15, colours['modes_unselected_fg'], colours['modes_unselected_bg'])
        curses.init_pair(start+16, colours['title_fg'], colours['title_bg'])
        curses.init_pair(start+17, colours['normal_fg'], colours['title_bar'])
        curses.init_pair(start+18, colours['normal_fg'], colours['scroll_bar_bg'])
        curses.init_pair(start+19, colours['selected_header_column_fg'], colours['selected_header_column_bg'])
        curses.init_pair(start+20, colours['footer_fg'], colours['footer_bg'])
        curses.init_pair(start+21, colours['refreshing_fg'], colours['refreshing_bg'])
        curses.init_pair(start+22, colours['40pc_fg'], colours['40pc_bg'])
        curses.init_pair(start+23, colours['refreshing_inactive_fg'], colours['refreshing_inactive_bg'])
        curses.init_pair(start+24, colours['footer_string_fg'], colours['footer_string_bg'])
        curses.init_pair(start+25, colours['selected_cell_fg'], colours['selected_cell_bg'])
        curses.init_pair(start+26, colours['deselecting_cell_fg'], colours['deselecting_cell_bg'])

        # Help
        colours = help_colours
        start = help_colours_start
        curses.init_pair(start+1, colours['selected_fg'], colours['selected_bg'])
        curses.init_pair(start+2, colours['unselected_fg'], colours['unselected_bg'])
        curses.init_pair(start+3, colours['normal_fg'], colours['background'])
        curses.init_pair(start+4, colours['header_fg'], colours['header_bg'])
        curses.init_pair(start+5, colours['cursor_fg'], colours['cursor_bg'])
        curses.init_pair(start+6, colours['normal_fg'], colours['background'])
        curses.init_pair(start+7, colours['error_fg'], colours['error_bg'])
        curses.init_pair(start+8, colours['complete_fg'], colours['complete_bg'])
        curses.init_pair(start+9, colours['active_fg'], colours['active_bg'])
        curses.init_pair(start+10, colours['search_fg'], colours['search_bg'])
        curses.init_pair(start+11, colours['waiting_fg'], colours['waiting_bg'])
        curses.init_pair(start+12, colours['paused_fg'], colours['paused_bg'])
        curses.init_pair(start+13, colours['active_input_fg'], colours['active_input_bg'])
        curses.init_pair(start+14, colours['modes_selected_fg'], colours['modes_selected_bg'])
        curses.init_pair(start+15, colours['modes_unselected_fg'], colours['modes_unselected_bg'])
        curses.init_pair(start+16, colours['title_fg'], colours['title_bg'])
        curses.init_pair(start+17, colours['normal_fg'], colours['title_bar'])
        curses.init_pair(start+18, colours['normal_fg'], colours['scroll_bar_bg'])
        curses.init_pair(start+19, colours['selected_header_column_fg'], colours['selected_header_column_bg'])
        curses.init_pair(start+20, colours['footer_fg'], colours['footer_bg'])
        curses.init_pair(start+21, colours['refreshing_fg'], colours['refreshing_bg'])
        curses.init_pair(start+22, colours['40pc_fg'], colours['40pc_bg'])
        curses.init_pair(start+23, colours['refreshing_inactive_fg'], colours['refreshing_inactive_bg'])
        curses.init_pair(start+24, colours['footer_string_fg'], colours['footer_string_bg'])
        curses.init_pair(start+25, colours['selected_cell_fg'], colours['selected_cell_bg'])
        curses.init_pair(start+26, colours['deselecting_cell_fg'], colours['deselecting_cell_bg'])
    except Exception as e:
        pass
    COLOURS_SET = True
    return start+21

def parse_arguments() -> Tuple[argparse.Namespace, dict]:
    """ Parse command line arguments. """
    parser = argparse.ArgumentParser(description='Convert table to list of lists.')
    # parser.add_argument('filename', type=str, help='The file to process')
    # parser.add_argument('-i', dest='file', help='File containing the table to be converted.')
    parser.add_argument('-i', dest='file', nargs='+', help='File containing the table to be converted.')
    parser.add_argument('--load', '-l', dest='load', type=str, help='Load file from Picker dump.')
    parser.add_argument('--stdin', dest='stdin', action='store_true', help='Table passed on stdin')
    parser.add_argument('--stdin2', action='store_true', help='Table passed on stdin')
    parser.add_argument('--generate', '-g', type=str, help='Pass file to generate data for listpick Picker.')
    parser.add_argument('--delimiter', '-d', dest='delimiter', default='\t', help='Delimiter for rows in the table (default: tab)')
    parser.add_argument('-t', dest='file_type', choices=['tsv', 'csv', 'json', 'xlsx', 'ods', 'pkl'], help='Type of file (tsv, csv, json, xlsx, ods)')
    parser.add_argument('--debug', action="store_true", help="Enable debug log.")
    parser.add_argument('--debug-verbose', action="store_true", help="Enable debug verbose log.")
    parser.add_argument('--headerless', action="store_false", help="By default the first row is interpreted as a header row. If --headerless is passed then there is no header.")
    args = parser.parse_args()


    function_data = {
        "items" : [],
        "header": [],
        "unselectable_indices" : [],
        "colours": get_colours(0),
        "top_gap": 0,
        "max_column_width": 70,
    }
    
    if args.file:
        input_arg = args.file[0]

    elif args.stdin:
        input_arg = '--stdin'
    elif args.stdin2:
        input_arg = '--stdin2'
    # elif args.filename:
    #     input_arg = args.filename

    elif args.generate:
        function_data["refresh_function"] = lambda : generate_picker_data(args.generate)
        function_data["get_data_startup"] = True
        function_data["get_new_data"] = True
        return args, function_data
    elif args.load:
        function_data = load_state(args.load)
        function_data["refresh_function"] = lambda : (load_state(args.load)["items"], load_state(args.load)["header"])
        function_data["get_new_data"] = True
        return args, function_data

    else:
        # print("Error: Please provide input file or use --stdin flag.")
        print("No data provided. Loading empty Picker.")
        return args, function_data
        # sys.exit(1)
    if args.debug:
        function_data["debug"] = True
        function_data["debug_level"] = 1

    if args.debug_verbose:
        function_data["debug"] = True
        function_data["debug_level"] = 0
    
    if not args.file_type:
        filetype = guess_file_type(input_arg)
    else:
        filetype = args.file_type
    

    while True:
        try:
            items, header, sheets = table_to_list(
                input_arg=input_arg, 
                delimiter=args.delimiter, 
                file_type = filetype,
                first_row_is_header=args.headerless,
            )
            if args.file:
                function_data["loaded_file"] = args.file[0]
                function_data["loaded_files"] = args.file
            break

        except Exception as e:
            items, header, sheets = [], [], []
            function_data["startup_notification"] = f"Error loading {input_arg}. {e}"
            if args.file:
                args.file = args.file[1:]
                input_arg = args.file[0]
            else:
                break

    function_data["items"] = items
    if header: function_data["header"] = header
    function_data["sheets"] = sheets

    return args, function_data

def start_curses() -> curses.window:
    """ Initialise curses and return curses window. """
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors() # For terminal theme-recolouring
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)
    stdscr.keypad(True) # Ensures that arrow and function keys are received as one key by getch
    curses.raw() # Disable control keys (ctrl-c, ctrl-s, ctrl-q, etc.)
    curses.curs_set(False)

    return stdscr

def close_curses(stdscr: curses.window) -> None:
    """ Close curses. """
    stdscr.keypad(False)
    curses.nocbreak()
    curses.noraw()
    curses.echo()
    curses.endwin()

def restrict_curses(stdscr: curses.window) -> None:
    """ Restrict curses for normal input. Used when dropping to ipython. """
    stdscr.keypad(False)
    curses.nocbreak()
    curses.noraw()
    curses.curs_set(True)
    curses.echo()

def unrestrict_curses(stdscr: curses.window) -> None:
    """ Unrestrict curses for terminal input. Used after dropping to ipython. """
    curses.noecho()  # Turn off automatic echoing of keys to the screen
    curses.cbreak()  # Interpret keystrokes immediately (without requiring Enter)
    stdscr.keypad(True)
    curses.raw() # Disable control keys (ctrl-c, ctrl-s, ctrl-q, etc.)
    curses.curs_set(False)



def main() -> None:
    """ Main function when listpick is executed. Deals with command line arguments and starts a Picker. """
    args, function_data = parse_arguments()

    try:
        if function_data["items"] == []:
            function_data["items"] = test_items
            function_data["highlights"] = test_highlights
            function_data["header"] = test_header
    except:
        pass
        
    # function_data["colour_theme_number"] = 3
    # function_data["modes"]  = [ 
    #     {
    #         'filter': '',
    #         'sort': 0,
    #         'name': 'All',
    #     },
    #     {
    #         'filter': '--2 miss',
    #         'name': 'miss',
    #     },
    #     {
    #         'filter': '--2 mp4',
    #         'name': 'mp4',
    #     },
    # ]
    # function_data["highlights"] = [
    #     {
    #         "field": 1,
    #         "match": "a",
    #         "color": 8,
    #     }
    # ]

    # function_data["cell_cursor"] = True
    # function_data["display_modes"] = True
    # function_data["centre_in_cols"] = True
    # function_data["show_row_header"] = True
    # function_data["keys_dict"] = picker_keys
    # function_data["id_column"] = -1
    # function_data["track_entries_upon_refresh"] = True
    # function_data["centre_in_terminal_vertical"] = True
    # function_data["highlight_full_row"] = True
    # function_data["pin_cursor"] = True
    # function_data["display_infobox"] = True
    # function_data["infobox_items"] = [["1"], ["2"], ["3"]]
    # function_data["infobox_title"] = "Title"
    # function_data["footer_string"] = "Title"
    # function_data["show_footer"] = False
    # function_data["paginate"] = True
    # function_data["debug"] = True
    # function_data["debug_level"] = 1


    # function_data["split_right"] = True
    # function_data["split_right_proportion"] = 2/3
    # function_data["split_right_refresh_data"] = data_refresh_randint_title
    # function_data["split_right_function"] = right_split_display_list
    # function_data["split_right_data"] = ["Files", [str(x) for x in range(100)]]


    # function_data["split_right_refresh_data"] = get_dl


    # function_data["split_right_function"] = right_split_file_attributes
    # function_data["split_right_auto_refresh"] = True
    # function_data["split_right_function"] = right_split_graph

    stdscr = start_curses()
    try:
        # Run the Picker

        # app = Picker(stdscr, **function_data)
        app = Picker(stdscr)
        app.set_config("~/.config/listpick/config.toml")
        app.set_function_data(function_data)
        app.splash_screen("Listpick is loading your data...")
        app.load_input_history("~/.config/listpick/cmdhist.json")
        app.run()

        app.save_input_history("~/.config/listpick/cmdhist.json")
    except Exception as e:
        print(e)

    # Clean up
    close_curses(stdscr)

if __name__ == '__main__':
    main()
