#!/usr/bin/python3

import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QBoxLayout, QVBoxLayout, QLabel, QTabWidget, QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt

from tabresults.tabresults import TabResults
from tabaccounts.tabaccounts import TabAccounts
from tabtransactions.tabtransactions import TabTransactions
from tabcrypto.tabcrypto import TabCrypto


class MainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tabwidget = QTabWidget(self)

        # Tab1 : Results
        self.tabresults = TabResults(self)
        self.tabwidget.addTab(self.tabresults, self.tabresults.windowIcon(),
                              self.tabresults.windowTitle())

        # Tab2 : Accounts
        self.tabaccounts = TabAccounts(self)
        self.tabwidget.addTab(self.tabaccounts, self.tabaccounts.windowIcon(),
                              self.tabaccounts.windowTitle())

        # Tab3 : Transactions
        self.tabtransactions = TabTransactions(self)
        self.tabwidget.addTab(self.tabtransactions, self.tabtransactions.windowIcon(),
                              self.tabtransactions.windowTitle())

        # Tab 4 : Crypto
        self.tabcrypto = TabCrypto(self)
        self.tabwidget.addTab(
            self.tabcrypto, self.tabcrypto.windowIcon(), self.tabcrypto.windowTitle())

        # Functionality between Tabs
        # Whenever a result is removed/added, we update the accounts on tabaccounts
        self.tabresults.righttable.rl.lineRemoved.connect(
            self.tabaccounts.refreshBalances)
        self.tabresults.leftlayout.add_results_form.insert_button.clicked.connect(
            self.tabaccounts.refreshBalances)

        # Whenever a transaction is removed/added, we update the accounts on tabaccounts
        self.tabtransactions.righttable.rl.lineRemoved.connect(
            self.tabaccounts.refreshBalances)
        self.tabtransactions.leftlayout.add_transactions_form.insert_button.clicked.connect(
            self.tabaccounts.refreshBalances)

        # Whenever a crypto account is added, or modified we update TabCrypto
        self.tabcrypto.toolbar.addaccount_dialog.updatecryptosignal.updated.connect(
            self.updateTabCrypto)

        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)
        self.setLayout(layout)

    def updateTabCrypto(self):
        """refreshes TabCrypto completely"""
        self.tabcrypto.deleteLater()
        self.tabcrypto = TabCrypto(self)
        self.tabwidget.addTab(
            self.tabcrypto, self.tabcrypto.windowIcon(), self.tabcrypto.windowTitle())
