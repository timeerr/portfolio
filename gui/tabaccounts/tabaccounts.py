# /usr/bin/python3

from dbhandler import balances
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QToolBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QMargins, QSize, Qt

from assetgen.accounticongen import get_png_account
from fonts import TitleFont, AccountBalanceHeaderFont, AccountBalanceTextFont
from tabaccounts.tabaccounts_toolbar import AccountsToolBar
from tabaccounts.tabaccounts_layout import AccountsLayout
from tabaccounts.account import Account


class TabAccounts(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Atributes and data
        self.updateDataAccounts()

        # -------UI--------
        self.setWindowTitle(self.tr("Accounts"))
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(QMargins(0, 0, 0, 0))

        # ----------------- Accounts Layout -----------------------
        self.accounts_layout = AccountsLayout(self.data_accounts)
        self.accounts_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        # ----------------- Left Layout -----------------------
        self.accounts_toolbar = AccountsToolBar(self)

        # -----------Functionality-----------
        self.accounts_toolbar.add_account_dialog.create_bttn.clicked.connect(
            self.refreshBalances)
        # Update layout with new account
        self.accounts_toolbar.remove_account_dialog.remove_account_warning.warning_bttn.clicked.connect(
            self.refreshBalances)
        # Account name updated
        self.accounts_toolbar.edit_account_dialog.customSignal.accountEdited.connect(
            self.refreshBalances)

        # ----------Main Layout---------
        self.mainlayout.addWidget(self.accounts_toolbar)
        self.mainlayout.addWidget(self.accounts_layout)
        self.setLayout(self.mainlayout)

    def updateDataAccounts(self):
        self.data_accounts = []
        print(balances.getAllAccounts())
        for acc in balances.getAllAccounts():
            print(acc[0])
            self.data_accounts.append(Account(acc[0], acc[1]))

    def refreshBalances(self):
        """ Clears balances and re-reads them on database """
        self.accounts_layout.deleteLater()
        self.updateDataAccounts()
        self.accounts_layout = AccountsLayout(self.data_accounts)
        self.mainlayout.addWidget(self.accounts_layout)
