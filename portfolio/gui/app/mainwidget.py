#!/usr/bin/python3

import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from portfolio.gui.tabcrypto.tabcrypto import TabCrypto
from portfolio.gui.tabtransactions.tabtransactions import TabTransactions
from portfolio.gui.tabaccounts.tabaccounts import TabAccounts
from portfolio.gui.tabresults.tabresults import TabResults
from portfolio.gui.tabdashboard.dashboard import TabDashboard


class MainWidget(QWidget):
    """
    The Widget which cointais all tabs and subwidgets
    It will handle all functionalities between tabs aswell.
    """

    def __init__(self, name,  *args, **kwargs):
        print(os.path.abspath(os.getcwd()))
        super().__init__(*args, **kwargs)

        self.tabwidget = QTabWidget(self)
        # self.tabwidget.setDocumentMode(True)
        self.tabwidget.setMovable(True)

        # Tab1 : Dashboard
        self.tabdashboard = TabDashboard(self)
        self.tabwidget.addTab(self.tabdashboard, self.tabdashboard.windowIcon(),
                              self.tabdashboard.windowTitle())

        # Tab2 : Results
        self.tabresults = TabResults(self)
        self.tabwidget.addTab(self.tabresults, self.tabresults.windowIcon(),
                              self.tabresults.windowTitle())

        # Tab3 : Accounts
        self.tabaccounts = TabAccounts(self)
        self.tabwidget.addTab(self.tabaccounts, self.tabaccounts.windowIcon(),
                              self.tabaccounts.windowTitle())

        # Tab4 : Transactions
        self.tabtransactions = TabTransactions(self)
        self.tabwidget.addTab(self.tabtransactions, self.tabtransactions.windowIcon(),
                              self.tabtransactions.windowTitle())

        # Tab 5 : Crypto
        self.tabcrypto = TabCrypto(self)
        self.tabwidget.addTab(
            self.tabcrypto, self.tabcrypto.windowIcon(), self.tabcrypto.windowTitle())

        # --------------- Functionality between Tabs --------------
        # Whenever a result is removed, we update tabaccounts
        self.tabresults.righttable.lineremoved.lineRemoved.connect(
            self.tabaccounts.refreshBalances)
        # Whenever a result is added, we update tabaccounts
        self.tabresults.leftlayout.add_results_form.insert_button.clicked.connect(
            self.tabaccounts.refreshBalances)

        # Whenever a transaction is removed, we update tabaccounts
        self.tabtransactions.righttable.lineremoved.lineremoved.connect(
            self.tabaccounts.refreshBalances)
        # Whenever a transaction is added, we update tabaccounts
        self.tabtransactions.leftlayout.add_transactions_form.insert_button.clicked.connect(
            self.tabaccounts.refreshBalances)

        # Whenever a crypto account is added/modified we update tabcrypto
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
