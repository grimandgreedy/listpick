"""

if self.show_footer:
    # Fill background
    self.stdscr.addstr(h-3, 0, ' '*(w-1), curses.color_pair(self.colours_start+20))
    self.stdscr.addstr(h-2, 0, ' '*(w-1), curses.color_pair(self.colours_start+20))
    self.stdscr.addstr(h-1, 0, ' '*(w-1), curses.color_pair(self.colours_start+20)) # Problem with curses that you can't write to the last char

    if self.filter_query:
        self.stdscr.addstr(h - 2, 2, f" Filter: {self.filter_query} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
    if self.search_query:
        self.stdscr.addstr(h - 3, 2, f" Search: {self.search_query} [{self.search_index}/{self.search_count}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
    if self.user_opts:
        self.stdscr.addstr(h-1, 2, f" Opts: {self.user_opts} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
    # Display sort information
    sort_column_info = f"{self.sort_column if self.sort_column is not None else 'None'}"
    sort_method_info = f"{self.SORT_METHODS[self.columns_sort_method[self.sort_column]]}" if self.sort_column != None else "NA"


    ## RIGHT
    # Sort status
    sort_order_info = "Desc." if self.sort_reverse[self.sort_column] else "Asc."
    sort_disp_str = f" Sort: ({sort_column_info}, {sort_method_info}, {sort_order_info}) "
    self.stdscr.addstr(h - 2, w-35, f"{sort_disp_str:>34}", curses.color_pair(self.colours_start+20))


    if self.footer_string:
        # footer_string_width = min(w, max(len(self.footer_string), w//3, 39))
        footer_string_width = min(w-1, max(len(self.footer_string), 50))
        disp_string = f"{self.footer_string[:footer_string_width]:>{footer_string_width-1}} "
        self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
        self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))
    else:
        # Display cursor mode
        select_mode = "Cursor"
        if self.is_selecting: select_mode = "Visual Selection"
        elif self.is_deselecting: select_mode = "Visual deselection"
        self.stdscr.addstr(h - 1, w-35, f"{select_mode:>33} ", curses.color_pair(self.colours_start+20))
    # Display selection count
    selected_count = sum(self.selections.values())
    if self.paginate:
        cursor_disp_str = f" {self.cursor_pos+1}/{len(self.indexed_items)}  Page {self.cursor_pos//self.items_per_page + 1}/{(len(self.indexed_items) + self.items_per_page - 1) // self.items_per_page}  Selected {selected_count}"
        self.stdscr.addstr(h - 3, w-35, f"{cursor_disp_str:>33} ", curses.color_pair(self.colours_start+20))
    else:
        cursor_disp_str = f" {self.cursor_pos+1}/{len(self.indexed_items)}  |  Selected {selected_count}"
        self.stdscr.addstr(h - 3, w-35, f"{cursor_disp_str:>33} ", curses.color_pair(self.colours_start+20))

    self.stdscr.refresh()
elif self.footer_string:
    footer_string_width = min(w-1, len(self.footer_string)+2)
    disp_string = f" {self.footer_string[:footer_string_width]:>{footer_string_width-2}} "
    self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
    self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))

## Display infobox
if self.display_infobox:
    self.infobox(self.stdscr, message=self.infobox_items, title=self.infobox_title)
    # self.stdscr.timeout(2000)  # timeout is set to 50 in order to get the infobox to be displayed so here we reset it to 2000
"""



import curses

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
        self.height = 3

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
        self.height = 3
    def draw(self, h, w):
        state = self.get_state()

        # Fill background
        for i in range(3):
            self.stdscr.addstr(h-3+i, 0, ' '*(w-1), curses.color_pair(self.colours_start+20))

        if state["filter_query"]:
            self.stdscr.addstr(h - 2, 2, f" Filter: {state['filter_query']} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["search_query"]:
            self.stdscr.addstr(h - 3, 2, f" Search: {state['search_query']} [{state['search_index']}/{state['search_count']}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["user_opts"]:
            self.stdscr.addstr(h - 1, 2, f" Opts: {state['user_opts']} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)

        # Sort info
        sort_column_info = f"{state['sort_column'] if state['sort_column'] is not None else 'None'}"
        sort_method_info = f"{state['SORT_METHODS'][state['columns_sort_method'][state['sort_column']]]}" if state['sort_column'] is not None else "NA"
        sort_order_info = "Desc." if state["sort_reverse"] else "Asc."
        sort_order_info = "▼" if state["sort_reverse"][state['sort_column']] else "▲"
        sort_disp_str = f" Sort: ({sort_column_info}, {sort_method_info}, {sort_order_info}) "
        self.stdscr.addstr(h - 2, w-35, f"{sort_disp_str:>34}", curses.color_pair(self.colours_start+20))

        if state["footer_string"]:
            footer_string_width = min(w-1, max(len(state["footer_string"]), 50))
            disp_string = f"{state['footer_string'][:footer_string_width]:>{footer_string_width-1}} "
            self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))
        else:
            select_mode = "Cursor"
            if state["is_selecting"]: select_mode = "Visual Selection"
            elif state["is_deselecting"]: select_mode = "Visual deselection"
            self.stdscr.addstr(h - 1, w-35, f"{select_mode:>33} ", curses.color_pair(self.colours_start+20))

        # Cursor & selection info
        selected_count = sum(state["selections"].values())
        if state["paginate"]:
            cursor_disp_str = f" {state['cursor_pos']+1}/{len(state['indexed_items'])}  Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])}  Selected {selected_count}"
        else:
            cursor_disp_str = f" {state['cursor_pos']+1}/{len(state['indexed_items'])}  |  Selected {selected_count}"
        self.stdscr.addstr(h - 3, w-35, f"{cursor_disp_str:>33} ", curses.color_pair(self.colours_start+20))

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
        self.height = 2
    def draw(self, h, w):
        state = self.get_state()

        # Fill background
        for i in range(1):
            self.stdscr.addstr(h-(i+1), 0, ' '*(w-1), curses.color_pair(self.colours_start+20))

        if state["filter_query"]:
            self.stdscr.addstr(h - 2, 2, f" Filter: {state['filter_query']} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["search_query"]:
            self.stdscr.addstr(h - 3, 2, f" Search: {state['search_query']} [{state['search_index']}/{state['search_count']}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["user_opts"]:
            self.stdscr.addstr(h - 1, 2, f" Opts: {state['user_opts']} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)

        right_width = 40
        # Sort info
        sort_column_info = f"{state['sort_column'] if state['sort_column'] is not None else 'None'}"
        sort_method_info = f"{state['SORT_METHODS'][state['columns_sort_method'][state['sort_column']]]}" if state['sort_column'] is not None else "NA"
        sort_order_info = "Desc." if state["sort_reverse"][state['sort_column']] else "Asc."
        sort_order_info = "▼" if state["sort_reverse"][state['sort_column']] else "▲"
        sort_disp_str = f" ({sort_column_info}, {sort_method_info}, {sort_order_info}) "
        # self.stdscr.addstr(h - 2, w-right_width, f"{sort_disp_str:>{right_width-1}}", curses.color_pair(self.colours_start+20))

        if state["footer_string"]:
            footer_string_width = min(w-1, max(len(state["footer_string"]), 50))
            disp_string = f"{state['footer_string'][:footer_string_width]:>{footer_string_width-1}} "
            self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(h - 2, w-right_width, f"{cursor_disp_str:>{right_width-2}}"[:right_width-1], curses.color_pair(self.colours_start+20))
        else:
            # Cursor & selection info
            selected_count = sum(state["selections"].values())
            if state["paginate"]:
                cursor_disp_str = f" {state['cursor_pos']+1}/{len(state['indexed_items'])}  Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])}  Selected {selected_count}"
            else:
                cursor_disp_str = f"{sort_disp_str} [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])}"
            self.stdscr.addstr(h - 1, w-right_width, f"{cursor_disp_str:>{right_width-2}}"[:right_width-1], curses.color_pair(self.colours_start+20))

        self.stdscr.refresh()
