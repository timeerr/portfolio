#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QButtonGroup

from portfolio.utils import confighandler, resource_gatherer
from portfolio.gui.ui_components.fonts import PreferencesLabelFont
from portfolio.gui.ui_components.widgets.preference_button import PreferenceButton


class CurrencySelect(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- Content ----
        self.layout = QHBoxLayout()
        self.layout.setSpacing(80)
        # Label
        self.label = QLabel(self.tr("Currency"))
        self.label.setFont(PreferencesLabelFont())
        self.layout.addWidget(self.label)
        # Languages buttons
        self.currency_bttns = CurrencyButtonsLayout()
        self.layout.addLayout(self.currency_bttns)
        # Spacer
        self.layout.addSpacerItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.setLayout(self.layout)

        # ---- Initialize ----
        self.set_initial_currency()

    def get_current_currency(self):
        for bttn in self.currency_bttns.bttns:
            if bttn.isChecked():
                return bttn.text()

    def set_initial_currency(self):
        initial_curr = confighandler.get_fiat_currency().upper()
        for bttn in self.currency_bttns.bttns:
            if bttn.text() == initial_curr:
                bttn.click()


class CurrencyButtonsLayout(QHBoxLayout):
    CURRENCIES = "USD", "EUR", "JPY"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- UI ----
        self.setSpacing(80)
        # ---- Content ----
        bttngroup = QButtonGroup(self)
        bttngroup.setExclusive(True)
        self.bttns = []
        for cur in self.CURRENCIES:
            curr_bttn = PreferenceButton(cur, f"currency_{cur}")
            bttngroup.addButton(curr_bttn)
            self.bttns.append(curr_bttn)
            self.addWidget(curr_bttn)
