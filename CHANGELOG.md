# CHANGELOG.md
## [0.1.13] 2025-??
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
 - Added cell_cursor option which displays a highlighted cursor on a cell (rather than the whole row being highlighted).
 - Added functionality to add rows after the cursor and add columns after the cursor.

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
