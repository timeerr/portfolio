#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QButtonGroup

from portfolio.utils import confighandler, resource_gatherer
from portfolio.gui.ui_components.fonts import PreferencesLabelFont
from portfolio.gui.ui_components.widgets.preference_button import PreferenceButton


class LanguageSelect(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- Content ----
        self.layout = QHBoxLayout()
        self.layout.setSpacing(80)
        # Label
        self.label = QLabel(self.tr("Language"))
        self.label.setFont(PreferencesLabelFont())
        self.layout.addWidget(self.label)
        # Languages buttons
        self.languages_bttns = LanguageButtonsLayout()
        self.layout.addLayout(self.languages_bttns)
        # Spacer
        self.layout.addSpacerItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.setLayout(self.layout)

        # ---- Initialize ----
        self.set_initial_language()

    def get_current_language(self):
        for bttn in self.languages_bttns.bttns:
            if bttn.isChecked():
                return bttn.text()

    def set_initial_language(self):
        initial_lang = confighandler.get_language().upper()
        for bttn in self.languages_bttns.bttns:
            if bttn.text() == initial_lang:
                bttn.click()


class LanguageButtonsLayout(QHBoxLayout):
    LANGUAGES = "EN", "ES"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- UI ----
        self.setSpacing(80)
        # ---- Content ----
        bttngroup = QButtonGroup(self)
        bttngroup.setExclusive(True)
        self.bttns = []
        for lang in self.LANGUAGES:
            lang_bttn = PreferenceButton(lang, f"language_{lang}")
            bttngroup.addButton(lang_bttn)
            self.bttns.append(lang_bttn)
            self.addWidget(lang_bttn)
