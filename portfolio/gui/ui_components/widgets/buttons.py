#!/usr/bin/python3

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal

from portfolio.utils import resource_gatherer


class OpenPortfolioButton(QPushButton):

    def __init__(self, name, path, *args, **kwargs) -> None:
        super().__init__(name, *args, **kwargs)
        self.setStyleSheet("font: bold; font-size:20px")
        self.setCheckable(True)
        self.setFixedWidth(200)
        self.path = path
        self.name = name

    def set_unfunctional(self):
        self.setStyleSheet(
            "font:bold; font-size:20px;background-color:grey")
        self.setCheckable(False)


class DeletePortfolioButton(QPushButton):
    deleted = pyqtSignal()

    def __init__(self, name, path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setStyleSheet("font: bold; font-size:20px")
        self.setCheckable(True)
        self.setFixedWidth(24)
        self.setIcon(QIcon(resource_gatherer.get_resource_QIcon('trash.png')))
        self.path = path
        self.name = name
