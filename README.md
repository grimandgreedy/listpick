# listpick

listpick is a TUI tool which displays a tabulated list of rows and allows the user to operate upon these rows--select, copy, pipe. A very simple concept but also, I hope, a powerful tool that will make it easier for people to develop TUI apps.

Rows of data can be viewed, selected, generated, saved, loaded, refreshed, modified or copied to the clipboard. Easy to integrate into your project by creating a `menu = Picker(stdscr, items:list[list[str]])` and then the menu will be displayed by running `menu.run()`.

It works great as the backend for a TUI application and can also be used as a standalone data viewer.

**NOTE**: listpick is still in development.

# Quickstart

Install listpick

```
python -m pip installl "listpick[full]"
```

Create a picker object to display rows:

```
from listpick.listpick_app import Picker, start_curses, close_curses

stdscr = start_curses()

x = Picker(
    stdscr,
    items=[
        ["row zero column zero", "row zero column one"],
        ["row one column zero", "row one column one"]
    ],
    header=["H0", "H1"]
)
x.run()

close_curses(stdscr)

```
Use the listpick binary to generate and display rows based on a list of commands:

```
wget https://raw.githubusercontent.com/grimandgreedy/listpick/refs/heads/master/examples/list_files.toml
listpick -g list_files.py
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


### Identify video duplicates (./examples/video_duplicates.toml):
```python 
listpick -g ./examples/video_duplicates.toml
```
  - From the list of commands in the toml file we generate the properties we will use to identify the duplicates. 

  - In the example file we set the directory and get the files with a simle `eza` (`ls`) command. We could also use `find` or `cat` from a list of files.


  - We get the SHA1 hash to identify identical files; we also get the size, duration, resolution, and bitrate so that we can identify a video duplicate that may have the same duration but a lower resolution.

<div align="center"> <img src="assets/file_compare.png" alt="Video Compare" width="70%"> </div>


### Aria2TUI

[Aria2TUI](https://github.com/grimandgreedy/Aria2TUI) is implemented using listpick. This is a good example of how listpick can be used for menus, data viewing, and active data retrieval.

<div align="center"> <img src="assets/aria2tui_screenshot.png" alt="Aria2TUI" width="70%"> </div>

### lpfman
[lpfman](https://github.com/grimandgreedy/lpfman) is a basic file manager created for the purposes of illustrating how easy TUI apps can be developed with the use of listpick. In 20 minutes and <100 lines of code we made a very basic file manager.

<div align="center"> <img src="assets/lpfman.png" alt="lpfman" width="70%"> </div>



## Description

### Key Features:
1. **File Input Support:**
```python 
listpick -i ~/dn.pkl -t pkl
```
   - Text files (TSV, CSV)
   - JSON
   - XLSX
   - ODS (OpenDocument Spreadsheet)
   - Pickle

2. **Generate data based on an toml file with relevant commands to generate the rows.**
```python 
listpick -g ./examples/video_duplicates.toml
```

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
   - The Picker object takes a keys_dict variable which allows all keys to be customised. Default keys can be seen in src/listpick/ui/keys.py.
   - Also allows the restriction of certain functions by not assigning a key.
11. **Dynamic or manual refresh of data**:
   - If a refresh_function is passed with auto_refresh=True then listpick will automatically refresh the data.
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
