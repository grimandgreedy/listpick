from typing import Tuple
import logging

logger = logging.getLogger('picker_log')

def paste_values(items: list[list[str]], pasta: list[list], paste_row:int, paste_col: int) -> Tuple[bool, list[list[str]]]:
    logger.info("function: paste_values (paste_operations.py)")
    if len(pasta) == 0:
        return False, items
    if len(items) == 0:
        return True, [[x if x!= None else "" for x in item] for item in pasta]
    
    pasta_row_count = len(pasta)
    pasta_col_count = len(pasta[0])
    items_row_count = len(items)
    items_col_count = len(items[0])

    if paste_row + pasta_row_count > items_row_count:
        # Add 
        rows_to_add = paste_row+pasta_row_count - items_row_count
        items += [["" for _ in range(items_col_count)] for __ in range(rows_to_add)]
    if paste_col + pasta_col_count > items_col_count:
        cols_to_add = paste_col + pasta_col_count - items_col_count
        for row in items:
            row += ["" for _ in range(cols_to_add)]

    for row_num in range(pasta_row_count):
        for col_num in range(pasta_col_count):
            val = pasta[row_num][col_num]
            if val != None:
                items[paste_row+row_num][paste_col+col_num] = val

    return True, items

