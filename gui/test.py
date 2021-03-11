#!/usr/bin/python3

from dbhandler import dbwrapper
from assetgen import accounticongen
import os
import sys
import time

# BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
# print(os.listdir(BASE_DIR))
#
#
# print(dbwrapper.Balances().getAccount("Prueba"))

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QMainWindow, QPushButton


class Sii(QMainWindow):

    def __init__(self):
        super().__init__()

        print(time.time())
        self.setUpdatesEnabled(True)

        self.layout = QVBoxLayout()
        if int(str(round(time.time()))[-1]) < 5:
            self.layout.addWidget(QLabel("Hola"))
        else:
            self.layout.addWidget(QLabel("Adios"))

        self.bttn = QPushButton("r")
        self.bttn.clicked.connect(self.updatee)
        self.layout.addWidget(self.bttn)

        self.w = QWidget()
        self.w.setUpdatesEnabled(True)
        self.w.setLayout(self.layout)

        self.setCentralWidget(self.w)

    def updatee(self):
        lyt = QVBoxLayout()
        self.w.setLayout(lyt)


app = QApplication(sys.argv)
w = Sii()
w.show()
app.exec_()
