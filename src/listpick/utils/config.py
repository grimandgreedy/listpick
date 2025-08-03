import os
import toml
import logging

logger = logging.getLogger('picker_log')

def get_config(path="~/.config/aria2tui/config.toml") -> dict:
    logger.info("function: get_config (config.py)")
    """ Get config from file. """
    full_config = get_default_config()

    if "ARIA2TUI_CONFIG_PATH" in os.environ:
        if os.path.exists(os.path.expanduser(os.environ["ARIA2TUI_CONFIG_PATH"])):
            path = os.environ["ARIA2TUI_CONFIG_PATH"]

    if os.path.exists(os.path.expanduser(path)):
        with open(os.path.expanduser(path), "r") as f:
            config = toml.load(f)

        if "general" in config:
            for key in config["general"]:
                full_config["general"][key] = config["general"][key]
        if "appearance" in config:
            for key in config["appearance"]:
                full_config["appearance"][key] = config["appearance"][key]

    return full_config

def get_default_config() -> dict:
    logger.info("function: get_default_config (config.py)")
    default_config = {
        "general" : {
            # "url": "http://localhost",
            # "port": "6800",
            # "token": "",
            # "startupcmds": ["aria2c"],
            # "restartcmds": ["pkill aria2c && sleep 1 && aria2c"],
            # "ariaconfigpath": "~/.config/aria2/aria2.conf",
            "paginate": False,
            "refresh_timer": 2,
            "global_stats_timer": 1,
            "terminal_file_manager": "yazi",
            "gui_file_manager": "kitty yazi",
            "launch_command": "xdg-open",
        },
        "appearance":{
            "theme": 0
        }
    }
    return default_config
