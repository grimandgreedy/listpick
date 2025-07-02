#!/bin/python
# -*- coding: utf-8 -*-
"""
clipboard_operations.py
Copy selected items in selected format to the clipboard.

Author: GrimAndGreedy
License: MIT
"""

import pyperclip
from typing import Tuple

"""
representation: python, tab-separated, comma-separated, current view
rows: selected, all, filtered
columns: all, not hidden
"""

def copy_to_clipboard(items: list[list[str]], indexed_items: list[Tuple[int, list[str]]], selections: dict, hidden_columns: set, representation: str="python", copy_hidden_cols: bool = False, separator="\t") -> None:
    """ 
    Copy selected items to clipboard.

    representation (str): The representation of the rows that should be copied.
                            accepted values: python, csv, tsv, current view, custom_sv

    """
    selected_indices = [i for i, selected in selections.items() if selected]
    rows_to_copy = [item for i, item in enumerate(items) if i in selected_indices]
    formatted_items = [[cell for i, cell in enumerate(item) if i not in hidden_columns or copy_hidden_cols] for item in rows_to_copy]
    if representation == "python":
        pyperclip.copy(repr(formatted_items))
    elif representation == "tsv":
        pyperclip.copy("\n".join(["\t".join(row) for row in formatted_items]))
    elif representation == "csv":
        pyperclip.copy("\n".join([",".join(row) for row in formatted_items]))
    elif representation == "custom_sv":
        # Ensure that escapes are interpreted properly in separator
        separator = bytes(separator, "utf-8").decode("unicode_escape")
        pyperclip.copy("\n".join([separator.join(row) for row in formatted_items]))
    # elif representation == "current_view":
    #     pyperclip.copy("\n".join([format_row(row, hidden_columns, column_widths, separator, centre_in_cols) for row in formatted_items]))
