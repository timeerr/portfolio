#!/usr/bin/python3
"""
A GUI to track a trading/investing portfolio's results, transactions and balances.
Includes cryptocurrency accounts support
"""

import os
import sys
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTranslator

import qdarkstyle

from portfolio.utils import confighandler, resource_gatherer
from portfolio.utils.confighandler import Paths
from portfolio.gui.app.app import MainWindow, PreferencesSelection
from portfolio import logger

RESOURCES_PATH = Paths.RESOURCES_PATH


def check_saved():
    if confighandler.get_language() == 'None' or confighandler.get_fiat_currency() == 'None':
        sys.exit()


def main():
    try:
        from PyQt5.QtWinExtras import QtWin
        myappid = 'timeerr.portfolio.0-0-1'
        QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app = QApplication(sys.argv)
    # ----- Internationalization ------
    # If a language hasn't been selected yet, we ask the user for one
    confighandler.initial_setup()
    if confighandler.get_language() == 'None' or confighandler.get_fiat_currency() == 'None':
        # Select language for the first time
        preferences_dlg = PreferencesSelection()
        preferences_dlg.finished.connect(check_saved)
        preferences_dlg.exec_()
    # Load language
    selected_language = confighandler.get_language()
    if selected_language != 'EN':
        logger.info(f"Loading language {selected_language}")
        # Search for translation file
        translation_file = os.path.join(
            RESOURCES_PATH, f"app_{selected_language.lower()}.qm")
        if not os.path.exists(translation_file):
            logger.warning(
                f"Couldn't tanslate app to {selected_language} : Translation file missing")
        else:
            # Translate
            translator = QTranslator()
            translator.load(translation_file)
            app.installTranslator(translator)

    # ------- Style ---------
    # Dark Style Theme
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # Font
    defaultfont = QFont()
    defaultfont.setFamily('Roboto')
    app.setFont(defaultfont)
    # Icon
    app.setWindowIcon(resource_gatherer.get_resource_QIcon('icon_64.png'))

    # ---- Execution ----
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
