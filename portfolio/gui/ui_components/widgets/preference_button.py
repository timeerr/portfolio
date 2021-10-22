#!/usr/bin/python3

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize

from portfolio.utils import resource_gatherer
from portfolio.gui.ui_components.fonts import PreferencesButtonFont


class PreferenceButton(QPushButton):
    def __init__(self, text, icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- UI ----
        self.setFixedSize(180, 100)
        self.setStyleSheet(f"""
        QPushButton {{
        background-color: #273B4F; border-radius: 30px; border-width: 0px;
        }}
        QPushButton::hover {{
        border-color: white; border-style:solid; border-width:2px;
        }}
        QPushButton::checked {{
        background-color: white; color:#273B4F; border-width: 0px;
        }}
        """)
        self.setIcon(resource_gatherer.get_resource_QIcon(
            f'{icon}.png'))
        self.setIconSize(QSize(64, 64))
        self.setText(text)
        self.setFont(PreferencesButtonFont())
        # ---- Functionality ----
        self.setCheckable(True)
