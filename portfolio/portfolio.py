#!/usr/bin/python3
"""
A GUI to track a trading/investing portfolio's results, transactions and balances.
Includes cryptocurrency accounts support
"""

import os
import sys

import configparser
import qdarkstyle

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTranslator

from portfolio.utils import confighandler
from portfolio.gui.app.app import MainWindow, PreferencesSelection


def main():
    """Main function"""
    app = QApplication(sys.argv)

    # ----- Internationalization ------
    # If a language hasn't been selected yet, we ask the user for one

    confighandler.initial_setup()
    if confighandler.get_language() == 'None' or confighandler.get_fiat_currency() == 'None':
        # Select language for the first time
        preferences_dlg = PreferencesSelection()
        preferences_dlg.exec_()

    selected_language = confighandler.get_language()
    if selected_language != 'en':
        translator = QTranslator()
        translator.load(os.path.join(os.path.expanduser(
            '~'), '.config', 'portfolio', "app_{}.qm".format(selected_language)))
        app.installTranslator(translator)

    # ------- Style ---------
    # Dark Theme
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    defaultfont = QFont()
    defaultfont.setFamily('Roboto')
    app.setFont(defaultfont)

    # Custom Theme
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

    # ---- Execution ----
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
