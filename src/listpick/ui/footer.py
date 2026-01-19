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

        # Check for sheets: Use PickerState if available, else fall back to old system
        has_sheets = False
        picker_states = state.get("loaded_picker_states", [])
        picker_state_index = state.get("picker_state_index", 0)
        
        if picker_states and 0 <= picker_state_index < len(picker_states):
            current_state = picker_states[picker_state_index]
            has_sheets = len(current_state.sub_states) > 1
        elif len(state.get("sheets", [])) > 1:
            has_sheets = True
        
        if has_sheets:
            self.height += 1
            self.picker_info_y -= 1
            self.sort_info_y -= 1
            self.footer_string_y -= 1
            self.sheets_y = h-1

        # Check for multiple PickerStates/files
        # Priority: Use PickerStates if they exist, otherwise fall back to loaded_files
        has_multiple_states = False
        if picker_states:
            # PickerStates are present - use them as source of truth
            has_multiple_states = len(picker_states) > 1
        elif len(state.get("loaded_files", [])) > 1 and state.get("loaded_file") in state.get("loaded_files", []):
            # No PickerStates - fall back to old system
            has_multiple_states = True
        
        if has_multiple_states:
            self.height += 1
            self.picker_info_y -= 1
            self.sort_info_y -= 1
            self.footer_string_y -= 1
            self.sheets_y -= 1

            self.files_y = h-1
        if state["search_query"] and self.height < 3:
            self.height = 3


    def draw(self, h, w):
        state = self.get_state()
        # Fill background

        self.adjust_sizes(h, w)



        ## Clear background of footer rows
        for i in range(self.height):
            self.stdscr.addstr(h-self.height+i, 0, ' '*(w-1), curses.color_pair(self.colours_start+20))

        # Display loaded files/PickerStates
        picker_states = state.get("loaded_picker_states", [])
        
        # Use PickerStates if available (new system), otherwise fall back to old system
        if picker_states and len(picker_states) > 1:
            sep = "◢ "
            
            # Build display strings using get_footer_info()
            state_displays = []
            for ps in picker_states:
                info = ps.get_footer_info()
                display = info["display_name"] + info["modified_indicator"]
                state_displays.append(display)
            
            states_str = sep.join(state_displays)
            states_str = states_str[:w-2]
            
            idx = state.get("picker_state_index", 0)
            current_state_x = sum((len(x) for x in state_displays[:idx])) + idx*len(sep)
            current_state_str = state_displays[idx] if idx < len(state_displays) else "Unknown"
            
            current_state_x_end = current_state_x + len(current_state_str) + 2
            self.stdscr.addstr(self.files_y, 0, ' '*(w-1), curses.color_pair(self.colours_start+4))
            if current_state_x_end < w:
                self.stdscr.addstr(self.files_y, 0, f" {states_str}", curses.color_pair(self.colours_start+4))
                self.stdscr.addstr(self.files_y, current_state_x, f" {current_state_str}{sep[0]}", curses.color_pair(self.colours_start+4) | curses.A_REVERSE)
            else:
                states_str = sep.join(state_displays)
                states_str = states_str[current_state_x_end-w:current_state_x_end][:w-2]
                self.stdscr.addstr(self.files_y, 0, f" {states_str}", curses.color_pair(self.colours_start+4))
                self.stdscr.addstr(self.files_y, w - (len(current_state_str)+3), f" {current_state_str}{sep[0]}", curses.color_pair(self.colours_start+4) | curses.A_REVERSE)
        
        # LEGACY: Fall back to old file display logic
        elif len(state["loaded_files"]) > 1 and state["loaded_file"] in state["loaded_files"]:

            sep = "◢ "

            # Use FileState objects if available, otherwise fall back to paths
            file_states = state.get("loaded_file_states_new", [])
            if file_states:
                # Build file names from FileState objects with modified indicator
                files = [
                    fs.display_name + (" *" if fs.is_modified else "")
                    for fs in file_states
                ]
            else:
                # Fallback to old behavior
                files = [x.split("/")[-1] for x in state["loaded_files"]]

            filename = state["loaded_file"].split("/")[:-1]

            files_str = sep.join(files)
            files_str = files_str[:w-2]

            idx = state["loaded_file_index"]
            current_file_x = sum((len(x) for x in files[:idx])) + idx*len(sep)

            # Get current file display name with modified indicator
            if file_states and idx < len(file_states):
                current_file_state = file_states[idx]
                current_file_str = current_file_state.display_name + (" *" if current_file_state.is_modified else "")
            else:
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

        # Display sheets/sub-states
        picker_states = state.get("loaded_picker_states", [])
        picker_state_index = state.get("picker_state_index", 0)
        
        # Use PickerState sub_states if available
        if picker_states and 0 <= picker_state_index < len(picker_states):
            current_state = picker_states[picker_state_index]
            
            if len(current_state.sub_states) > 1:
                sep = "◢ "
                
                # Build sheet display strings
                sheets = [sub.display_name for sub in current_state.sub_states]
                idx = current_state.sub_state_index
                
                sheets_str = sep.join(sheets)
                sheets_str = sheets_str[:w-2]
                
                current_sheet_x = sum((len(x) for x in sheets[:idx])) + idx*len(sep)
                current_sheet_str = sheets[idx] if idx < len(sheets) else "Unknown"
                
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
        
        # LEGACY: Fall back to old sheet display
        elif len(state.get("sheets", [])) > 1:

            sep = "◢ "

            # Try to use SheetState objects from FileState if available
            file_states = state.get("loaded_file_states_new", [])
            file_idx = state.get("loaded_file_index", 0)

            # Always use state["sheet_index"] as the source of truth
            idx = state["sheet_index"]

            if file_states and file_idx < len(file_states) and len(file_states[file_idx].sheets) > 0:
                current_file_state = file_states[file_idx]
                # Use sheet names from FileState.sheets
                sheets = [sheet.display_name for sheet in current_file_state.sheets]
            else:
                # Fallback to old behavior - handle both strings and objects
                raw_sheets = state["sheets"]
                if raw_sheets and hasattr(raw_sheets[0], 'name'):
                    # sheets are SheetState objects
                    sheets = [s.name for s in raw_sheets]
                else:
                    # sheets are strings
                    sheets = [x.split("/")[-1] if isinstance(x, str) else str(x) for x in raw_sheets]

            filename = state["sheet_name"].split("/")[:-1]

            sheets_str = sep.join(sheets)
            sheets_str = sheets_str[:w-2]

            current_sheet_x = sum((len(x) for x in sheets[:idx])) + idx*len(sep)

            if file_states and file_idx < len(file_states) and idx < len(file_states[file_idx].sheets):
                current_sheet_str = file_states[file_idx].sheets[idx].display_name
            else:
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

            disp_string = f"{state['footer_string'][:footer_string_width]}"
            disp_string = f" {disp_string:>{footer_string_width-2}} "
            self.stdscr.addstr(self.footer_string_y, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(self.footer_string_y, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))

        


        if state["filter_query"]:
            self.stdscr.addstr(h - 2, 2, f" Filter: {state['filter_query']} "[:w-40], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["search_query"]:
            self.stdscr.addstr(h - 3, 2, f" Search: {state['search_query']} [{state['search_index']}/{state['search_count']}] "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)
        if state["user_opts"]:
            self.stdscr.addstr(h - 1, 2, f" Opts: {state['user_opts']} "[:w-3], curses.color_pair(self.colours_start+20) | curses.A_BOLD)




        ## Cursor selection mode
        select_mode = "C"
        if state["is_selecting"]: select_mode = "VS"
        elif state["is_deselecting"]: select_mode = "VDS"
        if state["pin_cursor"]: select_mode = f"{select_mode} "

        # Cursor & selection info
        selected_count = sum(state["selections"].values())
        if state["paginate"]:
            cursor_disp_str = f" [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])} | Page {state['cursor_pos']//state['items_per_page']}/{len(state['indexed_items'])//state['items_per_page']} | {select_mode}"
        else:
            # cursor_disp_str = f" [{selected_count}] {state['cursor_pos']+1},{state['selected_column']}/{len(state['indexed_items'])},{len(state['column_widths'])} | {select_mode}"
            if state["cell_cursor"]:
                cursor_disp_str = f" [{selected_count}] {state['cursor_pos']+1}/{len(state['indexed_items'])} | {state['selected_column']}/{len(state['column_widths'])} | {select_mode}"
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

        # self.stdscr.refresh()



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

            disp_string = f"{state['footer_string'][:footer_string_width]}"
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
            disp_string = f"{state['footer_string'][:footer_string_width]}"
            disp_string = f" {disp_string:>{footer_string_width-2}} "
            self.stdscr.addstr(h - 1, w-footer_string_width-1, " "*footer_string_width, curses.color_pair(self.colours_start+24))
            self.stdscr.addstr(h - 1, w-footer_string_width-1, f"{disp_string}", curses.color_pair(self.colours_start+24))
