#!/bin/python
# -*- coding: utf-8 -*-
"""
filtering.py
Apply filter(s) to a list of lists and return indexed matched rows.

Author: GrimAndGreedy
License: MIT
"""

import re
from typing import Tuple
from listpick.utils.search_and_filter_utils import apply_filter, tokenise
import os

def filter_items(items: list[list[str]], indexed_items: list[Tuple[int, list[str]]], query: str) -> list[Tuple[int, list[str]]]:
    """ 
    Filter items based on the query.

    Accepts:
        regular expressions
        --# to specify column to match
        --i to specify case-sensitivity (it is case insensitive by default)
        --v to specify inverse match

    E.g.,

        --1 query       matches query in the 1 column


    Returns indexed_items, which is a list of tuples; each tuple consists of the index and the data of the matching row in the original items list. 
    """


    invert_filter = False
    case_sensitive = False

    filters = tokenise(query)

    indexed_items = [(i, item) for i, item in enumerate(items) if apply_filter(item, filters)]
    return indexed_items
