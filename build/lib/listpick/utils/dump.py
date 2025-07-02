#!/bin/python
# -*- coding: utf-8 -*-
"""
dump.py
Dump data to file in selected format.

Author: GrimAndGreedy
License: MIT
"""

import os

def make_list_unique(l:list) -> list:
    """ Ensure each of the strings in a list is unique by numbering identical strings. """
    result = []
    for i in l:
        if i not in result:
            result.append(i)
        else:
            result[-1] += f'_({len(result)-1})'
            result.append(i)
    return result

def dump_state(function_data:dict, file_path:str) -> None:
    """ Dump state of Picker to file. """

    import dill as pickle
    exclude_keys =  ["refresh_function", "get_data_startup", "get_new_data", "auto_refresh"]
    function_data = {key: val for key, val in function_data.items() if key not in exclude_keys}
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'wb') as f:
        pickle.dump(function_data, f)

def dump_data(function_data:dict, file_path:str, format="pickle") -> str:
    """ Dump data from a Picker object. Returns whether there was an error. """
    include_keys = ["items", "header"]
    function_data = {key: val for key, val in function_data.items() if key in include_keys }

    try:
        if format == "pickle":
            import dill as pickle
            with open(os.path.expandvars(os.path.expanduser(file_path)), 'wb') as f:
                pickle.dump(function_data, f)
        elif format == "csv":
            import csv
            with open(os.path.expandvars(os.path.expanduser(file_path)), mode='w', newline='') as f:
                writer = csv.writer(f)
                for row in [function_data["header"]] + function_data["items"]:
                    writer.writerow(row)
        elif format == "tsv":
            import csv
            with open(os.path.expandvars(os.path.expanduser(file_path)), mode='w', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                for row in [function_data["header"]] + function_data["items"]:
                    writer.writerow(row)

        elif format == "json":
            import json
            with open(os.path.expandvars(os.path.expanduser(file_path)), mode='w') as f:
                json.dump([function_data["header"]]+ function_data["items"], f, indent=4)

        elif format == "feather":
            import pyarrow as pa
            import pandas as pd
            import pyarrow.feather as feather
            table = pa.Table.from_pandas(pd.DataFrame(function_data["items"], columns=make_list_unique(function_data["header"])))
            feather.write_feather(table, os.path.expandvars(os.path.expanduser(file_path)))
            
        elif format == "parquet":
            import pyarrow as pa
            import pyarrow.parquet as pq
            import pandas as pd
            table = pa.Table.from_pandas(pd.DataFrame(function_data["items"], columns=make_list_unique(function_data["header"])))

            pq.write_table(table, os.path.expandvars(os.path.expanduser(file_path)))
        elif format == "msgpack":
            import msgpack as mp
            with open(os.path.expandvars(os.path.expanduser(file_path)), mode='wb') as f:
                mp.dump([function_data["header"]]+ function_data["items"], f)
    except Exception as e:
        return str(e)
    return ""

            

def load_state(file_path:str) -> dict:
    """ Load Picker state from dump. """
    import dill as pickle
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data

