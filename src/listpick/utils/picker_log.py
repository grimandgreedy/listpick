"""
picker_log.py
Lines to be displayed on the help screen.

Author: GrimAndGreedy
License: MIT
"""

import logging


def setup_logger(name="picker_log", log_file="picker.log", log_enabled=True, level=logging.INFO):
    """ Set up a logger """
    logger = logging.getLogger(name)

    logger.handlers.clear()
    if log_enabled:
        # # prevent 
        # if not logger.handlers:
        logger.propagate = False
        file_handler = logging.FileHandler(log_file)        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',  '%m-%d-%Y %H:%M:%S')
        file_handler.setFormatter(formatter)

        logger.setLevel(level)
        logger.addHandler(file_handler)
        logger.disabled = False
    else:
        logger.disabled = True

    return logger

