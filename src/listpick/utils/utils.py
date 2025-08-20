#!/bin/python
# -*- coding: utf-8 -*-
"""
utils.py

Author: GrimAndGreedy
License: MIT
"""

from wcwidth import wcwidth, wcswidth
from math import log10
import subprocess
import tempfile
import os
from typing import Tuple, Dict
import logging

logger = logging.getLogger('picker_log')

def clip_left(text, n):
    """
    Clips the first `n` display-width characters from the left of the input string.
    
    Parameters:
    - text (str): The input string.
    - n (int): The number of display-width characters to clip from the left.
    
    Returns:
    - str: The remaining part of the string after clipping.
    """
    width = 0
    for i, char in enumerate(text):
        char_width = wcwidth(char)
        if width + char_width > n:
            return text[i:]
        width += char_width
    return text  # If the total width is less than n, return the full string

def truncate_to_display_width(text: str, max_column_width: int, centre=False, unicode_char_width: bool = True) -> str:
    """ 
    Truncate and/or pad text to max_column_width using wcwidth to ensure visual width is correct 
        with foreign character sets. 

    Return: The truncated and/or padded string which has a visual length of max_column_width. 
        If centre=True then the string is centred, if applicable.

    """
    # logger.debug("function: truncate_to_display_width (utils.py)")
    result = ''
    width = 0
    for char in text:
        w = wcwidth(char)
        if w < 0:
            continue
        if width + w > max_column_width:
            break
        result += char
        width += w
    # Pad if it's shorter
    padding = max_column_width - wcswidth(result)
    # return result + ' ' * padding
    if centre:
        result = ' '*(padding//2) + result + ' '*(padding//2 + padding%2)
    else:
        result = result + ' ' * padding 
    return result

def is_formula_cell(cell: str) -> bool:
    """ Returns whether the cell should be evaluated as a formula. """
    if cell.startswith("$"): return True
    else: return False

def evaluate_cell(cell:str) -> str:
    return str(eval(cell[1:]))


def format_row_full(row: list[str], hidden_columns:list = [], unicode_char_width: bool = True) -> str:
    """ Format list of strings as a tab-separated single string. No hidden columns. """
    return '\t'.join(str(row[i]) for i in range(len(row)) if i not in hidden_columns)

def format_full_row(row:str, unicode_char_width: bool = True) -> str:
    """ Format list of strings as a tab-separated single string. Includes hidden columns. """
    return '\t'.join(row)


def format_row(row: list[str], hidden_columns: list, column_widths: list[int], separator: str, centre:bool=False, unicode_char_width: bool = True) -> str:
    """ Format list of strings as a single string. Requires separator string and the maximum width of the columns. """
    row_str = ""
    for i, cell in enumerate(row):
        if i in hidden_columns: continue
        # if is_formula_cell(cell):
        #     cell = evaluate_cell(cell)
        
        val = truncate_to_display_width(str(cell), column_widths[i], centre)
        row_str += val + separator
    return row_str
    # return row_str.strip()

def get_column_widths(items: list[list[str]], header: list[str]=[], max_column_width:int=70, number_columns:bool=True, max_total_width=-1, separator = "    ", unicode_char_width: bool = True) -> list[int]:
    """ Calculate maximum width of each column with clipping. """
    if len(items) == 0: return [0]
    assert len(items) > 0
    widths = [max(wcswidth(str(row[i])) for row in items) for i in range(len(items[0]))]
    # widths = [max(len(str(row[i])) for row in items) for i in range(len(items[0]))]
    if header:
        header_widths = [wcswidth(f"{i}. {str(h)}") if number_columns else wcswidth(str(h)) for i, h in enumerate(header)]
        col_widths =  [min(max_column_width, max(widths[i], header_widths[i])) for i in range(len(header))]
        # actual_max_widths = [max(header_widths[i], widths[i]) for i in range(len(widths))]
        #
        # if sum(col_widths) + len(separator)*(len(col_widths)-1) < max_total_width:
        #     # Elongate rows...
        #     amount_less = max_total_width  - (sum(col_widths) + len(separator)*(len(col_widths)-1))
        #     number_over = sum([1 if col_widths[i] != actual_max_widths[i] else 0 for i in range(len(col_widths))])
        #     count = 0
        #     for i in range(len(col_widths)):
        #         if col_widths[i] < actual_max_widths[i]:
        #             col_widths[i] += amount_less//number_over
        #             count+=1
        #             if count == number_over:
        #                 col_widths[i]+= amount_less%number_over
        #                 break
        #     if sum(actual_max_widths) + len(separator)*(len(col_widths)-1) < max_total_width:
        #         col_widths = actual_max_widths
        #     else:
        #         # Maximise balance.....
        #         pass
    else:
        col_widths = [min(max_column_width, width) for width in widths]
    return col_widths

def get_mode_widths(item_list: list[str]) -> list[int]:
    """ Calculate the maximum width of modes with clipping. """
    widths = [wcswidth(str(row)) for row in item_list]
    return widths

def intStringToExponentString(n: str) -> str:
    """ Return exponent representation of integer. E.g., 1234 -> ¹²³⁴ """
    n = str(n)
    digitdict = { "0" : "⁰", "1" : "¹", "2" : "²", "3" : "³", "4" : "⁴", "5" : "⁵", "6" : "⁶", "7" : "⁷", "8" : "⁸", "9" : "⁹"}
    return "".join([digitdict[char] for char in n])

def convert_seconds(seconds:int, long_format:bool=False) -> str:
    """ Convert seconds to human readable format. E.g., 60*60*24*3+62=772262 -> 3d2m2s """
    if isinstance(seconds, str):
        seconds = int(seconds)

    # Calculate years, days, hours, minutes, and seconds
    years = seconds // (365 * 24 * 3600)
    days = (seconds % (365 * 24 * 3600)) // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    # Long format = years, days, hours, minutes, seconds
    if long_format:
        human_readable = []
        if years > 0:
            human_readable.append(f"{years} year{'s' if years > 1 else ''}")
        if days > 0:
            human_readable.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0:
            human_readable.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            human_readable.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        if remaining_seconds > 0 or not human_readable:
            human_readable.append(f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}")
        return ', '.join(human_readable)
    else:
        # Compact format = y, d, h, m, s
        compact_parts = []
        if years > 0:
            compact_parts.append(f"{years}y")
        if days > 0:
            compact_parts.append(f"{days}d")
        if hours > 0:
            compact_parts.append(f"{hours}h")
        if minutes > 0:
            compact_parts.append(f"{minutes}m")
        if remaining_seconds > 0 or not compact_parts:
            compact_parts.append(f"{remaining_seconds}s")
        return ''.join(compact_parts)

def convert_percentage_to_ascii_bar(p:int, chars:int=8) -> str:
    """ Convert percentage to an ascii status bar of length chars. """

    done = "█"
    notdone = "▒"
    return done * int(p / 100 * chars) + (chars-(int(p / 100 * chars)))*notdone
    return "[" + "=" * int(p / 100 * chars) + ">" + " " * (chars - int(p / 100 * chars) - 1) + "]"


def get_selected_indices(selections: dict[int, bool]) -> list[int]:
    """ Return a list of indices which are True in the selections dictionary. """

    # selected_indices = [items[i] for i, selected in selections.values() if selected]
    selected_indices = [i for i, selected in selections.items() if selected]
    return selected_indices

def get_selected_cells(cell_selections: Dict[Tuple[int, int], bool]) -> list[Tuple[int, int]]:
    """ {(0,1): True, (9,1): True} """
    selected_cells = [i for i, selected in cell_selections.items() if selected]
    return selected_cells

def get_selected_cells_by_row(cell_selections: dict[tuple[int, int], bool]) -> dict[int, list[int]]:
    """ {0: [1,2], 9: [1] }"""
    
    d = {}
    try:
        for tup in cell_selections.keys():
            if cell_selections[tup]:
                if tup[0] in d:
                    d[tup[0]].append(tup[1])
                else:
                    d[tup[0]] = [tup[1]]
    except:
        pass
    return d

def get_selected_values(items: list[list[str]], selections: dict[int, bool]) -> list[list[str]]:
    """ Return a list of rows based on wich are True in the selections dictionary. """
    selected_values = [items[i] for i, selected in selections.items() if selected]
    return selected_values

def format_size(n:int) -> str:
    """
    Convert bytes to a human-readable format. E.g., 8*1024*1024*3 -> 8MB
    
    Args:
        n (int): The number of bytes to convert.
        
    Returns:
        str: A string representing the bytes in a more human-readable form.
    """
    if n < 0:
        raise ValueError("Number must be non-negative")
    
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = {}
    for i, symbol in enumerate(symbols):
        prefix[symbol] = 1 << (i * 10)
        
    if n == 0:
        return "0B"
    
    symbol, value = "B", 0
    for symbol in reversed(symbols):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            break
    
    return f"{value:.1f}{symbol}"


def openFiles(files: list[str]) -> str:
    """
    Opens multiple files using their associated applications.
        Get mime types
        Get default application for each mime type
        Open all files; files with the same default application will be opened in one instance

    Args:
        files (list[str]): A list of file paths.

    Returns:
        str
    """
    logger.info("function: openFiles (utils.py)")
    def get_mime_types(files):
        types = {}

        for file in files:
            resp = subprocess.run(f"xdg-mime query filetype {file}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            ftype = resp.stdout.decode("utf-8").strip()
            if ftype in types:
                types[ftype] += [file]
            else:
                types[ftype] = [file]

        return types

    def get_applications(types):
        apps = {}

        for t in types:
            resp = subprocess.run(f"xdg-mime query default {t}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            app = resp.stdout.decode("utf-8").strip()
            if app in apps:
                apps[app] += [t]
            else:
                apps[app] = [t]

        return apps
    for i in range(len(files)):
        if ' ' in files[i] and files[i][0] not in ["'", '"']:
            files[i] = repr(files[i])

    types = get_mime_types(files)
    apps = get_applications(types.keys())

    apps_files = {}
    for app, filetypes in apps.items():
        flist = []
        for filetype in filetypes:
            flist += types[filetype]
        apps_files[app] = flist

    for app, files in apps_files.items():
        files_str = ' '.join(files)
        result = subprocess.Popen(f"gio launch /usr/share/applications/{app} {files_str}", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # if result.stderr: 
        #     return result.stderr.read().decode("utf-8").strip()
    return ""

def file_picker() -> list[str]:
    """ Run file picker (yazi by default) and return the path of the file picked. If no file is picked an empty string is returned. """

    logger.info("function: file_picker (utils.py)")
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        subprocess.run(f"yazi --chooser-file={tmpfile.name}", shell=True)

        lines = tmpfile.readlines()
        if lines:
            filenames = [line.decode("utf-8").strip() for line in lines]
            # filename = lines[0].decode("utf-8").strip()
            return filenames
        else:
            return []

            
def dir_picker() -> str:
    """ Run dir picker (yazi by default) and return the path of the directory one is in upon exit. """

    logger.info("function: dir_picker (utils.py)")
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        subprocess.run(f"yazi --cwd-file={tmpfile.name}", shell=True)

        lines = tmpfile.readlines()
        if lines:
            filename = lines[0].decode("utf-8").strip()
            return filename
        else:
            return ""

def guess_file_type(filename: str) -> str:
    """ Guess filetype. Currently just uses the extension of the file. """
    logger.info("function: guess_file_type (utils.py)")
    return filename.split(".")[-1]


def pad_lists_to_same_length(list_of_lists: list[list[str]]) -> list[list[str]]:
    """ Ensure that all lists in a list of lists are of the same length. Pad any shorter sublists with empty strings. """
    if not list_of_lists or list_of_lists in [[], [[]]]:
        return []
    if type(list_of_lists) == type([]) and len(list_of_lists) and type(list_of_lists[0]) == type(""):
        list_of_lists = [[x] for x in list_of_lists]

    # Find the maximum length of the sublists
    lengths = [len(sublist) for sublist in list_of_lists]
    max_length = max(lengths)
    min_length = min(lengths)
    if min_length == max_length: return list_of_lists

    # Pad each sublist with empty strings to match the maximum length
    padded_list = [sublist + [''] * (max_length - len(sublist)) for sublist in list_of_lists]

    return padded_list
