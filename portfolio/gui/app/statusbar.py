# /usr/bin/python3

from PyQt5.QtWidgets import QStatusBar


class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self.showMessage(self.tr("Bienvenido"), 1000)
