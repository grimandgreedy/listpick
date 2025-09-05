#!/bin/python
# -*- coding: utf-8 -*-
"""
get_data.py
Functions to get data to be displayed in the a pane.

Author: GrimAndGreedy
License: MIT
"""

from listpick.pane.pane_utils import get_file_attributes

def data_refresh_randint_by_row(data, state):
    """
    Add a random number to the data if row id is the same.


    Can be used with right_split_graph()
    
    data[0]: 0,1,2,...,n+1
    data[1]: randint(), randint(), ...
    data[2]: row id
    """
    from random import randint
    if state["indexed_items"]:
        id = state["indexed_items"][state["cursor_pos"]][1][state["id_column"]]
    else:
        return [[0], [0], -1]
    if data in [[], {}, None] or data[2] != id:
        return [[0], [randint(0, 1000)], id]
    else:
        data[0].append(data[0][-1]+1)
        data[1].append(randint(0, 1000))
    return data

def data_refresh_randint(data, state):
    """ 
    Add a random number to the data--regardless of whether the row id is the same.


    Can be used with right_split_graph()

    data[0]: 0,1,2,...,n+1
    data[1]: randint(), randint(), ...
    data[2]: row id
    """
    from random import randint

    if data in [[], {}, None]:
        return [[0], [randint(0, 1000)], -1]
    else:
        data[0].append(data[0][-1]+1)
        data[1].append(randint(0, 1000))
    return data


def data_refresh_randint_title(data, state):
    """ 
    Add a random number to data[1]. 

    Can be used with right_split_display_list()

    data[0]: title
    data[1]: randint(), randint(), ...
    """
    from random import randint

    if data in [[], {}, None]:
        return ["I CHOOSE", [str(randint(0, 1000))]]
    else:
        data[1].append(str(randint(0, 1000)))
    return data

def get_dl(data, state):
    """
    Get dl speed and add it to data[1]

    data[0]: 0,1,2,...,n+1
    data[1]: dl_speed_at_0, dl_speed_at_1, ...
    data[2]: row id
    """
    from aria2tui.utils import aria2c_utils

    gid = "3c60b0fc67230b66"
    req = aria2c_utils.tellStatus(gid)
    info = aria2c_utils.sendReq(req)
    dl = info["result"]["downloadSpeed"]
    ul = info["result"]["uploadSpeed"]

    dl, ul = int(dl), int(ul)

    if data in [[], {}, None]:
        return [[0], [dl], gid]
    else:
        data[0].append(data[0][-1]+1)
        data[1].append(dl)
    return data


def update_file_attributes(data, state):
    """
    Get file attributes

    data[0]: ["size: {}", filetype: {}, last modified: {}]
    ]
    data[1]: id
    """
    if state["indexed_items"]:
        # id = state["indexed_items"][state["cursor_pos"]][1][state["id_column"]]
        id = state["indexed_items"][state["cursor_pos"]][1][0]
    else:
        return [[], -1]
    return [get_file_attributes(id), id]
    

