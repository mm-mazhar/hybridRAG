# """
# configs.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# """

import logging

import yaml

logger: logging.Logger = logging.getLogger(name="app.logs")

DOC_CONFIGS = "./configs/docPipeline_configs.yaml"


cfgs: dict = {}
try:
    with open(file=DOC_CONFIGS) as file:
        cfgs = yaml.safe_load(stream=file)
except FileNotFoundError:
    logger.error(msg=f"{DOC_CONFIGS} not found.")
finally:
    if not cfgs:
        logger.error(msg="No configuration found in the YAML file.")
        exit(code=1)
