# TODO for list_picker.py

> [!IMPORTANT] Features
> - [x] Generate data based on commands in input file
>   - [ ] Add support for python commands in addition to bash.
> - [x] Add ability to list_picker current state to file.
>     - [x]  selected column, sort method, etc.
> - [x] Add ability to dump current view to file.
>   - [x] pickle
>   - [x] add other formats
>     - [x] csv, tsv
>     - [x] json
>     - [x] parquet
>     - [x] msgpack
>     - [x] feather
> - [x] Dump current state to file.
>   - [ ] Can't pickle refresh function if it uses libraries not included in list_picker
> - [x] Create notification system
>    - [ ] add transient non-blocking notifications
> - [x] Copy selected frows to clipboard
>   - [x] Add copy selection box with options
>   - [x] Copy rows with different representations
>     - [x] python representation
>     - [x] csv and tsv representation
>     - [x] value_sv representation with value passed as opt
>     - [x] include/exclude hidden columns
>     - [ ] copy what is visible in selected rows
> - [ ] Modes
>   - [x] Allow filtering in mode
>   - [x] Display modes
>   - [ ] Search
>   - [ ] ...
> - [x] add different selection styles
>   - [x] row highlighted   
>   - [x] selection indicator (selection char at end of line)
> - [x] Add help screen
>   - [ ] Generate help screen based on keys dict
> - [ ] add key-chain support. Can use the timeout to clear the key.
>   - [ ] gg
>   - [ ] count
> - [ ] add return value; e.g., refreshing
> - [ ] add indexed columns
>   - [ ] will fix highlighting when column order is switched
> - [ ] adjust width of particular columns
> - [ ] merge columns
> - [ ] show/hide col based on name; have tab auto complete
> - [ ] add option for padding/border
>   - [ ] stdscr.box??
> - [ ] add key to go to next dissimilar value in column
>   - [ ] e.g., select column 2 (download: complete), and pressing tab will go to the next entry that is not complete 
> - [ ] when column is selected try best guess search method
> - [x] add registers to input field
> - [x] Add keys_dict to support remapping of keys
>   - [x] Separate keys for:
>     - [x] notifications
>     - [x] options
>     - [x] menu
> - [x] Add load data dialog
>   - [ ] Open yazi and allow file to be chosen.
>   - [ ] Load full state from running list_picker instance
>   - [ ] Complete load_function_data function
>   - [ ] Add more formats:
>     - [ ] csv, tsv
>     - [x] pickle
>     - [ ] msgpack
>     - [ ] feather
>     - [ ] parquet
>     - [ ] json
> - [ ] Merge data sets/look at two datasets at once





> [!Important] Improvements
> - [ ] (!!!) Need to remove nonlocal args and pass all variables as arguments
> - [ ] change hidden_columns from set() to list()
> - [ ] make unselectable_indices work with filtering
> - [ ] look at adjustment for cursor position and hidden unselectable indices
> - [ ] each time we pass options it will resort and refilter; add an option to simply load the items that are passed
> - [ ] require_option should skip the prompt if an option has already been given
> - [ ] force option type; show notification to user if option not appropriate
> - [ ] add the ability to disable options for:
>   - [x] show footer
>   - [x] auto-refresh
>   - [x] edit cell
>   - [ ] sort
>   - [ ] visual selection
>   - [ ] disable visual selection when # is greater than max_selected
>   - [ ] NOTIFICATIONS
>   - [ ] OPTIONS
> - [ ] Colours
>   - [ ] Redo colours
>   - [ ] pass colours to list_picker in a more intuitive way
>   - [ ] complete get_colours loop
>   - [?] we have arbitrarily set application colours to be 0-50, notification 50-100 and help 100-150
> - [ ] make infobox variable in size and position 
> - [ ] break draw_screen() into functions
> - [ ] input_field
>      - [ ] implement readline keybinds
>          - [x] ctrl-f, ctrl-b
>      - [ ] add variable max display length
> - [ ] Highlights
>   - [ ] (!!!) there is a difference between search matches and highlights because the highlights operate on what is displayed
>      - [?] allow visual matches with searches?
>      - [?] hide highlights across fields?
>      - [?] e.g., mkv$ shows no highlights but does match
>   - [ ]  - e.g., wmv$ shows no matches but --3 wmv$ shows matches
> - [ ] Pipe
>   - [ ] if no items are selected pipe cursor to command
> - [ ] Redo keybinds
>   - [ ]  n/N search next/prev
>   - [ ] (!!!) allow key remappings; have a dictionary to remap
>      - [ ] escape should close option selections and notifications
>   - [ ] Add keybind to focus on next (visible) column
> - [ ] (?) adjust default column width based on current page?
> - [ ] Need to set environment variables somehow.
>   - [ ] cwd
> - [ ] Make time sort work with formats like: 
>   - [ ] '42 min 40 s'
> - [ ] Add no-select mode which will look better for notifications, options and menus
> - [ ] Unify in-app load and command-line input file
> - [ ] Create list of errors encountered when generating data and output to file if user requests...



> [!Bug] Bugs
> - [ ] fix resizing when input field active
>   - [ ] Remap resize in keymaps and return "refresh" in the opts 
> - [ ] Visual selection
>   - [ ] when visually selecting sometimes single rows above are highlighted (though not selected)
> - [ ] weird alignment problem with certain characters
>   - [x] Chinese characters
>   - [x] Korean characters
>   - [x] Japanese characters
>   - [ ] Problems with the following:
>       - ： 
> - [ ] moving columns:
>   - ruins highlighting
>   - is not preserved in function_data
>   - implement indexed_columns
>   - will have to put header in function_data to track location of fields
> - [ ] regexp and field entry errors
>   - [ ] filter
>   - [ ] "--1 error .*" doesn't work but ".* --1" error does
>   - [ ] search
>   - [ ] highlights
>   - [x] when +,* is added to the filter it errors out
>   - [ ] some capture groups don't work [^0]
>   - [ ] should general search be cell-wise?
>   - [ ] option to search visible columns only
> - [ ] Visual selection: start visual selection on row 100. List_picker refreshes and there are only 10 rows with the applied filter. End visual selection on row 2. Crash
> - [ ] blinking cursor character shows after opening nvim and returning to listpicker
>    - Not sure if this can be avoided. 
>       - In alacritty it always shows the cursor
>       - In kitty it shows only after opening nvim
> - [x] The backspace key is not registered in the input field when the cursor is in the options box. The keys work in the main application and in help but not in the options box list_picker...
>   -  [x] No idea why but the keycode for backspace is 263 in the main window but in curses.newwin the backspace keycode is 127
>   - Had to set submenu_win.keypad(True) for the submenu window as well as the main window. It doesn't seem to inherit the parent window's properties
> - [x] Last character on header string doesn't show if header value for that cell is longer than all entries in that column
>   - [x] have to +1 to total visible column width
> - [x] If require option is given and the box is empty then we should exit the input field without returning the index
> - [ ] Sometimes the variables from one menu remain in the other in aria2tui... weird
> - [ ] When loading a pickled file from aria2tui we get a crash because there are more lines in the data.
>   - [ ] Reset other variables when loading data?






> - [!IMPORTANT] Done (assorted)
> - [x] make filter work with regular expressions
> - [x] Make escape work with opts (as it does with pipe and filter)
> - [x] adjust page after resize
> - [x] fix not resizing properly
> - [x] fix header columns not being aligned with certain input (fixed by replacing tabs with spaces so char count clipped properly)
> - [x] rows not aligned with chinese characters (need to trim display rows based on wcswidth)
> - [x] fix problems with empty lists both [] and [[],[]] 
> - [x] fix issue where item when filtering the cursor goes to a nonexistent item
> - [x] add unselectable_indices support for filtered rows and visual selection
> - [x] allow a keyword match for colours in columns (error, completed)
> - [x] fix time sort
> - [x] add colour highlighting for search and filter
> - [x] fix highlights when columns are shortened
> - [x] highlights wrap on bottom row
> - [x] Search
>    - [x] add search count
>    - [x] add option to continue search rather than finding all matches every time
>    - [x] problem when filter is applied
> - [x] Visual selection
>    - [x] (!!!) Fix visual selection in the entries are sorted differently.
>    - [x] when filtered it selects entries outside of those visible and throws an error
> - [x] add config file
> - [x] Highlights
>    - [x] add highlight colour differentiation for selected and under cursor
>    - [x] remain on same row when sorting (23-5-25)
>    - [x] add option to stay on item when sorting
> - [x] fix highlighting when cols are hidden
> - [x] Add hidden columns to function so that they remain hidden on refresh
> - [x] Fix the position of a filter and options when terminal resizes
> - [x] fix the filtering so that it works with more than one arg
> - [x] fix error when filtering to non-existing rows
> - [x] implement settings:
>      - [x] !11 show/hide 11th column
>      - [x] ???
> - [x] Allow state to be restored
>    - [x] allow search/filter to be passed to list_picker so that search can resume
>    - [x] cursor postion (x)
>    - [x] page number
>    - [x] sort
>    - [x] filter state
>    - [x] search
>    - [x] show/hide cols
> - [x] implement scroll as well as page view
> - [x] why the delay when pressing escape to cancel selection, remove filter, search, etc.
>    - [x] the problem is that ESCDELAY has to be set
> - [x] (!!!) high CPU usage
>    - [x] when val in `stdscr.timeout(val)` is low the cpu usage is high
> - [x] (!!!) When the input_field is too long the application crashes
> - [x] crash when selecting column from empty list
> - [x] sendReq()...
> - [x] add tabs for quick switching
> - [x] add header for title
> - [x] add header tabs
> - [x] add colour for active setting; e.g., when filter is being entered the bg should be blue
> - [x] check if mode filter in query when updating the query and if not change the mode
> - [x] when sorting on empty data it throws an error
> - [x] hiding a column doesn't hide the corresponding header cell
> - [x] add colour for selected column
> - [x] highlighting doesn't disappear when columns are hidden
> - [x] add scroll bar
> - [x] (!!!) fix crash when terminal is too small
> - [x] add option to start with X rows already selected (for watch active selection)
> - [x] prevent overspill on last row
> - [x] redo help
>    - [x] help screen doesn't adjust when terminal resized
>    - [x] add search/filter on help page
>    - [x] use list_picker to implement help
> - [x] +/- don't work when using scroll (rather than paginate)
> - [x] flickering when "watching"
> - [x] change the cursor tracker from current_row, current_page to current_pos
> - [x] add flag to require options for a given entry
> - [x] option to number columns or not
> - [x] make sure `separator` works with header
> - [x] add cursor when inputing filter, opts, etc.
> - [x] remain on same row when resizing with +/-


> [!error] Errors
> - [ ] Crash: place cursor on last row and hold + when entries > items_per_page
>   - [ ] Does it even need the +/- functionality any more?
> - [ ] why does curses crash when writing to the final char on the final line?
>   - [ ] is there a way to colour it?
> - [ ] errors thrown when length(header) != length(items[0])
> - [ ] Error handling needed
>   - [ ] apply_settings("sjjj") 
> - [ ] Error when drawing highlights. Have to put them in a try-except block
> - [ ] Add error-checking for:
>   - [ ] displaying modes... 
> - [x] Crash on the display header section of draw_screen when we have a column selected and we resize that column out of the frame


> # [!WARNING] Add docstrings
> - [x] aria2_detailing
> - [x] aria2c_utils
> - [x] aria2c_wrapper
> - [x] aria2tui
> - [x] aria_adduri
> - [x] clipboard_operations
> - [x] filtering
> - [x] help_screen
> - [x] input_field
> - [x] keys
> - [x] list_picker
> - [x] list_picker_colours
> - [x] searching
> - [x] sorting
> - [x] table_to_list_of_lists
> - [x] utils
