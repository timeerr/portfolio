#!/usr/bin/python3
"""
This module creates the essential configuration and initializes the main widget of the application
"""

from PyQt5.QtWidgets import QVBoxLayout, QDialog, QComboBox, QPushButton, QMainWindow

from portfolio import logger
from portfolio.db import dbhandler
from portfolio.utils import confighandler
from portfolio.utils.confighandler import Vars
from portfolio.gui.app.welcomescreen import WelcomeWidget
from portfolio.gui.app.statusbar import StatusBar
from portfolio.gui.app.mainwidget import MainWidget


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Layout
        self.setWindowTitle(self.tr("Portfolio"))
        self.welcomewidget = WelcomeWidget(self)
        self.setCentralWidget(self.welcomewidget)
        # UI
        self.showMaximized()
        # Functionality
        self.welcomewidget.portfolioselected.connect(
            self.endWelcomeWidget)

    def endWelcomeWidget(self, portfolioname: str):
        """
        When the user selects a portfolio, the welcomewidget closes.
        Parameters:
            - portfolioname: name of portfolio to be opened
        """
        # Remove Welcome Screen
        self.welcomewidget.deleteLater()
        # Set portfolio as new central widget
        self.setWindowTitle(f'Portfolio - {portfolioname}')
        self.setCentralWidget(MainWidget(self))
        # Add Status Bar
        self.statusbar = StatusBar()
        self.setStatusBar(self.statusbar)

    def closeEvent(self, event):
        """Making sure that the database is properly updated before closing the app"""
        if type(self.centralWidget()) == WelcomeWidget:
            return
        logger.info("App Closed, updating database ...")
        dbhandler.handle_close()


class PreferencesSelection(QDialog):
    """
    A dialog that shows up the first time the app has ever been opened
    It's purpose is to make the user select the initial preferences
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Portfolio')
        self.layout = QVBoxLayout()
        self.setStyleSheet("QWidget { \
                           background-color: #19232d; color: white; }")

        self.lang_selection = QComboBox()
        self.lang_selection.addItems(Vars.LANGUAGES)
        self.layout.addWidget(self.lang_selection)

        self.fiat_selection = QComboBox()
        self.fiat_selection.addItems(Vars.FIAT_CURRENCIES)
        self.layout.addWidget(self.fiat_selection)

        self.select_bttn = QPushButton("Save")
        self.select_bttn.clicked.connect(self.setInitialPreferences)
        self.layout.addWidget(self.select_bttn)

        self.setLayout(self.layout)

    def setInitialPreferences(self):
        """Storing the selection on the config file"""
        language = self.lang_selection.currentText().lower()
        fiat_currency = self.fiat_selection.currentText().lower()

        confighandler.set_language(language)
        confighandler.set_fiat_currency(fiat_currency)
        self.close()
