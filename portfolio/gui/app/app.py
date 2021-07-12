#!/usr/bin/python3
"""
This module creates the essential configuration and initializes the main widget of the application
"""

import os
import configparser

from PyQt5.QtWidgets import QVBoxLayout, QDialog, QComboBox, QPushButton, QMainWindow

from portfolio.db.cdbhandler import chistoricalbalances
from portfolio.db.fdbhandler import historicalbalances, costbasis
from portfolio.utils import confighandler
from portfolio.gui.app.welcomescreen import WelcomeWidget
from portfolio.gui.app.statusbar import StatusBar
from portfolio.gui.app.mainwidget import MainWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.tr("Portfolio"))
        self.showMaximized()

        self.welcomewidget = WelcomeWidget(self)
        self.welcomewidget.portfolioselected.selected.connect(
            self.endWelcomeWidget)
        self.setCentralWidget(self.welcomewidget)

    def endWelcomeWidget(self, portfolioname):
        """
        When the user selects a portfolio, the welcomewidget closes.
        Parameters:
            - portfolioname: name of portfolio to be opened
        """
        self.setWindowTitle(portfolioname)
        self.setCentralWidget(MainWidget(self))

        self.welcomewidget.deleteLater()

        self.statusbar = StatusBar()
        self.setStatusBar(self.statusbar)

    def closeEvent(self, event):
        """Making sure that the database is properly updated before closing the app"""
        print("App Closed, updating database ...")
        historicalbalances.add_todays_balances()
        costbasis.update_cost_basis()
        chistoricalbalances.add_todays_balances()


class PreferencesSelection(QDialog):
    """
    A dialog that shows the first time the app has ever been opened
    It's purpose is to make the user select the initial preferences,
    such as language, fiat currency
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Portfolio')
        self.layout = QVBoxLayout()
        self.setStyleSheet("QWidget { \
                           background-color: #19232d; color: white; }")

        self.language_selection = QComboBox()
        self.language_selection.addItems(['EN', 'ES'])
        self.layout.addWidget(self.language_selection)

        self.fiat_currency_selection = QComboBox()
        self.fiat_currency_selection.addItems(
            ['EUR', 'USD', 'JPY', 'CAD', 'AUD'])
        self.layout.addWidget(self.fiat_currency_selection)

        self.select_bttn = QPushButton("Select Language")
        self.select_bttn.clicked.connect(self.setInitialPreferences)
        self.layout.addWidget(self.select_bttn)

        self.setLayout(self.layout)

    def setInitialPreferences(self):
        """Storing the selection on the config file"""
        language = self.language_selection.currentText().lower()
        fiat_currency = self.fiat_currency_selection.currentText().lower()

        confighandler.set_language(language)
        confighandler.set_fiat_currency(fiat_currency)
        self.close()
