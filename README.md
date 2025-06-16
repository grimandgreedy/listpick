# list_picker

A TUI tool to select from a list of items using keyboard navigation. Items can come from various formats including text files (tsv, csv), JSON, XLSX, ODS, or directly from standard input. Rows of data can be viewed, selected, generated, saved, loaded, refreshed, modified or copied to the clipboard. Can be used as a standalone data viewer and generator or as a backend for a TUI application.

**NOTE**: list_picker is still in development.

# Quickstart

```
git clone https://github.com/grimandgreedy/list_picker

cd list_picker && python -m pip install -r requirements.txt

python list_picker.py -g ./examples/list_files.py
```

## Overview

The application allows you to:
- Select multiple items from different file types and input streams
- Delete individual items
- Highlight specific items for quick selection
- Filtering: supports regular expressions for row- and column-based filtering.
- Searching: supports regular expressions for row- and column-based searching.
- Sort data based on specified columns and sort-type
- Save and load data.
- Copy/paste selections to clipboard
- Generate rows from a list of commands in an input.toml file.

## Examples

 - list_picker is used in [Aria2TUI](https://github.com/grimandgreedy/Aria2TUI). This is a good example of how list_picker can be used for menus, data viewing, and active data retrieval.

 - Identify video duplicates (./examples/video_duplicates.toml):
    - We from the list of commands in the toml file we generate the properties we will use to identify the duplicates. 
    - In the example file we set the directory and get the files with a simle `eza` (`ls`) command. We could also use `find` or `cat` from a list of files.
    - We get the SHA1 hash to identify identical files; we also get the size, duration, resolution, and bitrate so that we can identify a video duplicate that may have the same duration but a lower resolution.


## Description

### Key Features:
1. **File Input Support:**
   - Text files (TSV, CSV)
   - JSON
   - XLSX
   - ODS (OpenDocument Spreadsheet)

2. **Generate data based on an toml file with relevant commands to generate the rows.**
    - See ./examples/

3. **Highlighting:**
   - Highlight specific strings for display purposes.
   - E.g., when we search for a string we will highlight strings in the rows that match the search.

4. **Filtering and Sorting:**
   - Apply custom filters and sort criteria on the fly

5. **Modes:**
   - Default modes are supported so that a certain filter/search/sort can structure the data in a way that is easy to move between.


6. **Options:**
   - Along with returning the selected rows, the user can also return options.
   - Input field with readline support
   - Options select box

7. **Colour themes:**
   - Several colour themes are available

8. **Copy rows:**
   - 'y' to copy rows in various formats: CSV, TSV, python list
9. **Save data:**
   - Data can be saved so that it can be loaded with the -i flag.
   - This is very helpful if your data generation takes a long time.
10. **Customisable keybinds:**
   - The list_picker application takes a key dictionary so that certain functions can easily be changed to a preferred keybind.
   - Also allows the restriction of certain functions by not assigning a key.
11. **Dynamic or manual refresh of data**:
    - If a refresh_function is passed with auto_refresh=True then list_picker will automatically refresh the data.
    - If a refresh_function is passed then one can also manually refresh by pressing f5.
12. Notifications.
    - Supports notifications upon certain events
13. Visual options
    - Display/hide title. 
    - Display/hide footer with selection information
    - Display/hide columns
    - Display/hide highlights
    - Option to centre in cells, centre in terminal and centre rows vertically.

14. Change settings on the fly.
    - Press '~' to see list of display settings or press '`' to enter a command to change display settings.
    - Change visual options
        - Cycle through themes
        - Centre data in cells or centre rows vertically
        - Show/hide the footer
        - Show/hide a specific column.
        - Select a column
    - Toggle auto-refresh
    - Toggle highlights

15. Pipe the data from the selected rows in the focussed column to a bash command ('|')
    - By default when you press '|' it will fill the input field with `xargs -d '\n' -I {} `. You can remove this if you like (^U).
    - If you add `notify-send {}` to this it will display notifications containing the data from the current column 
    - Useful for:
        - Opening files with a specific application `xargs -d \n -I{} mpv {}` will open the files in mpv
        - Dumping data. `xargs -d \n -I{} echo {} > ~/stuff.txt`

## Overview

The application allows you to:
- Select multiple items from different file types and input streams
- Navigate between selected items with arrow keys
- Delete individual items
- Highlight specific items for quick selection
- Perform complex filtering operations
- Sort data based on specified columns
- Persistent save/load of selections
- Copy/paste selections to clipboard


## Support and Feedback

Feel free to request features. Please report any errors you encounter with appropriate context.
