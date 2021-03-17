#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import QApplication,  QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class WidgetTest(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Bienvenido")
        self.layout.addWidget(self.label)

        self.button = QPushButton("Hola")
        self.button.setStyleSheet("padding: 10px")
        self.button.setMaximumWidth(50)
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)


app = QApplication(sys.argv)
w = WidgetTest()
w.show()
app.exec_()
