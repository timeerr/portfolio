#!/usr/bin/python3

import os
import shutil
from gui import confighandler


os.system("pip install .")

CONFIG_PATH = confighandler.getConfigPath()
for file in os.listdir("gui"):
    if ".qm" in file:
        source = os.path.join("gui", file)
        dest = os.path.join(CONFIG_PATH, file)
        shutil.copy(source, dest)
        print("Moved ", source, "translation to ", dest)

RESOURCES_PATH = os.path.join(os.path.expanduser(
    '~'), '.local', 'share', 'portfolio')
if 'portfolio' in os.listdir(os.path.join(os.path.expanduser('~'), '.local', 'share')):
    shutil.rmtree(RESOURCES_PATH)

shutil.copytree(os.path.join('gui', 'resources'), RESOURCES_PATH)
for file in os.listdir(RESOURCES_PATH):
    if ".py" in file:
        os.remove(os.path.join(RESOURCES_PATH, file))
