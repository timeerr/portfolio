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
from PyQt5.QtCore import QTranslator

from .app.app import MainWindow, LanguageSelection

CONFIG_PATH = os.path.join('config.ini')


def get_language():
    """Reads configuration file to parse the current selected language"""
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    return config['LANGUAGE']['language']


def main():
    """Main function"""
    app = QApplication(sys.argv)

    if 'config.ini' not in os.listdir() or os.stat('config.ini').st_size == 0:
        # If a config file is not created, or is empty, we create one and ask for a language
        open('config.ini', 'w').close()

        language_dlg = LanguageSelection()
        language_dlg.exec_()

    selected_language = get_language()
    if selected_language != 'en':
        translator = QTranslator()
        translator.load("app_{}.qm".format(selected_language))
        app.installTranslator(translator)

    # Dark Theme
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

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

    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
