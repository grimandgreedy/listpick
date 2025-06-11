import os
import dill as pickle

def dump_state(function_data:dict, file_path:str) -> None:
    """ Dump state of list picker to file. """
    exclude_keys =  ["refresh_function", "get_data_startup", "get_new_data", "auto_refresh"]
    function_data = {key: val for key, val in function_data.items() if key not in exclude_keys}
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'wb') as f:
        pickle.dump(function_data, f)

def dump_data(function_data:dict, file_path:str) -> None:
    """ Dump data from list_picker. """
    include_keys = ["items", "header"]
    function_data = {key: val for key, val in function_data.items() if key in include_keys }
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'wb') as f:
        pickle.dump(function_data, f)

def load_state(file_path:str) -> dict:
    """ Load list_picker state from dump. """
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data

