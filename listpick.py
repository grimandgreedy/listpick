#!/bin/python
# -*- coding: utf-8 -*-
"""
Parse command-line arguments and run Picker.

Author: GrimAndGreedy
License: MIT
"""


from src.listpick.listpick_app import main
from src.listpick.ui.help_screen import *
from src.listpick.ui.input_field import *
from src.listpick.ui.keys import *
from src.listpick.ui.picker_colours import *
from src.listpick.utils.clipboard_operations import *
from src.listpick.utils.dump import *
from src.listpick.utils.filtering import *
from src.listpick.utils.generate_data import *
from src.listpick.utils.options_selectors import *
from src.listpick.utils.search_and_filter_utils import *
from src.listpick.utils.searching import *
from src.listpick.utils.sorting import *
from src.listpick.utils.table_to_list_of_lists import *
from src.listpick.utils.utils import *
from src.listpick.listpick_app import *


if __name__ == "__main__":
    main()
