#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QMessageBox

from portfolio.gui.ui_components.widgets.language_select import LanguageSelect
from portfolio.gui.ui_components.widgets.currency_select import CurrencySelect
from portfolio.gui.ui_components.fonts import PreferencesButtonFont, BoldFont

from portfolio.utils import confighandler


class TabPreferences(QWidget):
    """ Tab where user can change several app parameters """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- UI ----
        self.setWindowTitle(self.tr("Preferences"))
        # ---- Content ----
        self.layout = QVBoxLayout()
        self.layout.setSpacing(120)
        # Language
        self.language_select = LanguageSelect()
        self.layout.addWidget(self.language_select)
        # Currency
        self.currency_select = CurrencySelect()
        self.layout.addWidget(self.currency_select)
        # Spacer
        self.layout.addSpacerItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # Save Button
        self.save = SaveButton()
        self.layout.addLayout(self.save)

        self.setLayout(self.layout)

        # ---- Functionality ----
        self.save.bttn.clicked.connect(self.handleSave)

    def handleSave(self):
        confighandler.set_language(
            self.language_select.get_current_language())
        confighandler.set_fiat_currency(
            self.currency_select.get_current_currency())
        mssg = SavedMessage(self)
        mssg.exec()


class SavedMessage(QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("Saved"))
        self.setFont(BoldFont())
        self.setText(self.tr("Restart required to reflect changes"))


class SaveButton(QHBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- Content ----
        self.addSpacerItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.bttn = QPushButton(self.tr("Save && Restart"))
        self.addWidget(self.bttn)
        self.addSpacerItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Button
        font = PreferencesButtonFont()
        font.setPointSize(18)
        self.bttn.setFont(font)
        self.bttn.setFixedSize(240, 100)
        self.bttn.setStyleSheet(f"""
        QPushButton {{
        border-radius: 30px; border-width: 0px;
        }}
        """)
