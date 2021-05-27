#!/usr/bin/python3

import os
import shutil


def install_dependencies():
    os.system("pip3 install appdirs")
    os.system("pip3 install .")


def initialize():
    from portfolio import confighandler
    from appdirs import user_data_dir
    confighandler.initial_setup()
    CONFIG_PATH = confighandler.getConfigPath()
    for file in os.listdir():
        if ".qm" in file:
            source = os.path.join(file)
            dest = os.path.join(CONFIG_PATH, file)
            shutil.copy(source, dest)
            print("Moved ", source, "translation to ", dest)

    RESOURCES_PATH = confighandler.getUserDataPath()
    if 'portfolio' in os.listdir(user_data_dir()):
        # Deleting previous folder
        print("Deleting ", RESOURCES_PATH)
        shutil.rmtree(RESOURCES_PATH)
    # Copy resources to RESOURCES_PATH
    shutil.copytree(os.path.join('resources'), RESOURCES_PATH)
    print("Created resources folder on ", RESOURCES_PATH)
    for file in os.listdir(RESOURCES_PATH):
        if ".py" in file:
            os.remove(os.path.join(RESOURCES_PATH, file))


install_dependencies()
initialize()
