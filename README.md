# listpick

listpick is a powerful TUI data tool for viewing, editing and operating upon tabulated data; can be used to build TUI applications, generate data columns, or function as a command-line utility.

**NOTE**: listpick is still in development.

# Quickstart

Install listpick:

```
python -m pip installl "listpick[full]"
```

Create a Picker:

```
from listpick.listpick_app import Picker, start_curses, close_curses

stdscr = start_curses()

x = Picker(
    stdscr,
    items=[
        ["row zero column zero", "row zero column one"],
        ["row one column zero", "row one column one"]
    ],
    header=["H0", "H1"],
    cell_cursor=True,
)
x.run()

close_curses(stdscr)

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


### listpick as a command-line tool

listpick can be used as a command-line tool for tabulating command outputs:
```bash
df -h | listpick --stdin
```

<div align="center"> <img src="assets/listpick_df_example.png" alt="lpfman" width="90%"> </div>

### Applications

#### Aria2TUI

[Aria2TUI](https://github.com/grimandgreedy/Aria2TUI): TUI client for the aria2c download utility.

<div align="center"> <img src="assets/aria2tui_graph_screenshot.png" alt="Aria2TUI" width="90%"> </div>

#### lpfman
[lpfman](https://github.com/grimandgreedy/lpfman): Terminal file manager with extensive column support.

<div align="center"> <img src="https://github.com/grimandgreedy/lpfman/blob/master/assets/lpfman_02.png?raw=true" alt="lpfman" width="90%"> </div>


### Data generation from toml file

```python 
listpick -g ./listpick/examples/data_generation/video_duplicates.toml
```
  - From the list of commands in the toml file we generate the properties we will use to identify the duplicates. 

  - In the example file we set the directory and get the files with a simle `eza` (`ls`) command. We could also use `find` or `cat` from a list of files.


  - We get the SHA1 hash to identify identical files; we also get the size, duration, resolution, and bitrate so that we can identify a video duplicate that may have the same duration but a lower resolution.

<div align="center"> <img src="assets/file_compare.png" alt="Video Compare" width="90%"> </div>


## Description

### Key Features:
1. **File Input Support:**
```python 
listpick -i ~/items.csv
```
   - Text files (TSV, CSV)
   - JSON
   - XLSX
   - ODS (OpenDocument Spreadsheet)
   - Pickle

2. **Generate data based on an toml file with relevant commands to generate the rows.**
```python 
listpick -g ./examples/data_generation/video_duplicates.toml
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
   - By default when you press '|' it will fill the input field with `xargs `. You can remove this if you like (^U).
   - For example, if you run `xargs -d '\n' -I {} notify-send {}` to this it will display notifications containing the data from the current column 
   - Useful for:
       - Opening files with a specific application `xargs -d \n -I{} mpv {}` will open the files in mpv
       - Dumping data. `xargs -d \n -I{} echo {} > ~/stuff.txt`

## Support and Feedback

Feel free to request features. Please report any errors you encounter with appropriate context.
