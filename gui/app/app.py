#!/usr/bin/python3
"""
This module creates the essential configuration and initializes the main widget of the application
"""

import os
import configparser


from PyQt5.QtWidgets import QVBoxLayout, QDialog, QComboBox, QPushButton, QMainWindow

from gui.cdbhandler import cdb_initialize  # Just to create the db
from gui.cdbhandler import chistoricalbalances
from gui.dbhandler import db_initialize  # Just to create the db
from gui.dbhandler import historicalbalances, costbasis
from .welcomescreen import WelcomeWidget
from .statusbar import StatusBar
from .mainwidget import MainWidget


CONFIG_PATH = os.path.join('config.ini')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.tr("Portfolio"))
        # self.showMaximized()
        self.setGeometry(500, 300, 1000, 600)

        self.welcomewidget = WelcomeWidget(self)
        self.welcomewidget.children()[2].clicked.connect(self.endWelcomeWidget)

        self.statusbar = StatusBar()

        self.setCentralWidget(self.welcomewidget)
        # self.setCentralWidget(MainWidget())

    def endWelcomeWidget(self):
        """ When the user selects a portfolio, the welcomewidget closes """
        self.setCentralWidget(MainWidget(self))
        self.setStatusBar(self.statusbar)

    def closeEvent(self, event):
        """Making sure that the database is properly updated before closing the app"""
        # Before closeing, we update balances on balancehistory
        print("App Closed, updating database ...")
        historicalbalances.addTodaysBalances()
        costbasis.updateCostBasis()
        chistoricalbalances.addTodaysBalances()


class LanguageSelection(QDialog):
    """
    A dialog that shows the first time the app has ever been opened
    It's purpose is to make the user select a language, that also could be changed later
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

        self.select_bttn = QPushButton("Select Language")
        self.select_bttn.clicked.connect(
            lambda: self.changeLanguageConfig(self.language_selection.currentText()))
        self.layout.addWidget(self.select_bttn)

        self.setLayout(self.layout)

    def changeLanguageConfig(self, language):
        """Storing the language selection on the config file"""
        language = language.lower()

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        config.add_section('LANGUAGE')
        config.set('LANGUAGE', 'language', language)

        with open(CONFIG_PATH, 'w') as cf:
            config.write(cf)

        self.close()
