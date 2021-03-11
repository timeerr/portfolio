# /usr/bin/python3

from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QToolBar, QAction, QComboBox, QDialog, QFormLayout, QLineEdit, QLabel, QDoubleSpinBox, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

import os
import time

from tabaccounts.tabaccounts_toolbar_dialogs import AddAccountDialog, RemoveAccountDialog, EditAccountDialog


class AccountsToolBar(QToolBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Account Action
        self.addaccount_action = QAction("Add Account", self)
        self.addaccount_action.setStatusTip(
            "Create an account and add it on the database")
        self.addaccount_action.triggered.connect(self.addAccountActionClick)
        self.addAction(self.addaccount_action)

        self.add_account_dialog = AddAccountDialog()
        self.add_account_dialog.setVisible(False)

        # Edit Account Action
        self.editaccount_action = QAction("Edit Account", self)
        self.editaccount_action.setStatusTip("Change account balance/info")
        self.editaccount_action.triggered.connect(self.editAccountActionClick)
        self.addAction(self.editaccount_action)

        self.edit_account_dialog = EditAccountDialog()

        # Remove Account Action
        self.removeaccount_action = QAction("Remove Account", self)
        self.removeaccount_action.setStatusTip(
            "Delete account from the database")
        self.removeaccount_action.triggered.connect(
            self.removeAccountActionClick)
        self.addAction(self.removeaccount_action)

        self.remove_account_dialog = RemoveAccountDialog(self)

    def addAccountActionClick(self, event):
        "To add an accounts, a dialog will be displayed with a form"
        self.add_account_dialog.setVisible(True)

    def editAccountActionClick(self, event):
        self.edit_account_dialog.setVisible(True)

    def removeAccountActionClick(self, event):
        self.remove_account_dialog.setVisible(True)
