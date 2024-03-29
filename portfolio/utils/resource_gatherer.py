#!/usr/bin/python3

import os

from PyQt5.QtGui import QIcon, QPixmap

from portfolio.utils.confighandler import Paths

RESOURCES_PATH = Paths.RESOURCES_PATH


def get_resource(name: str) -> str:
    """Returns path to resource"""
    return os.path.join(RESOURCES_PATH, name)


def get_resource_QIcon(name: str):
    """Returns resource in QIcon format"""
    return QIcon(get_resource(name))


def get_resource_QPixmap(name: str):
    """Returns resource in QPixmap format"""
    return QPixmap(get_resource(name))
