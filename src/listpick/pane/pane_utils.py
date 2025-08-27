#!/bin/python
# -*- coding: utf-8 -*-
"""
pane_utils.py
Utility functions for Picker panes.

Author: GrimAndGreedy
License: MIT
"""

import re

def escape_ansi(line: str) -> str:
    """ Remove ansi characters from string. """
    ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)


def get_graph_string(x_vals, y_vals, width=50, height=20, title=None, x_label=None, y_label=None):
    """ Generate a graph of x_vals, y_vals using plotille"""

    import plotille as plt
    # Create a figure and axis object using plotille
    fig = plt.Figure()
    
    # Plot the data on the figure
    fig.plot(x_vals, y_vals)
    
    # Set the dimensions of the graph
    fig.width = width-10
    fig.height = height-4
    fig.x_ticks_fkt = lambda x, _: f"{int(x)}s"
    fig.y_ticks_fkt = lambda y, _: f"{int(y)}"
    
    # Set the title and labels if provided
    if title:
        fig.title = title
    if x_label:
        fig.xlabel = x_label
    if y_label:
        fig.ylabel = y_label
    
    # Generate the ASCII art of the graph
    ascii_art = str(fig.show())
    
    return ascii_art


def get_file_attributes(filename):
    import mimetypes
    import time
    import os
    try:
        if not os.path.exists(filename) and len(filename) > 2 and filename[0] == "'" and filename[-1] == "'":
            filename = filename[1:-1] 

        abs_path = os.path.abspath(filename)
        
        if not os.path.exists(abs_path):
            return ["File not found"]

        # Get the size of the file in bytes and convert it to a human-readable format
        size = os.path.getsize(abs_path)
        size_str = f"{(size / (1024 * 1024 * 1024)):,.2f}GB" if size > 1024 ** 3 else \
                   f"{(size / (1024 * 1024)):,.2f}MB" if size > 1024 ** 2 else \
                   f"{(size / 1024):,.2f}KB" if size > 1024 else f"{size}B"
        
        # Get the file type
        mime_type, _ = mimetypes.guess_type(abs_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Get the last modified time in a human-readable format
        mod_time = os.path.getmtime(abs_path)
        mod_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
        
        attributes = [
            f"Size: {size_str}",
            f"Filetype: {mime_type}",
            f"Last Modified: {mod_str}"
        ]
        
        return attributes
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

