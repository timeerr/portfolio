#!/usr/bin/python3
"""
This module creates the essential configuration and initializes the main widget of the application
"""

import os
import configparser

from PyQt5.QtWidgets import QVBoxLayout, QDialog, QComboBox, QPushButton, QMainWindow

from gui.cdbhandler import chistoricalbalances
from gui.dbhandler import historicalbalances, costbasis
from gui import confighandler
from gui.app.welcomescreen import WelcomeWidget
from gui.app.statusbar import StatusBar
from gui.app.mainwidget import MainWidget


CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'portfolio')
CONFIG_FILE_PATH = os.path.join(os.path.expanduser(
    '~'), '.config', 'portfolio', 'config.ini')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.tr("Portfolio"))
        self.showMaximized()
        #self.setGeometry(500, 300, 1000, 600)

        self.welcomewidget = WelcomeWidget(self)
        self.welcomewidget.portfolioselected.selected.connect(
            self.endWelcomeWidget)
        # self.welcomewidget.continue_bttn.clicked.connect(self.endWelcomeWidget)
        self.setCentralWidget(self.welcomewidget)

    def endWelcomeWidget(self, portfolioname):
        """ 
        When the user selects a portfolio, the welcomewidget closes 
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
        # Before closeing, we update balances on balancehistory
        print("App Closed, updating database ...")
        historicalbalances.addTodaysBalances()
        costbasis.updateCostBasis()
        chistoricalbalances.addTodaysBalances()


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
