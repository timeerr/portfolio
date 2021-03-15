#!/usr/bin/python3

from gui.dbhandler import historicalbalances, costbasis
from gui.dbhandler import db_initialize
from gui.cdbhandler import chistoricalbalances
from gui.cdbhandler import cdb_initialize

from PyQt5 import QtGui, QtCore

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QBoxLayout, QVBoxLayout, QLabel, QStatusBar, QMessageBox, QDialog, QComboBox, QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt, QTranslator

import qdarkstyle
import os
from gui.resources.fonts import TitleFont
from .welcomescreen import WelcomeWidget
from .mainwidget import MainWidget
from .statusbar import StatusBar

import configparser

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
        """IMPLEMENTAR CLASE HIJA DE QSTATUSBAR CON DIFERENTES COSITAS COMO PRECIOS DE SPX, FEESBTC ETC"""

        self.setCentralWidget(self.welcomewidget)
        # self.setCentralWidget(MainWidget())

    def endWelcomeWidget(self):
        self.setCentralWidget(MainWidget(self))

        self.setStatusBar(self.statusbar)

    def closeEvent(self, event):
        # Before closeing, we update balances on balancehistory
        print("App Closed, updating database ...")
        historicalbalances.addTodaysBalances()
        costbasis.updateCostBasis()
        chistoricalbalances.addTodaysBalances()


class LanguageSelection(QDialog):

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
        language = language.lower()

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        config.add_section('LANGUAGE')
        config.set('LANGUAGE', 'language', language)

        with open(CONFIG_PATH, 'w') as cf:
            config.write(cf)

        self.close()
