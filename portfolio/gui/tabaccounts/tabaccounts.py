# /usr/bin/python3

import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QToolBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QMargins, QSize, Qt

from portfolio.gui.ui_components.fonts import TitleFont, AccountBalanceHeaderFont, AccountBalanceTextFont
from portfolio.gui.tabaccounts.tabaccounts_toolbar import AccountsToolBar
from portfolio.gui.tabaccounts.tabaccounts_layout import AccountsLayout


class TabAccounts(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -------UI--------
        self.setWindowTitle(self.tr("Accounts"))
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(QMargins(0, 0, 0, 0))

        # ----------------- Toolbar -----------------------
        self.accounts_toolbar = AccountsToolBar(self)

        # ----------------- Accounts Layout -----------------------
        self.accounts_layout = AccountsLayout()
        self.accounts_layout.setContentsMargins(QMargins(0, 0, 0, 0))

        # -----------Functionality-----------
        # Refresh
        self.accounts_toolbar.refresh_action.triggered.connect(
            self.refreshBalances)
        self.accounts_toolbar.add_account_dialog.accountAdded.connect(
            self.refreshBalances)

        # ----------Main Layout---------
        self.mainlayout.addWidget(self.accounts_toolbar)
        self.mainlayout.addWidget(self.accounts_layout)
        self.setLayout(self.mainlayout)

    def refreshBalances(self):
        """ Clears balances and re-reads them on database """
        self.accounts_layout.deleteLater()
        print("TabAccounts Layout Refreshed")
        self.accounts_layout = AccountsLayout()
        self.mainlayout.addWidget(self.accounts_layout)
