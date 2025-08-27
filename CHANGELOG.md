# CHANGELOG.md
Note that the changes between 0.1.11.0 and 1.1.12.0 are listed under 0.1.11

## [0.1.15.3] 2025-07-27
 - Added error checking when setting the cursor_pos_id in fetch_data.

## [0.1.15.1] 2025-07-27
 - Added key to toggle right pane.
 - Improved appearance of help screen.

## [0.1.15.0] 2025-07-27
 - Feature added: support for dynamic data display in a right pane.
 - Bugs fixed:
   - Fixed ipython not working when data is piped into the picker.

## [0.1.14.0] - [0.1.14.14] 2025-08-24
 - Added info screen to display all information on the running Picker.
 - Added keys for file_next and file_prev
 - Added __sizeof__() function for the Picker class.
 - Fixed rows resizing twice when opening/switching between some files.
 - Added to settings: goto row, goto column
 - NaN replaced with empty string when loading empty cells from xlsx or ods files.
 - Added Picker.get_config(path) method.
 - Can now take input on stdin -- e.g., `du -h | listpick --stdin`
 - We now get user input via '/dev/tty' rather than stdscr.getch() (which uses stdin). 
   - This was necessary to ensure that we can pipe data in via stdin and still receive user input.
 - Bugs fixed:
   - Closing files causes issues switching between files.
   - Fixed crash when loading non-existent config file.
   - Fixed highlighted cell not being aligned in the way that we expect.
   - Fixed search query covering last row of data.
   - Discovered missing keys from colour_theme 0 which caused menus not to be displayed.
   - Setting colour_theme_number in the config now works.
 - Create ~/.config/listpick directory for storing input history if it doesn't already exist.
 - Added error checking when opening files.
 - Added --headerless flag to prevent interpreting the first line of the input as the header.
 - Fixed special keys not working:
   - arrow keys (main picker, input_field)
   - meta+key (input_field, main picker)
 - Added column number to footer
 - Improved splitting of whitespace separated data passed on stdin.
 - Ensured that main picker elements resize if the terminal is resized when other dialogues are in focus: notifications, options, settings.
 - Added method to check for terminal resize.
   - Was necessary since we are no longer using getch from curses so we can't test whether getch() == curses.KEY_RESIZE.
 - Added Alt+keys in build_help.

## [0.1.14] 2025-08-20
 - Fixed bug when cells are centred vertically.
 - Added "level" keyword for highlight dictionary.
  - l0: show highlight above base rows
  - l1: show highlight above selected cells/rows
  - l2: show highlight above cursor cell/row.
 - Added separate selected_column argument (distinct from sort_column) so that columns can be navigated without sorting on the selected column. 's' has to be pressed on the selected_column to trigger sorting.
 - Changed scrolling to start/end so that it selects the first/last column.
 - Bug fixes:
   - When data was centred vertically it would take an extra draw_screen loop to determine the proper column widths when the column sizes changed. This has been fixed.
   - Refreshing sorted data would resort it on the selected column rather than the sort column. Fixed.
   - Fixed error when padding uneven lists when a list of strings is passed instead of a list of lists.
   - Fixed crash when showing certain notifications. The notification message was not being split into lines properly.
   - Fixed wrong page number in the footer when paginate=True.
 - Added some extra options to the settings:
   - Toggle header
   - Toggle row header
   - Toggle modes
   - Add/insert blank row
   - Add/insert blank column
 - Added splash screen to picker which can be displayed when loading a large data set, for example.
 - Ensured that the curses colour pairs are redefined if we are loading from a picker save state.
 - Added functions to insert an empty row/column at an an arbitrary position in the picker items.
 - Adjusted the commandline arguments so that the filename can be passed without the -i flag.
 - If no input file type is specified on the command line it will now guess based on the input file's extension.
 - Improved display of cells/rows with various unicode characters. It is much better but there are still some problems with alignment and highlighting.
 - Setup logging for the Picker class. Currently still very basic but will track to the last function that was run before crash if the --debug flag is passed to the picker.
 - Added pin_cursor options which keeps the cursor on the same row during a refresh rather than tracking the id of the highlighted row. 
 - Updated StandardFooter. Now shows information on two lines rather than three; all cursor and selection information on the first line and the sort information on the second. Cursor, Visual (de)selection now abreviated to C, VS, and VDS.
 - Added try-except wrapper to draw_screen function to prevent crashes during rapid resizing.
 - Speed improvements:
   - Create and track self.selected_cells_by_row when selections change rather than derive it from the self.cell_selections
     - Much faster with very large data sets as we need to determine selected_cells_by_row every time we run self.draw_screen()
 - We can now pipe data from cells in multiple columns to a command.
   - e.g., pipe two cols to gnuplot
 - Features added:
   - Listpick now supports multiple open files.
     - 'file_next' setting
   - Listpick now supports files with multiple sheets.
     - 'sheet_next' setting
 - Fixed error when opening xlsx files.
 - Can now open multiple files from the command line: listpick -i file1.csv, file2.csv

## [0.1.13] 2025-07-28
 - Cell-based picker is now supported.
   - Cell-wise navigation.
   - Cell-wise selection.
   - Cell-wise copying.
   - Cell-wise pasting.
 - Pasting cells a picker is now supported
 - Added footer_style class variable which can be given to select the footer style. Currently supports StandardFooter, CompactFooter, and NoFooter.
 - Fixed bug which showed a distorted footer when the footer string was one char longer than the width of the terminal.
 - Can now display a left-justified column indicating the row numbers (show_row_header)
 - Selecting column to the left or right now scrolls the selected column into view.
 - Input field autocompletion significantly improved.
   - Now shows popup list showing the next autocomplete suggestions
   - Supports auto-completing any words passed to the auto_complete_words argument of the input_field function
     - Search and filter autocomplete any words in the items of the picker by default.
   - Supports auto-complete functions %time and %date
   - Supports auto-complete formulae.
     - Will allow formulae filling at a later date.
   - Can now edit input_field string in nvim by pressing ctrl+x
 - Added functionality to add (empty) rows after the cursor and add (empty) columns after the cursor.

## [0.1.12] 2025-07-25
 - The Picker now supports different footer options. Three options have been added:
   - StandardFooter
   - CompactFooter
   - NoFooter
 - Added input field history for search and filter, pipe, settings, and opts. 
 - Fixed instacrash when a terminal doesn't have 8bit colour support.
 - Created a fallback colour theme for terminals with < 256 colours available.
 - Fixed bug when scrollbar doesn't show with several thousand entries. Ensured it is always at least 1 character high.
 - Fixed colour configuration errors on some terminals by setting curses.use_default_colours().
 - Added save and load history functions.
 - Can now load full Picker from pickled save state.
 - Fixed size of option-picker dialogue.
 - Added the ability to add highlights from the settings input.
   - hl,.*,3,8: highlight field 3
 - Can now select theme with th# in settings; th still cycles as before.

## [0.1.11] 2025-07-13
 - Greatly improved the input_field
   - Implemented path auto-completion with tab/shift+tab
   - History can be passed to the input field
   - Implemented a kill-ring
   - Can paste into the input_field
   - Implemented more readline keybinds:
     - Alt+w: delete to word-separator character (' ' or '/')
     - Alt+f: forwards one word
     - Alt+b: backwards one word
     - Ctrl+g: exit
     - Ctrl+y: Yank from the top of the kill ring
     - Alt+y: Yank from the kill ring. As is typical, this only works after a yank.
     - Ctrl+n: Cycle forwards through history
     - Ctrl+p: Cycle backwards through history
   - Now accepts curses colour pair to set colours.
 - Fixed bug where searching with a lot of matches causes slow down.
 - 

## [0.1.10] 2025-07-04
 - Help is now *built* (rather than simply displaying help text) using the active keys_dict and so only shows keys that function in the current Picker object. 

## [0.1.9] 2025-07-04
 - Added asynchronous data refresh requests using threading.

## [0.1.8] 2025-07-03
 - Added left-right scrolling using h/l.
 - Scroll to home/end with H/L.
 - Fixed header columns not being aligned when len(header)>10.

## [0.1.7] 2025-07-02
 - Added row-wise highlighting.
 - Added MIT license information.

## [0.1.6] 2025-07-01
 - Fixed footer_string not displaying immediately if passed with a refresh function.

## [0.1.5] 2025-06-29
 - Renamed list_picker listpick.
 - Restructured project and added it to pypi so that it can be intalled with pip. 
 - Modified dependencies so that the dependencies required for loading/saving--pandas, csv, openpyxl, etc.--are only installed with `python -m pip install listpick[full]`."
  - `python -m pip install listpick` will install all run-time dependencies outside of those used for saving data.

## [0.1.4] 2025-06-27
 - Added more themes: blue and purple.
 - Added an a key dict which will work well with data passed in to be edited--e.g., settings.
 - Column width is now determined by the width of the visible data rather than all data in the column.
 - Notifications and options-picker can be exited with escape.

## [0.1.3] 2025-06-19
 - Fixed bug where list_picker crashed when rapidly resizing terminal or rapidly changing font-size.
 - Fixed bug with filtering/searching where multiple tokens could not be specified for the same column.
 - Visual improvements:
   - Changed the footer colour to match the title bar in the main theme.
   - Right aligned the elements in the footer
   - Improved the appearance of the refresh indicator.
 - Pickle files can now be loaded from the command line in addition to being able to be loaded wile running the Picker.

## [0.1.2] 2025-06-18
 - Added the ability to edit current instance of Picker in ipython when Ctrl+e is pressed.
 - Quick-toggle footer with '_'.

## [0.1.1] 2025-06-18
 - Added a footer string function which can be auto refreshed with a given function.

## [0.1.0] 2025-06-17
 - CHANGELOG created
 - Converted the underlying Picker from a function into a class.
