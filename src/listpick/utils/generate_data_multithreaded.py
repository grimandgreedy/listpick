#!/bin/python
# -*- coding: utf-8 -*-
"""
generate_data_multithreaded.py
Generate data for listpick Picker.


1. Read toml file.
2. Set environment variables.
3. Get files from first command.
4. Create items with "..." for cells to be filled.
5. Create a priority queue which determines which cells are to be filled first.
6. Create a queue updater which increases the priorty of cells which are on screen which does so each second.
7. Create threads to start generating data for cells.

Author: GrimAndGreedy
License: MIT
"""

import subprocess
import os
from typing import Tuple, Callable
import toml
import logging
import threading
from queue import PriorityQueue
import time
import re
import shlex

logger = logging.getLogger('picker_log')

def generate_columns_worker(
    funcs: list,
    files: list,
    items: list[list[str]],
    getting_data: threading.Event,
    task_queue: PriorityQueue,
    completed_cells: set,
    state: dict,
) -> None:
    """ Get a task from the priorty queue and fill the data for that cell."""
    while task_queue.qsize() > 0 and not state["thread_stop_event"].is_set():
        _, (i, j) = task_queue.get()

        if (i, j) in completed_cells:
            task_queue.task_done()
            continue
            
        if state["thread_stop_event"].is_set():
            with task_queue.mutex:
                task_queue.queue.clear()

        generate_cell(
            func=funcs[j],
            file=files[i],
            items=items,
            row=i,
            col=j+1,
            state=state,
        )
        completed_cells.add((i, j))
        task_queue.task_done()
    getting_data.set()

def generate_cell(func: Callable, file: str, items: list[list[str]], row: int, col: int, state: dict) -> None:
    """
    Takes a function, file and a file and then sets items[row][col] to the result.
    """
    if not state["thread_stop_event"].is_set():
        try:
            result = func(file).strip()
            if not state["thread_stop_event"].is_set():
                items[row][col] = result
        except Exception as e:
            pass
            # import pyperclip
            # pyperclip.copy(f"({row}, {col}): len(items)={len(items)}, len(items[0])={len(items[0])} {e}")

def update_queue(task_queue: PriorityQueue, visible_rows_indices: list[int], rows: int, cols: int, state: dict):
    """ Increase the priority of getting the data for the cells that are currently visible. """
    while task_queue.qsize() > 0:
        time.sleep(0.1)
        if state["thread_stop_event"].is_set():
            with task_queue.mutex:
                task_queue.queue.clear()
            break 
        for row in visible_rows_indices:
            for col in range(cols):
                if state["generate_data_for_hidden_columns"] == False and col+1 in state["hidden_columns"]: continue
                if 0 <= row < rows:
                    task_queue.put((1, (row, col)))

        # Delay
        time.sleep(0.9)

def command_to_func(command: str) -> Callable:
    """
    Convert a command string to a function that will run the command.

    E.g.,
        mediainfo {} | grep -i format
        mediainfo {} | grep -i format | head -n 1 | awk '{{print $3}}'
    """
    logger.info("function: command_to_func (generate_data.py)")
    
    func = lambda arg: subprocess.run(replace_braces(command, arg), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip()
    return func

def load_environment(envs:dict):
    """
    Load environment variables from an envs dict.
    """
    logger.info("function: load_environment (generate_data.py)")

    if "cwd" in envs:
        os.chdir(os.path.expandvars(os.path.expanduser(envs["cwd"])))

def replace_braces(text, s):
    text = re.sub(r'\{\{(.*?)\}\}', r'@@\1@@', text)
    text = re.sub(r'\{\}', shlex.quote(s), text)
    text = re.sub(r'@@(.*?)@@', r'{{\1}}', text)
    return text

def read_toml(file_path) -> Tuple[dict, list, list]:
    """
    Read toml file and return the environment, commands and header sections.
    """
    logger.info("function: read_toml (generate_data.py)")
    with open(file_path, 'r') as file:
        config = toml.load(file)

    environment = config['environment'] if 'environment' in config else {}
    data = config['data'] if 'data' in config else {}
    commands = [command.strip() for command in data['commands']] if 'commands' in data else []
    header = [header for header in data['header']]  if 'header' in data else []
    return environment, commands, header
    
    
def generate_picker_data_from_file(
    file_path: str,
    items,
    header,
    visible_rows_indices,
    getting_data,
    state,

) -> None:
    """
    Generate data for Picker based upon the toml file commands.
    """
    logger.info("function: generate_picker_data (generate_data.py)")


    environment, lines, hdr = read_toml(file_path)

    # Load any environment variables from the toml file
    if environment:
        load_environment(environment)


    # Get list of files to be displayed in the first column.
    get_files_command = lines[0]
    files = subprocess.run(get_files_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip().split("\n")
    files = [file.strip() for file in files if files]
    
    commands_list = [line.strip() for line in lines[1:]]
    command_funcs = [command_to_func(command) for command in commands_list]

    generate_picker_data(
        files = files,
        column_functions = command_funcs,
        data_header = hdr,
        items = items,
        picker_header = header,
        visible_rows_indices = visible_rows_indices,
        getting_data = getting_data,
        state=state,
    )

def generate_picker_data(
    files: list[str],
    column_functions: list[Callable],
    data_header,
    items,
    picker_header,
    visible_rows_indices,
    getting_data,
    state,
) -> None:
    """
    Generate data from a list of files and a list of column functions which will be used to 
        generate subsequent columns.

    This function is performed asynchronously with os.cpu_count() threads.

    data_header: header list to be set for the picker
    picker_header: the picker header will be passed in so that it can be set for the class

    """
    logger.info("function: generate_picker_data (generate_data.py)")

    items.clear()
    items.extend([[file] + ["..." for _ in column_functions] for file in files])
    picker_header[:] = data_header


    task_queue = state["data_generation_queue"]
    for i in range(len(files)):
        for j in range(len(column_functions)):
            if state["generate_data_for_hidden_columns"] == False and j+1 in state["hidden_columns"]: continue
            task_queue.put((10, (i, j)))

    num_workers = os.cpu_count()
    if num_workers in [None, -1]: num_workers = 4
    if num_workers == None or num_workers < 1: num_workers = 1
    completed_cells = set()

    for _ in range(num_workers):
        gen_items_thread = threading.Thread(
            target=generate_columns_worker,
            args=(column_functions, files, items, getting_data, task_queue, completed_cells, state),
        )
        state["threads"].append(gen_items_thread)
        gen_items_thread.daemon = True
        gen_items_thread.start()

    update_queue_thread = threading.Thread(
        target=update_queue,
        args=(task_queue, visible_rows_indices, len(files), len(column_functions), state),
    )
    state["threads"].append(update_queue_thread)
    update_queue_thread.daemon = True
    update_queue_thread.start()
