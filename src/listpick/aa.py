
import curses
import re
import os
import subprocess
import argparse
import time
from wcwidth import wcswidth
from typing import Callable, Optional, Tuple

from listpick.ui.picker_colours import get_colours, get_help_colours, get_notification_colours, get_theme_count
from listpick.utils.options_selectors import default_option_input, output_file_option_selector, default_option_selector
from listpick.utils.table_to_list_of_lists import *
from listpick.utils.utils import *
from listpick.utils.sorting import *
from listpick.utils.filtering import *
from listpick.ui.input_field import *
from listpick.utils.clipboard_operations import *
from listpick.utils.searching import search
from listpick.ui.help_screen import help_lines
from listpick.ui.keys import picker_keys, notification_keys, options_keys, help_keys
from listpick.utils.generate_data import generate_picker_data
from listpick.utils.dump import dump_state, load_state, dump_data
from listpick.ui.build_help import build_help_rows
from listpick.ui.footer import StandardFooter, CompactFooter
from listpick.listpick_app import *
from listpick.listpick_app import Picker, start_curses, close_curses


stdscr = start_curses()

x = Picker(stdscr, items=[], search_query="HI")
x.run()

close_curses(stdscr)
