#!/bin/python
# -*- coding: utf-8 -*-
"""
input_field.py
Function to display an input field within a curses window.

Author: GrimAndGreedy
License: MIT
"""

import curses
from typing import Tuple, Optional, Callable
import os

def input_field(
    stdscr: curses.window,
    usrtxt:str="",
    field_prefix: str = " Input: ",
    x:Callable=lambda:0,
    y:Callable=lambda:0,
    colours_start:int=0,
    colour_pair_bg: int = 20,
    colour_pair_text: int = 13,
    literal:bool=False,
    max_length:Callable = lambda: 1000,
    registers: dict={},
    refresh_screen_function:Optional[Callable]=None,
    cursor: int = 0,
    path_auto_complete: bool = True,
    history: list[str] = [],
    clear_screen: bool = True,
        
) -> Tuple[str, bool]:
    """
    Display input field at x,y for the user to enter text.

    ---Arguments
        stdscr: curses screen
        usrtxt (str): text to be edited by the user
        field_prefix (str): The text to be displayed at the start of the input field
        x (Callable): prompt begins at (x,y) in the screen given. x is callable so that our input_field adapts to terminal resizing and/or text size changes.
        y (Callable): prompt begins at (x,y) in the screen given. y is callable so that our input_field adapts to terminal resizing and/or text size changes.
        colours_start (int): where to start when initialising the colour pairs with curses.
        colour_pair_text (int): which curses.color_pair to use for displaying the text of the input box.
        colour_pair_bg (int): which curses.color_pair to use for clearing the background for the input field.
        literal: whether to display the repr() of the string; e.g., if we want to display escape sequences literally
        max_length (callable): function that returns the length of input field
        refresh_screen_function (Callable): If the terminal resizes we likely want to redraw the rest of the screen with the new size. 
                            If no refresh_screen_function is passed then only the input field will adapt when the terminal resizes.
        registers (dict): registers for use with ctrl+r (currently only the * register will work)
        cursor (int): the starting position of the cursor.
        path_auto_complete (bool): whether tab (or shift+tab) should trigger path autocomplete
        history (list[str]): list of history to by cycled through with ctrl+n/ctrl+p
        clear_screen (bool): whether to clear the screen each time a key is pressed or getch timeout is reached.


    ---Returns
        usrtxt, return_code
        usrtxt: the text inputted by the user
        return_code: 
                        0: user hit escape
                        1: user hit return
    """
    potential_path = usrtxt
    word_separator_chars = ["/", " "]
    kill_ring = []
    kill_ring_active = False
    kill_ring_index = 0
    prev_usrtxt = ""
    history_index = len(history)

    offscreen_x, offscreen_y = False, False
    orig_x, orig_y = x, y

    # Input field loop
    while True:

        h, w = stdscr.getmaxyx()

        if refresh_screen_function != None:
            refresh_screen_function()

        # If the beggining of the input field starts offscreen (i.e., x>=w or y>=h) then set x=0 or y=0
        if orig_x() >= w or orig_x() < 0: x = lambda: 0
        else: x = orig_x
        if orig_y() >= h or orig_y() < 0: y = lambda: 0
        else: y = orig_y


        field_end = min(w, x()+max_length())       # Last character of terminal that can be written to
        field_y = min(h-1, y())                    
        max_field_length = field_end - x()         # Maximum length of the string displayed

        # We can't write to the last char of the last row of the terminal in curses
        if field_y == h-1 and field_end == w:
            max_field_length -= 1

        # Clear background to end of the input field
        stdscr.addstr(field_y, x(), " "*(max_field_length), curses.color_pair(colours_start+colour_pair_bg))
        stdscr.refresh()

        if literal:
            field_string_length = len(repr(usrtxt)) + len(field_prefix)
        else:
            field_string_length = len(usrtxt) + len(field_prefix)

        ## Display the field name and current usrtxt
        if literal:
            # If usrtxt overspills the length of the input field then clip the usrtxt before setting the disp_string
            if field_string_length > max_field_length:
                disp_string = f"{field_prefix}{repr(usrtxt)[-(cursor+max_field_length-len(field_prefix)):]}"[:max_field_length]
            else:
                disp_string = f"{field_prefix}{repr(usrtxt)}"[:max_field_length]
        else:
            # If usrtxt overspills the length of the input field then clip the usrtxt before setting the disp_string
            if field_string_length >= max_field_length:
                disp_string = f"{field_prefix}{usrtxt[-(cursor+max_field_length-len(field_prefix)-1):]}"[:max_field_length]
            else:
                disp_string = f"{field_prefix}{usrtxt}"[:max_field_length]
        stdscr.addstr(field_y, x(), disp_string, curses.color_pair(colours_start+colour_pair_text) | curses.A_BOLD)

        ## Display cursor 
        # If the whole of usrtxt fits within the input field
        cursor_x_pos, cursor_char = x(), " "
        if field_string_length < max_field_length:
            if not literal:
                cursor_x_pos = min(field_string_length + x() - cursor, w-1)
                if usrtxt and cursor != 0: cursor_char = f"{usrtxt[-(cursor)]}"
                else: cursor_char = " "
            elif literal:
                cursor_x_pos = min(field_string_length + x()-cursor-2, w-1)
                cursor_char = repr(usrtxt)[-(cursor+1)]
        # If usrtxt is longer than the length of the input field and the cursor position is in the first `max_field_length` characters.
        elif field_string_length >= max_field_length and field_string_length - cursor < max_field_length:
            if not literal:
                cursor_x_pos = min(field_string_length + x() - cursor, w-1)
                cursor_char = f"{usrtxt[-(cursor)]}"
            elif literal:
                cursor_x_pos = min(field_string_length + x() - cursor - 1, w-1)
                cursor_char = repr(usrtxt)[-(cursor+1)]
        # If usrtxt is longer than the length of the input field and the cursor is positioned after field_string_length characters then the cursor will be at the end of the input field
        else:
            if not literal:
                cursor_x_pos = max_field_length+x()-1
                cursor_char = f" "
            elif literal:
                cursor_char = repr(usrtxt)[-(cursor+1)]
                cursor_x_pos = max_field_length+x()-1

        stdscr.addstr(field_y, cursor_x_pos, cursor_char, curses.color_pair(colours_start+colour_pair_text) | curses.A_REVERSE | curses.A_BOLD)


        key = stdscr.getch()

        if key in [27, 7]:                                                           # ESC/ALT key or Ctrl+g
            # For Alt-key combinations: set nodelay and get the second key
            stdscr.nodelay(True)
            key2 = stdscr.getch()

            if key2 == -1:                  # ESCAPE key (no key-combination)
                stdscr.nodelay(False)
                return "", False
            elif key2 == curses.KEY_BACKSPACE:
                # Delete to backslash or space (word_separator_chars)
                search_txt = usrtxt[:-cursor] if cursor > 0 else usrtxt
                index = -1
                for word_separator_char in word_separator_chars:
                    tmp_index = search_txt[::-1].find(word_separator_char)
                    if tmp_index > -1:
                        if index == -1:
                            index = tmp_index
                        else:
                            index = min(index, tmp_index)

                if index == -1:
                    if cursor == 0:
                        kill_ring.append(usrtxt)
                        usrtxt = ""
                    else:
                        kill_ring.append(usrtxt[:-(cursor+1)])
                        usrtxt = usrtxt[-(cursor+1):]
                    cursor = len(usrtxt)
                else:
                    if index == 0:
                        kill_ring.append(search_txt[-1:])
                        usrtxt = search_txt[:-1] + usrtxt[len(search_txt):]
                    else:
                        kill_ring.append(search_txt[-index:])
                        usrtxt = search_txt[:-index] + usrtxt[len(search_txt):]

                potential_path = usrtxt
                kill_ring_active = False

            elif key2 == ord('f'):
                # Forward word
                search_txt = usrtxt[-cursor:]
                index = -1
                for word_separator_char in word_separator_chars:
                    tmp_index = search_txt.find(word_separator_char)

                    if tmp_index > -1:
                        if index == -1:
                            index = tmp_index
                        else:
                            index = min(index, tmp_index)

                if index == -1:
                    cursor = 0
                else:
                    cursor -= index + 1
                    cursor = max(cursor, 0)
                kill_ring_active = False

            elif key2 == ord('b'):
                # Backwards word
                search_txt = usrtxt[:-cursor] if cursor > 0 else usrtxt
                index = -1
                for word_separator_char in word_separator_chars:
                    tmp_index = search_txt[::-1].find(word_separator_char)

                    if tmp_index == 0:
                        tmp_index = search_txt[:-1][::-1].find(word_separator_char)

                    if tmp_index > -1:
                        if index == -1:
                            index = tmp_index
                        else:
                            index = min(index, tmp_index)

                if index == -1:
                    cursor = len(usrtxt)
                else:
                    cursor += index + 1
                kill_ring_active = False

            elif key2 == ord('y'):
                prev_kill_ring_index = kill_ring_index
                kill_ring_index = (kill_ring_index + 1)%len(kill_ring)
                if kill_ring_active and len(kill_ring):
                    if cursor == 0:
                        usrtxt = usrtxt[:-len(kill_ring[prev_kill_ring_index])]
                        usrtxt += kill_ring[kill_ring_index]
                    else:
                        usrtxt = usrtxt[-cursor:-(cursor+len(kill_ring[prev_kill_ring_index]))]
                        usrtxt = usrtxt[:-cursor] + kill_ring[kill_ring_index] + usrtxt[-cursor:]
            # Return to delayed getch
            stdscr.nodelay(False)

        elif key == 3:                                                           # ctrl+c
            # Immediate exit
            stdscr.keypad(False)
            curses.nocbreak()
            curses.noraw()
            curses.echo()
            curses.endwin()
            exit()

        elif key == 10:                                                         # Enter/return key
            # Return
            return usrtxt, True

        elif key in [curses.KEY_BACKSPACE, "KEY_BACKSPACE", 263, 127]:
            # Delete char before cursor

            if cursor == 0:
                usrtxt = usrtxt[:-1]
            else:
                usrtxt = usrtxt[:-(cursor+1)] + usrtxt[-cursor:]
            potential_path = usrtxt
            kill_ring_active = False

        elif key in [curses.KEY_LEFT, 2]:                                       # CTRL+B
            # Go back one character
            cursor = min(len(usrtxt), cursor + 1)
            kill_ring_active = False

        elif key in [curses.KEY_RIGHT, 6]:                                      # CTRL-F
            # Go forward one character
            cursor = max(0, cursor - 1)
            kill_ring_active = False

        elif key in [4, 330]:                                                   # Ctrl+D, Delete
            # Delete char after cursor
            if cursor != 0 and usrtxt != "":
                if cursor == 1:
                    usrtxt = usrtxt[:-(cursor)]
                else:
                    usrtxt = usrtxt[:-(cursor)] + usrtxt[-(cursor-1):]
                cursor = max(0, cursor - 1)
            potential_path = usrtxt
            kill_ring_active = False
                
        elif key == 21 or key == "^U":                                          # CTRL+U
            # Delete from cursor to beginning of usrtxt
            if cursor == 0:
                usrtxt = ""
            else:
                usrtxt = usrtxt[-(cursor+1):]
            cursor = len(usrtxt)
            potential_path = usrtxt
            kill_ring_active = False

        elif key == 11 or key == "^K":                                          # CTRL+K
            # Delete from cursor to end of usrtxt
            if cursor: usrtxt = usrtxt[:-cursor]
            cursor = 0
            potential_path = usrtxt
            kill_ring_active = False

        elif key in [1, 262]:                                            # CTRL+A (beginning)
            # Send cursor to beginning of usrtxt
            cursor = len(usrtxt)
            kill_ring_active = False
            
        elif key in [5, 360]:                                                          # CTRL+E (end)
            # Send cursor to end of usrtxt
            cursor = 0
            kill_ring_active = False

        elif key in [18]:                                                          # CTRL+R
            # Get register (* by default)
            if "*" in registers:
                if cursor == 0:
                    addtxt = registers["*"]
                    usrtxt = usrtxt[-cursor:] + registers["*"]
                else:
                    usrtxt = usrtxt[:-cursor] + registers["*"] + usrtxt[-cursor:]
            kill_ring_active = False

        elif key in [23,8]:                                                     # Ctrl+BACKSPACE, CTRL+W
            # Delete backwards to space or start of usrtxt
            search_txt = usrtxt[:-cursor] if cursor > 0 else usrtxt
            index = search_txt[::-1].find(" ")
            if index == 0:
                index = search_txt[:-1][::-1].find(" ")+ 1
            if index == -1:
                if cursor == 0:
                    kill_ring.append(usrtxt)
                    usrtxt = ""
                else:
                    kill_ring.append(usrtxt[:-(cursor+1)])
                    usrtxt = usrtxt[-(cursor+1):]
                cursor = len(usrtxt)
            else:
                kill_ring.append(search_txt[-index:])
                usrtxt = search_txt[:-index] + usrtxt[len(search_txt):]

            potential_path = usrtxt
            kill_ring_active = False
        elif key == curses.KEY_RESIZE:
            # Do nothing
            pass
        elif key == 9:                                                      # Tab key
            # Cycle forwards through path completions (if applicable)
            completions = autocomplete_path(potential_path)
            if completions:
                dir, file = os.path.split(potential_path)
                
                middle = "" if not dir else "/"
                index = 0
                try:
                    dir2, file2 = os.path.split(usrtxt)
                    index = (completions.index(file2) + 1)%len(completions)
                except:
                    pass
                usrtxt = dir + middle + completions[index]
                # If there is only one completion option then set this to the potential_path
                if len(completions) == 1:
                    potential_path = usrtxt
            if potential_path.startswith("//"):
                potential_path = potential_path[1:]
            if usrtxt.startswith("//"):
                usrtxt = usrtxt[1:]
            kill_ring_active = False

        elif key == 353:                                            # Shift+Tab key
            # Cycle backwards through path completions (if applicable)
            completions = autocomplete_path(potential_path)
            if completions:
                dir, file = os.path.split(potential_path)
                
                middle = "" if file else "/"
                index = 0
                try:
                    dir2, file2 = os.path.split(usrtxt)
                    index = (completions.index(file2) - 1)%len(completions)
                except:
                    pass
                usrtxt = dir + "/" + completions[index]
                # If there is only one completion option then set this to the potential_path
                if len(completions) == 1:
                    potential_path = usrtxt
            if potential_path.startswith("//"):
                potential_path = potential_path[1:]
            if usrtxt.startswith("//"):
                usrtxt = usrtxt[1:]
            kill_ring_active = False

        elif key == 25:                                         # Ctrl+y
            # Yank from the top of the kill ring
            if len(kill_ring) > 0:
                kill_ring_index = 0
                if cursor == 0:
                    usrtxt += kill_ring[kill_ring_index]
                else:
                    usrtxt = usrtxt[:-cursor] + kill_ring[kill_ring_index] + usrtxt[-cursor:]
                kill_ring_active = True
        elif key in [14, curses.KEY_DOWN, 258]:                 # Ctrl+n
            # Cycle forwards through history
            if history_index == len(history)-1:
                usrtxt = prev_usrtxt
                history_index += 1
            elif history_index < len(history):
                history_index += 1
                usrtxt = history[history_index]

        elif key in [16, curses.KEY_UP, 258]:                 # Ctrl+p
            # Cycle backwards through history
            if len(history):
                if history_index == len(history):
                    prev_usrtxt = usrtxt
                history_index = max(0, history_index-1)
                usrtxt = history[history_index]
        elif key == 24:                     # Ctrl+x 
            # Edit with nvim
            pass


        else:
            # Try to add representatio of keycode to usrtxt
            if isinstance(key, int):
                try:
                    val = chr(key) if chr(key).isprintable() else ''
                except:
                    val = ''
            else: val = key
            if cursor == 0:
                usrtxt += val
            else:
                usrtxt = usrtxt[:-cursor] + val + usrtxt[-cursor:]
            if val:
                potential_path = usrtxt
            kill_ring_active = False
        if clear_screen:
            stdscr.erase()


def autocomplete_path(partial_path: str) -> list:
    """ Given a partial path return the list of possible completion options. """
    # Expand home (if ~ is present)
    partial_path = os.path.expanduser(partial_path)
    dir, file = os.path.split(partial_path)
    
    # List all files and directories in the dir
    try:
        entries = os.listdir(dir)
    except FileNotFoundError:
        return []
    
    # Filter the entries that match the partial file
    completions = [entry for entry in entries if entry.startswith(file)]
    
    # If only one completion is found, append a trailing slash if it's a directory
    if len(completions) == 1 and not completions[0].endswith('/'):
        try:
            if os.path.isdir(os.path.join(dir, completions[0])):
                completions[0] += '/'
        except FileNotFoundError:
            pass
    return sorted(completions, key=lambda x: x.lower())
