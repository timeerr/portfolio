#!/usr/bin/python3

import sys
import os
import shutil


def install_dependencies():
    os.system(f"{sys.executable} -m pip install .")


def initialize():
    from portfolio import logger
    from portfolio.utils import confighandler
    from portfolio.utils.confighandler import Paths
    from portfolio.utils.appdirs import user_data_dir

    confighandler.initial_setup()

    # ---- Move resources to filesystem----
    RESOURCES_PATH = Paths.RESOURCES_PATH
    # Remove previous resources
    if 'portfolio' in os.listdir(user_data_dir()):
        logger.info(f"Deleting previous resources: {RESOURCES_PATH}")
        shutil.rmtree(RESOURCES_PATH)
    # Translation files
    for file in os.listdir('tanslations'):
        if ".qm" in file:
            dest = os.path.join(RESOURCES_PATH, file)
            shutil.copy(file, dest)
            logger.info(f"- Moved {file} translation to {dest}")
    # Assets
    shutil.copytree(os.path.join('resources'), RESOURCES_PATH)

    logger.info("Created resources folder on {RESOURCES_PATH}")


if __name__ == "__main__":
    install_dependencies()
    initialize()
