#!/usr/bin/python3


from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt

from fonts import TitleFont


class WelcomeWidget(QWidget):

    def __init__(self):
        super().__init__()

        welcomelayout = QVBoxLayout()

        # -----High container------
        high_container = QWidget()
        high_container_layout = QVBoxLayout()
        high_container_layout.setAlignment(Qt.AlignBottom)

        label = QLabel(" Bienvenido ")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(TitleFont())

        high_container_layout.addWidget(label)

        label2 = QLabel("PortfolioFSA")
        font = QFont()
        font.setItalic(True)
        label2.setFont(font)
        label2.setAlignment(Qt.AlignHCenter)

        high_container_layout.addWidget(label2)
        high_container.setLayout(high_container_layout)

        welcomelayout.addWidget(high_container)

        # -------Low container-------
        low_container_layout = QVBoxLayout()
        pushbutton = QPushButton("Continuar")
        pushbutton.setStyleSheet("font: bold; font-size:20px")
        low_container_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        low_container_layout.addWidget(pushbutton)

        welcomelayout.addLayout(low_container_layout)

        self.setLayout(welcomelayout)
