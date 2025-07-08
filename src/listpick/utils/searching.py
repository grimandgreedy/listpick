#!/bin/python
# -*- coding: utf-8 -*-
"""
searching.py
Search list[list[str]] 

Author: GrimAndGreedy
License: MIT
"""

from typing import Tuple
from listpick.utils.search_and_filter_utils import apply_filter, tokenise

def search(query: str, indexed_items: list[Tuple[int, list[str]]], highlights: list[dict]=[], cursor_pos:int=0, unselectable_indices:list=[], reverse:bool=False, continue_search:bool=False) -> Tuple[bool, int, int, int, list[dict]]:
    """
    Search the indexed items and see which rows match the query.

    Accepts:
        regular expressions
        --# to specify column to match
        --i to specify case-sensitivity (it is case insensitive by default)
        --v to specify inverse match

    ---Returns: a tuple consisting of the following
        return_val:     True if search item found
        cursor_pos:     The position of the next search match
        search_index:   If there are x matches then search_index tells us we are on the nth out of x
        search_count:   The number of matches
        highlights:     Adds the search highlights to the existing highlights list 
                            I.e.,, we append the following to the highlights list to be displayed in draw_screen
                            {
                                "match": token,
                                "field": "all",
                                "color": 10,
                                "type": "search",
                            }

    """
    
    # Clear previous search highlights

    if len(indexed_items) < 1: 
        return False, cursor_pos, 0, 0, highlights
    highlights = [highlight for highlight in highlights if "type" not in highlight or highlight["type"] != "search" ]





    # Ensure we are searching from our current position forwards
    searchables =  list(range(cursor_pos+1, len(indexed_items))) + list(range(cursor_pos+1))
    if reverse:
        searchables =  (list(range(cursor_pos, len(indexed_items))) + list(range(cursor_pos)))[::-1]

    invert_filter = False
    case_sensitive = False
    filters = tokenise(query)

    if not filters: return False, cursor_pos, 0,0,highlights
    found = False
    search_count = 0
    search_list = []
    
    for i in searchables:
        # if apply_filter(indexed_items[i][1]):
        if apply_filter(indexed_items[i][1], filters, add_highlights=True, highlights=highlights):
            new_pos = i
            if new_pos in unselectable_indices: continue
            search_count += 1
            search_list.append(i)
            
            if not found:
                cursor_pos = new_pos
                found = True
            # break
            # return False
            # for i in range(diff):
            #     cursor_down()
            # break
    if search_list:
        search_index = sorted(search_list).index(cursor_pos)+1
    else:
        search_index = 0

    return bool(search_list), cursor_pos, search_index, search_count, highlights

