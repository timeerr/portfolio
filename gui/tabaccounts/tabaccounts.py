# /usr/bin/python3

from gui.dbhandler import balances
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QToolBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QMargins, QSize, Qt

from gui.assetgen.accounticongen import get_png_account
from gui.resources.fonts import TitleFont, AccountBalanceHeaderFont, AccountBalanceTextFont
from gui.tabaccounts.tabaccounts_toolbar import AccountsToolBar
from gui.tabaccounts.tabaccounts_layout import AccountsLayout
from gui.tabaccounts.account import Account


class TabAccounts(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Atributes and data
        self.updateDataAccounts()

        # -------UI--------
        self.setWindowTitle(self.tr("Accounts"))
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(QMargins(0, 0, 0, 0))

        # ----------------- Toolbar -----------------------
        self.accounts_toolbar = AccountsToolBar(self)

        # ----------------- Accounts Layout -----------------------
        self.accounts_layout = AccountsLayout(self.data_accounts)
        self.accounts_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        # -----------Functionality-----------
        self.accounts_toolbar.add_account_dialog.create_bttn.clicked.connect(
            self.refreshBalances)
        # Update layout with new account
        self.accounts_toolbar.remove_account_dialog.remove_account_warning.warning_bttn.clicked.connect(
            self.refreshBalances)
        # Account name updated
        self.accounts_toolbar.edit_account_dialog.customSignal.accountEdited.connect(
            self.refreshBalances)
        # Refresh
        self.accounts_toolbar.refresh_action.triggered.connect(
            self.refreshBalances)

        # ----------Main Layout---------
        self.mainlayout.addWidget(self.accounts_toolbar)
        self.mainlayout.addWidget(self.accounts_layout)
        self.setLayout(self.mainlayout)

    def updateDataAccounts(self):
        self.data_accounts = []
        for acc in balances.getAllAccounts():
            self.data_accounts.append(Account(acc[0], acc[1]))

    def refreshBalances(self):
        """ Clears balances and re-reads them on database """
        self.accounts_layout.deleteLater()
        self.updateDataAccounts()
        print("TabAccounts Layout Refreshed")
        self.accounts_layout = AccountsLayout(self.data_accounts)
        self.mainlayout.addWidget(self.accounts_layout)
