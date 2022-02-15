#!/usr/bin/python3

from PyQt5.QtWidgets import QPushButton


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
