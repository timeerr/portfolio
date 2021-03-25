#!/usr/bin/python3

import os
import shutil


os.system("pip install appdirs")
os.system("pip install .")


def initialize():
    from gui import confighandler
    from appdirs import user_data_dir
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

    shutil.copytree(os.path.join('gui', 'resources'), RESOURCES_PATH)
    print("Created resources folder on ", RESOURCES_PATH)
    for file in os.listdir(RESOURCES_PATH):
        if ".py" in file:
            os.remove(os.path.join(RESOURCES_PATH, file))


initialize()
