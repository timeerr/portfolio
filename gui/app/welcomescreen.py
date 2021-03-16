#!/usr/bin/python3


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from gui.resources.fonts import TitleFont


class WelcomeWidget(QWidget):
    """
    First window that gets displayed.
    Here the user can add/remove portfolios, and select which one they want to access.
    Once one is selected, it closes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()

        # -----High container------
        self.high_container = QWidget()
        self.high_container_layout = QVBoxLayout()
        self.high_container_layout.setAlignment(Qt.AlignBottom)

        self.label = QLabel(self.tr("Welcome"))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(TitleFont())
        self.high_container_layout.addWidget(self.label)

        self.label2 = QLabel("Portfolio")
        self.label2.setAlignment(Qt.AlignHCenter)
        font = QFont()
        font.setItalic(True)
        self.label2.setFont(font)

        self.high_container_layout.addWidget(self.label2)
        self.high_container.setLayout(self.high_container_layout)
        self.layout.addWidget(self.high_container)

        # -------Low container-------
        self.low_container_layout = QVBoxLayout()
        self.continue_bttn = QPushButton(self.tr("Continue"))
        self.continue_bttn.setStyleSheet("font: bold; font-size:20px")
        self.low_container_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.low_container_layout.addWidget(self.continue_bttn)
        self.layout.addLayout(self.low_container_layout)

        self.setLayout(self.layout)
