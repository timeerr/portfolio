# /usr/bin/python3

import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QMargins

from portfolio.gui.tabaccounts.toolbar import AccountsToolBar
from portfolio.gui.tabaccounts.main_layout import AccountsLayout


class TabAccounts(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- UI ----
        self.setWindowTitle(self.tr("Accounts"))
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(QMargins(0, 0, 0, 0))

        # ---- Content ----
        # Toolbar
        self.accounts_toolbar = AccountsToolBar(self)
        self.mainlayout.addWidget(self.accounts_toolbar)
        # Layout
        self.accounts_layout = AccountsLayout()
        self.accounts_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.mainlayout.addWidget(self.accounts_layout)

        self.setLayout(self.mainlayout)

        # ---- Functionality ----
        # Refresh
        self.accounts_toolbar.refresh_action.triggered.connect(
            self.refreshBalances)
        self.accounts_toolbar.add_account_dialog.accountAdded.connect(
            self.refreshBalances)
        self.accounts_toolbar.remove_account_dialog.remove_account_warning.accountRemoved.connect(
            self.refreshBalances)

    def refreshBalances(self):
        """ Clears balances and re-reads them on database """
        # Refresh dialogs' data
        self.accounts_toolbar.remove_account_dialog.set_combobox()
        # Refresh layout
        self.accounts_layout.deleteLater()
        logging.info("TabAccounts Layout Refreshed")
        self.accounts_layout = AccountsLayout()
        self.mainlayout.addWidget(self.accounts_layout)
