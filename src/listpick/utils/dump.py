#!/bin/python
# -*- coding: utf-8 -*-
"""
dump.py
Dump data to file in selected format.

Author: GrimAndGreedy
License: MIT
"""

import os
import logging

logger = logging.getLogger('picker_log')

def make_list_unique(l:list) -> list:
    """ 
    Ensure each of the strings in a list is unique by numbering identical strings.
    """

    logger.info("function: make_list_unique (dump.py)")
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

    logger.info("function: dump_state (dump.py)")

    import dill as pickle
    exclude_keys =  ["refresh_function", "get_data_startup", "get_new_data", "auto_refresh"]
    function_data = {key: val for key, val in function_data.items() if key not in exclude_keys}
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'wb') as f:
        pickle.dump(function_data, f)

def dump_data(function_data:dict, file_path:str, format="pickle") -> str:
    """ Dump data from a Picker object. Returns whether there was an error. """
    logger.info("function: dump_data (dump.py)")

    # For multi-sheet formats, keep sheet data; otherwise filter to items/header only
    if format in ["xlsx", "ods"] and "sheet_states" in function_data:
        include_keys = ["items", "header", "sheet_states", "sheets", "original_file_path"]
    else:
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
        elif format == "xlsx":
            import pandas as pd

            # Check if we have multiple sheets to save
            if "sheet_states" in function_data and "sheets" in function_data and len(function_data["sheets"]) > 1:
                # Multi-sheet save - load all sheets BEFORE opening writer
                from listpick.utils.table_to_list_of_lists import xlsx_to_list
                original_file = function_data.get("original_file_path")

                # Prepare all dataframes before opening the writer
                sheets_to_save = []
                for i, sheet_name in enumerate(function_data["sheets"]):
                    # Check if this sheet has been modified (exists in sheet_states)
                    if i < len(function_data["sheet_states"]) and function_data["sheet_states"][i]:
                        # Use modified data from sheet_states
                        sheet_data = function_data["sheet_states"][i]
                        df = pd.DataFrame(sheet_data["items"], columns=make_list_unique(sheet_data["header"]))
                        sheets_to_save.append((sheet_name, df))
                    elif original_file and os.path.exists(original_file):
                        # Load unmodified sheet from original file
                        items, header, _ = xlsx_to_list(original_file, sheet_number=i)
                        df = pd.DataFrame(items, columns=make_list_unique(header))
                        sheets_to_save.append((sheet_name, df))

                # Now write all sheets
                with pd.ExcelWriter(os.path.expandvars(os.path.expanduser(file_path)), engine='openpyxl') as writer:
                    for sheet_name, df in sheets_to_save:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Single sheet save
                df = pd.DataFrame(function_data["items"], columns=make_list_unique(function_data["header"]))
                df.to_excel(os.path.expandvars(os.path.expanduser(file_path)), index=False, engine='openpyxl')
        elif format == "ods":
            import pandas as pd

            # Check if we have multiple sheets to save
            if "sheet_states" in function_data and "sheets" in function_data and len(function_data["sheets"]) > 1:
                # Multi-sheet save - load all sheets BEFORE opening writer
                from listpick.utils.table_to_list_of_lists import ods_to_list
                original_file = function_data.get("original_file_path")

                # Prepare all dataframes before opening the writer
                sheets_to_save = []
                for i, sheet_name in enumerate(function_data["sheets"]):
                    # Check if this sheet has been modified (exists in sheet_states)
                    if i < len(function_data["sheet_states"]) and function_data["sheet_states"][i]:
                        # Use modified data from sheet_states
                        sheet_data = function_data["sheet_states"][i]
                        df = pd.DataFrame(sheet_data["items"], columns=make_list_unique(sheet_data["header"]))
                        sheets_to_save.append((sheet_name, df))
                    elif original_file and os.path.exists(original_file):
                        # Load unmodified sheet from original file
                        items, header, _ = ods_to_list(original_file, sheet_number=i)
                        df = pd.DataFrame(items, columns=make_list_unique(header))
                        sheets_to_save.append((sheet_name, df))

                # Now write all sheets
                with pd.ExcelWriter(os.path.expandvars(os.path.expanduser(file_path)), engine='odf') as writer:
                    for sheet_name, df in sheets_to_save:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Single sheet save
                df = pd.DataFrame(function_data["items"], columns=make_list_unique(function_data["header"]))
                df.to_excel(os.path.expandvars(os.path.expanduser(file_path)), index=False, engine='odf')
    except Exception as e:
        return str(e)
    return ""

            

def load_state(file_path:str) -> dict:
    """ Load Picker state from dump. """
    logger.info("function: load_state (dump.py)")
    import dill as pickle
    with open(os.path.expandvars(os.path.expanduser(file_path)), 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data

