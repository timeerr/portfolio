#!/usr/bin/python3

import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from portfolio.gui.tabdashboard.dashboard import TabDashboard
from portfolio.gui.tabresults.tabresults import TabResults
from portfolio.gui.tabaccounts.tabaccounts import TabAccounts
from portfolio.gui.tabtransactions.tabtransactions import TabTransactions
from portfolio.gui.tabcrypto.tabcrypto import TabCrypto
from portfolio.gui.tabpreferences.tabpreferences import TabPreferences


class MainWidget(QTabWidget):
    """
    The Widget which contains all tabs and subwidgets
    It will handle all functionalities between tabs aswell.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # -------- UI ---------
        # self.tabwidget.setDocumentMode(True)
        self.setMovable(True)
        # -------- Content ---------
        # Tab1 : Dashboard
        self.tabdashboard = TabDashboard(self)
        self.addTab(self.tabdashboard, self.tabdashboard.windowTitle())
        # Tab2 : Results
        self.tabresults = TabResults(self)
        self.addTab(self.tabresults, self.tabresults.windowTitle())
        # Tab3 : Accounts
        self.tabaccounts = TabAccounts(self)
        self.addTab(self.tabaccounts, self.tabaccounts.windowTitle())
        # Tab4 : Transactions
        self.tabtransactions = TabTransactions(self)
        self.addTab(self.tabtransactions, self.tabtransactions.windowTitle())
        # Tab 5 : Crypto
        self.tabcrypto = TabCrypto(self)
        self.addTab(self.tabcrypto,  self.tabcrypto.windowTitle())
        # Tab 6 : Preferences
        self.tabpreferences = TabPreferences(self)
        self.addTab(self.tabpreferences,  self.tabpreferences.windowTitle())

        # --------------- Functionality between Tabs --------------
        # Whenever a result is removed, we update tabaccounts
        self.tabresults.righttable.lineremoved.lineRemoved.connect(
            self.tabaccounts.refreshBalances)
        # Whenever a result is added, we update tabaccounts
        self.tabresults.leftlayout.add_results_form.insert_button.clicked.connect(
            self.tabaccounts.refreshBalances)

        # Whenever an account is added, we refresh several widgets
        self.tabaccounts.accounts_toolbar.add_account_dialog.accountAdded.connect(
            self.updateWithNewAccount
        )

        # Whenever a transaction is removed, we update tabaccounts
        self.tabtransactions.righttable.lineremoved.lineremoved.connect(
            self.tabaccounts.refreshBalances)
        # Whenever a transaction is added, we update tabaccounts
        self.tabtransactions.leftlayout.add_transactions_form.insert_button.clicked.connect(
            self.tabaccounts.refreshBalances)

        # Whenever a crypto account is added/modified we update tabcrypto
        self.tabcrypto.toolbar.addaccount_dialog.updatecryptosignal.updated.connect(
            self.refreshTabCrypto)

    def refreshTabCrypto(self):
        """Refreshes TabCrypto completely"""
        self.tabcrypto.deleteLater()
        self.tabcrypto = TabCrypto(self)
        self.insertTab(4, self.tabcrypto, self.tabcrypto.windowTitle())

    def refreshTabDashboard(self):
        """Refreshes TabDashboard completely"""
        self.tabdashboard.deleteLater()
        self.tabdashboard = TabDashboard(self)
        self.insertTab(0, self.tabdashboard,  self.tabdashboard.windowTitle())

    def refreshTabResults(self):
        self.tabresults.deleteLater()
        self.tabresults = TabResults(self)
        self.insertTab(1, self.tabresults, self.tabresults.windowTitle())

    def updateWithNewAccount(self):
        """
        Updates several widgets that need to reflect a new account
        that has just been added
        """
        self.refreshTabResults()
        self.refreshTabDashboard()
