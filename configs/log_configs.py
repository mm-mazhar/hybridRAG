# """
# log_configs.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# """

import json
import logging
import logging.config
import os


def load_logging_config(file_path) -> dict:
    """Loads the JSON config from the given file path"""
    with open(file_path) as f:
        return json.load(f)


def load_logConfigs() -> None:
    """Loads and sets up logging config if not already configured"""
    # log_dir = os.path.join(os.path.dirname(__file__), "logs")
    log_dir = os.path.join("logs")
    # print(f"log_dir: {log_dir}")

    # ✅ Ensure the logs directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_configs = load_logging_config(os.path.join(os.path.dirname(__file__), "log_Configs.json"))

    # Add colored formatter
    log_configs["formatters"]["colored"] = {
        "()": "colorlog.ColoredFormatter",
        "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "log_colors": {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    }

    # Modify the console handler to use the colored formatter
    log_configs["handlers"]["console"]["formatter"] = "colored"

    # Reconfigure logging with the modified configuration
    logging.config.dictConfig(log_configs)


# Run setup when the module is imported
# load_logConfigs()
