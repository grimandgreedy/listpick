#!/bin/python
# -*- coding: utf-8 -*-
"""
search_and_filter_utils.py
Utilities for searching and filtering.

Author: GrimAndGreedy
License: MIT
"""

import re

def apply_filter(row: list[str], filters: dict, case_sensitive: bool = False, add_highlights:bool = False, highlights: list=[]) -> bool:
    """ Checks if row matches the filter. """
    for col, filter_list in filters.items():
        for filter in filter_list:
            if case_sensitive or (filter != filter.lower()):
                pattern = re.compile(filter)
            else:
                pattern = re.compile(filter, re.IGNORECASE)
            if col == -1:  # Apply filter to all columns
                if not any(pattern.search(str(item)) for item in row):
                    return False
                # return not invert_filter
            elif col >= len(row) or col < 0:
                return False
            else:
                cell_value = str(row[col])
                if not pattern.search(str(cell_value)):
                    return False
                # return invert_filter

    if add_highlights:
        for col, filter_list in filters.items():
            for filter in filter_list:
                hcol = "all" if col == -1 else col
                highlight = {
                    "match": filter,
                    "field": hcol,
                    "color": 10,
                    "type": "search",
                }
                if highlight not in highlights:
                    highlights.append(highlight)
    
    return True


def tokenise(query:str) -> dict:
    """ Convert query into dict consisting of filters. '--1  """
    filters = {}

    # tokens = re.split(r'(\s+--\d+|\s+--i)', query)
    # tokens = re.split(r'((\s+|^)--\w)', query)
    tokens = re.split(r'\s+', query)
    tokens = [token.strip() for token in tokens if token.strip()]  # Remove empty tokens
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token:
            if token.startswith("--"):
                flag = token
                if flag == '--v':
                    invert_filter = True 
                    i += 1
                elif flag == '--i':
                    case_sensitive = True
                    i += 1
                else:
                    if i+1 >= len(tokens):
                        break
                    col = int(flag[2:])
                    arg = tokens[i+1].strip()
                    try:
                        i+=2
                        re.compile(arg)
                        if col in filters: filters[col].append(arg)
                        else: filters[col] = [arg]
                    except:
                        pass
            else:
                try:
                    i += 1
                    re.compile(token)
                    if -1 in filters: filters[-1].append(token)
                    else: filters[-1] = [token]
                except:
                    pass
        else:
            i += 1
    return filters
