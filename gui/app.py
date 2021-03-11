#!/usr/bin/python3

from dbhandler import historicalbalances, costbasis
from dbhandler import db_initialize
from cdbhandler import chistoricalbalances
from cdbhandler import cdb_initialize

from PyQt5 import QtGui, QtCore

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QBoxLayout, QVBoxLayout, QLabel, QStatusBar, QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt

import qdarkstyle
from fonts import TitleFont
from welcomescreen import WelcomeWidget
from mainwidget import MainWidget
from statusbar import StatusBar


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PortfolioFSA")
        # self.showMaximized()
        self.setGeometry(500, 300, 1000, 600)

        self.welcomewidget = WelcomeWidget()
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


app = QApplication(sys.argv)

""" TEMA 1 """
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

"""TEMA 2"""
# app.setStyle('Fusion')
# palette = QtGui.QPalette()
# palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
# palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
# palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
# palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
# palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
# palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
# palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
# palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
# palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
# palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
#
# palette.setColor(QtGui.QPalette.Highlight,
#                  QtGui.QColor(142, 45, 197).lighter())
# palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
# app.setPalette(palette)

w = MainWindow()
w.show()
app.exec_()
