#!/usr/bin/python3
import os
import sys

import configparser
import qdarkstyle
from .app.app import MainWindow, LanguageSelection
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTranslator

CONFIG_PATH = os.path.join('config.ini')


def main():
    app = QApplication(sys.argv)

    def getLanguage():
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        return config['LANGUAGE']['language']

    if 'config.ini' not in os.listdir() or os.stat('config.ini').st_size == 0:
        # If a config file is not created, or is empty, we create one and ask for a language
        open('config.ini', 'w').close()

        language_dlg = LanguageSelection()
        language_dlg.exec_()

    selected_language = getLanguage()
    if selected_language != 'en':
        t = QTranslator()
        t.load("app_{}.qm".format(selected_language))
        app.installTranslator(t)

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


if __name__ == "__main__":
    main()
