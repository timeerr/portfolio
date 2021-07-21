#!/usr/bin/python3

import sys
import sys
import os
import shutil
import logging


def install_dependencies():
    os.system(f"{sys.executable} -m pip install .")


def initialize():
    from portfolio.utils import confighandler
    from portfolio.utils.appdirs import user_data_dir

    confighandler.initial_setup()

    # Translation
    CONFIG_PATH = confighandler.get_config_path()
    for file in os.listdir():
        if ".qm" in file:
            source = os.path.join(file)
            dest = os.path.join(CONFIG_PATH, file)
            shutil.copy(source, dest)
            logging.info("Moved %s translation to %s", source, dest)

    RESOURCES_PATH = confighandler.get_user_data_path()
    if 'portfolio' in os.listdir(user_data_dir()):
        logging.info("Deleting previous resources: %s", RESOURCES_PATH)
        shutil.rmtree(RESOURCES_PATH)
    # Copy resources to RESOURCES_PATH
    shutil.copytree(os.path.join('resources'), RESOURCES_PATH)
    for file in os.listdir(RESOURCES_PATH):
        if ".py" in file:
            os.remove(os.path.join(RESOURCES_PATH, file))
    logging.info("Created resources folder on %s", RESOURCES_PATH)


if __name__ == "__main__":
    install_dependencies()
    initialize()
