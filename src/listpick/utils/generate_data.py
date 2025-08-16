#!/bin/python
# -*- coding: utf-8 -*-
"""
generate_data.py
Generate data for listpick Picker.

Author: GrimAndGreedy
License: MIT
"""

import subprocess
import os
from typing import Tuple, Callable
import toml
import logging

logger = logging.getLogger('picker_log')

def generate_columns(funcs: list, files: list) -> list[list[str]]:
    """
    Takes a list of functions and a list of files. Each function is run for each file and a list of lists is returned.
    """
    logger.info("function: generate_columns (generate_data.py)")
    items = []
    for file in files:
        item = []
        for func in funcs:
            try:
                item.append(func(file))
            except:
                item.append("")
        items.append(item)
        
    return items

def command_to_func(command: str) -> Callable:
    """
    Convert a command string to a function that will run the command.

    E.g.,
        mediainfo {} | grep -i format
        mediainfo {} | grep -i format | head -n 1 | awk '{{print $3}}'
    """
    logger.info("function: command_to_func (generate_data.py)")
    
    func = lambda arg: subprocess.run(command.format(repr(arg)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    return func

def load_environment(envs:dict):
    """
    Load environment variables from an envs dict.
    """
    logger.info("function: load_environment (generate_data.py)")

    if "cwd" in envs:
        os.chdir(os.path.expandvars(os.path.expanduser(envs["cwd"])))


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
    
def generate_picker_data(file_path: str) -> Tuple[list[list[str]], list[str]]:
    """
    Generate data for Picker based upon the toml file commands.
    """
    logger.info("function: generate_picker_data (generate_data.py)")
    environment, commands, header = read_toml(file_path)
    lines = commands

    if environment:
        load_environment(environment)

    arg_command = lines[0]
    args = subprocess.run(arg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").split("\n")
    args = [arg.strip() for arg in args if arg]
    
    commands_list = [line.strip() for line in lines[1:]]
    command_funcs = [command_to_func(command) for command in commands_list]
    items = generate_columns(command_funcs, args)
    items = [[args[i]] + items[i] for i in range(len(args))]
    items = [[cell.strip() for cell in item] for item in items]

    return items, header
    
