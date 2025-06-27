# CHANGELOG.md

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
