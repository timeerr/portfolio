# /usr/bin/python3

from PyQt5.QtWidgets import QStatusBar


class StatusBar(QStatusBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showMessage(self.tr("Bienvenido"), 1000)
