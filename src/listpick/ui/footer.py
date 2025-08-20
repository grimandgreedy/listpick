"""
footer.py
Lines to be displayed on the help screen.

Author: GrimAndGreedy
License: MIT
"""

import curses
import logging

logger = logging.getLogger('picker_log')

class Footer:
    def __init__(self, stdscr, colours_start, get_state_function):
        """
        stdscr: curses screen object
        colours_start: base colour pair index
        get_state_callback: function that returns a dict with all required data for rendering
        """
        self.stdscr = stdscr
        self.colours_start = colours_start
        self.get_state = get_state_function
        self.height = 0

    def draw(self, h, w):
        """
        Draw the footer. Must be implemented by subclasses.
        """
        raise NotImplementedError

class StandardFooter(Footer):
    def __init__(self, stdscr, colours_start, get_state_function):
        """
        stdscr: curses screen object
        colours_start: base colour pair index
        get_state_callback: function that returns a dict with all required data for rendering
        """
        self.stdscr = stdscr
        self.colours_start = colours_start
        self.get_state = get_state_function

        self.height = 2
        try:
            state = self.get_state()
            if "footer_string" in state and state["footer_string"]: self.height = 3
            else: self.height = 2
        except:
            logger.error("Error encountered when running StandardFooter.get_state")

        self.footer_string_y = 0
        self.picker_info_y = 1
        self.sort_info_y = 2
        self.sheets_y = 3
        self.files_y = 4
    def adjust_sizes(self, h, w):
        state = self.get_state()

        self.sheets_y=-1
        if state["footer_string"]:
            self.footer_string_y = h-1
            self.picker_info_y = h-3
            self.sort_info_y = h-2
            
            self.height = 3

        else:
            self.picker_info_y = h-2
            self.sort_info_y = h-1
            self.footer_string_y = -1
            self.height = 2

        if len(state["sheets"]) > 1:
            self.height += 1
            self.picker_info_y -= 1
            self.sort_info_y -= 1
            self.footer_string_y -= 1
            self.sheets_y = h-1

        if len(state["loaded_files"]) > 1 and state["loaded_file"] in state["loaded_files"]:
            self.height += 1
            self.picker_info_y -= 1
            self.sort_info_y -= 1
            self.footer_string_y -= 1
            self.sheets_y -= 1

            self.files_y = h-1

    def draw(self, h, w):
        state = self.get_state()
        # Fill background

        self.adjust_sizes(h, w)



        for i in range(self.height):
            self.stdscr.addstr(h-self.height+i, 0, ' '*(w-1), curses.color_pair(self.colours_start+20))

        if len(state["loaded_files"]) > 1 and state["loaded_file"] in state["loaded_files"]:

            sep = "◢ "
            files = [x.split("/")[-1] for x in state["loaded_files"]]
            filename = state["loaded_file"].split("/")[:-1]

            files_str = sep.join(files)
            files_str = files_str[:w-2]

            idx = state["loaded_file_index"]
            current_file_x = sum((len(x) for x in files[:idx])) + idx*len(sep)
            current_file_str = state["loaded_file"].split("/")[-1]
            current_file_x_end = current_file_x + len(current_file_str) + 2
            self.stdscr.addstr(self.files_y, 0, ' '*(w-1), curses.color_pair(self.colours_start+4))
            if current_file_x_end < w:

                self.stdscr.addstr(self.files_y, 0, f" {files_str}", curses.color_pair(self.colours_start+4))

                self.stdscr.addstr(self.files_y, current_file_x, f" {current_file_str}{sep[0]}", curses.color_pair(self.colours_start+4) | curses.A_REVERSE)
            else:
                files_str = sep.join(files)
                files_str = files_str[current_file_x_end-w:current_file_x_end][:w-2]
                self.stdscr.addstr(self.files_y, 0, f" {files_str}", curses.color_pair(self.colours_start+4))

                self.stdscr.addstr(self.files_y, w - (len(current_file_str)+3), f" {current_file_str}{sep[0]}", curses.color_pair(self.colours_start+4) | curses.A_REVERSE)

        if len(state["sheets"]) > 1:

            sep = "◢ "
            sheets = [x.split("/")[-1] for x in state["sheets"]]
            filename = state["sheet_name"].split("/")[:-1]

            sheets_str = sep.join(sheets)
            sheets_str = sheets_str[:w-2]

            idx = state["sheet_index"]
            current_sheet_x = sum((len(x) for x in sheets[:idx])) + idx*len(sep)
            current_sheet_str = state["sheet_name"].split("/")[-1]
            current_sheet_x_end = current_sheet_x + len(current_sheet_str) + 2
            self.stdscr.addstr(self.sheets_y, 0, ' '*(w-1), curses.color_pair(self.colours_start+4))
            if current_sheet_x_end < w:

                self.stdscr.addstr(self.sheets_y, 0, f" {sheets_str}", curses.color_pair(self.colours_start+4))

                self.stdscr.addstr(self.sheets_y, current_sheet_x, f" {current_sheet_str}{sep[0]}", curses.color_pair(self.colours_start+4) | curses.A_REVERSE)
            else:
                sheets_str = sep.join(sheets)
                sheets_str = sheets_str[current_sheet_x_end-w:current_sheet_x_end][:w-2]
                self.stdscr.addstr(self.sheets_y, 0, f" {sheets_str}", curses.color_pair(self.colours_start+4))

                self.stdscr.addstr(self.sheets_y, w - (len(current_sheet_str)+3), f" {current_sheet_str}{sep[0]}", curses.color_pair(self.colours_start+4) | curses.A_REVERSE)
                



        if state["footer_string"]:
            footer_string_width = min(w-1, len(state["footer_string"])+2)

            disp_string = f"{state["footer_string"][:footer_string_width]}"
            disp_string = f" {disp_string:>{footer_string_width-2}} "
            self.stdscr.addstr(self.footer_string_y, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(self.footer_string_y, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))

        


        if state["filter_query"]:
            self.stdscr.addstr(h - 2, 2, f" Filter: {state['filter_query']} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["search_query"]:
            self.stdscr.addstr(h - 3, 2, f" Search: {state['search_query']} [{state['search_index']}/{state['search_count']}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["user_opts"]:
            self.stdscr.addstr(h - 1, 2, f" Opts: {state['user_opts']} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)



        select_mode = "C"
        if state["is_selecting"]: select_mode = "VS"
        elif state["is_deselecting"]: select_mode = "VDS"
        if state["pin_cursor"]: select_mode = f"{select_mode} "
        # Cursor & selection info
        selected_count = sum(state["selections"].values())
        if state["paginate"]:
            # cursor_disp_str = f" [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])} | Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])//state['items_per_page']} | {select_mode}"
            cursor_disp_str = f" [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])} | Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])//state['items_per_page']} | {select_mode}"
        else:
            cursor_disp_str = f" [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])} | {select_mode}"

        # Maximum chars that should be displayed
        max_chars = min(len(cursor_disp_str)+2, w)
        self.stdscr.addstr(self.picker_info_y, w-max_chars, f"{cursor_disp_str:>{max_chars-2}} ", curses.color_pair(self.colours_start+20))


        # Sort info
        sort_column_info = f"{state['sort_column'] if state['sort_column'] is not None else 'None'}"
        sort_method_info = f"{state['SORT_METHODS'][state['columns_sort_method'][state['sort_column']]]}" if state['sort_column'] is not None else "NA"
        sort_order_info = "Desc." if state["sort_reverse"] else "Asc."
        sort_order_info = "▼" if state["sort_reverse"][state['sort_column']] else "▲"
        sort_disp_str = f" Sort: ({sort_column_info}, {sort_method_info}, {sort_order_info}) "
        max_chars = min(len(sort_disp_str)+2, w)
        self.stdscr.addstr(self.sort_info_y, w-max_chars, f"{sort_disp_str:>{max_chars-1}}", curses.color_pair(self.colours_start+20))

        self.stdscr.refresh()



class CompactFooter(Footer):
    def __init__(self, stdscr, colours_start, get_state_function):
        """
        stdscr: curses screen object
        colours_start: base colour pair index
        get_state_callback: function that returns a dict with all required data for rendering
        """
        self.stdscr = stdscr
        self.colours_start = colours_start
        self.get_state = get_state_function
        self.height = 1

    def adjust_sizes(self, h, w):
        pass

    def draw(self, h, w):
        state = self.get_state()

        # Fill background
        if state["search_query"]: self.height = 3
        elif state["filter_query"]: self.height = 2
        elif state["user_opts"]: self.height = 1
        elif state["footer_string"]: self.height = 2
        else: self.height = 1
        for i in range(self.height):
            self.stdscr.addstr(h-(i+1), 0, ' '*(w-1), curses.color_pair(self.colours_start+20))

        if state["user_opts"]:
            self.stdscr.addstr(h - 1, 2, f" Opts: {state['user_opts']} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["filter_query"]:
            self.stdscr.addstr(h - 2, 2, f" Filter: {state['filter_query']} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["search_query"]:
            self.stdscr.addstr(h - 3, 2, f" Search: {state['search_query']} [{state['search_index']}/{state['search_count']}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)

        right_width = 40
        # Sort info
        sort_column_info = f"{state['sort_column'] if state['sort_column'] is not None else 'None'}"
        sort_method_info = f"{state['SORT_METHODS'][state['columns_sort_method'][state['sort_column']]]}" if state['sort_column'] is not None else "NA"
        sort_order_info = "Desc." if state["sort_reverse"][state['sort_column']] else "Asc."
        sort_order_info = "▼" if state["sort_reverse"][state['sort_column']] else "▲"
        sort_disp_str = f" ({sort_column_info}, {sort_method_info}, {sort_order_info}) "
        # self.stdscr.addstr(h - 2, w-right_width, f"{sort_disp_str:>{right_width-1}}", curses.color_pair(self.colours_start+20))

        if state["footer_string"]:
            footer_string_width = min(w-1, len(state["footer_string"])+2)

            disp_string = f"{state["footer_string"][:footer_string_width]}"
            disp_string = f" {disp_string:>{footer_string_width-2}} "
            self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))
            selected_count = sum(state["selections"].values())
            if state["paginate"]:
                cursor_disp_str = f" {state['cursor_pos']+1}/{len(state['indexed_items'])}  Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])}  Selected {selected_count}"
            else:
                cursor_disp_str = f"{sort_disp_str} [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])}"
            self.stdscr.addstr(h-2, w-right_width, f"{cursor_disp_str:>{right_width-2}}"[:right_width-1], curses.color_pair(self.colours_start+20))
        else:
            # Cursor & selection info
            selected_count = sum(state["selections"].values())
            if state["paginate"]:
                cursor_disp_str = f" {state['cursor_pos']+1}/{len(state['indexed_items'])}  Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])}  Selected {selected_count}"
            else:
                cursor_disp_str = f"{sort_disp_str} [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])}"
            self.stdscr.addstr(h - 1, w-right_width, f"{cursor_disp_str:>{right_width-2}}"[:right_width-1], curses.color_pair(self.colours_start+20))

        self.stdscr.refresh()

class NoFooter(Footer):
    def __init__(self, stdscr, colours_start, get_state_function):
        """
        stdscr: curses screen object
        colours_start: base colour pair index
        get_state_callback: function that returns a dict with all required data for rendering
        """
        self.stdscr = stdscr
        self.colours_start = colours_start
        self.get_state = get_state_function
        self.height = 0

    def adjust_sizes(self, h, w):
        pass

    def draw(self, h, w):
        state = self.get_state()

        if state["search_query"]: self.height = 3
        elif state["filter_query"]: self.height = 2
        elif state["user_opts"]: self.height = 1
        elif state["footer_string"]: self.height = 1
        else: self.height = 0

        for i in range(self.height):
            self.stdscr.addstr(h-(i+1), 0, ' '*(w-1), curses.color_pair(self.colours_start+20))

        if state["user_opts"]:
            self.stdscr.addstr(h - 1, 2, f" Opts: {state['user_opts']} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["filter_query"]:
            self.stdscr.addstr(h - 2, 2, f" Filter: {state['filter_query']} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["search_query"]:
            self.stdscr.addstr(h - 3, 2, f" Search: {state['search_query']} [{state['search_index']}/{state['search_count']}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
            self.height = 3


        if state["footer_string"]:
            footer_string_width = min(w-1, len(state["footer_string"])+2)
            disp_string = f"{state["footer_string"][:footer_string_width]}"
            disp_string = f" {disp_string:>{footer_string_width-2}} "
            self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))
