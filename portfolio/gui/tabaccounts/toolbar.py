# /usr/bin/python3

from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QToolBar, QAction, QComboBox, QDialog, QFormLayout, QSizePolicy
from PyQt5.QtWidgets import QLineEdit, QLabel, QDoubleSpinBox, QVBoxLayout, QMessageBox, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

import os
import time

from portfolio.gui.tabaccounts.toolbar_dialogs import AddAccountDialog, RemoveAccountDialog, EditAccountDialog
from portfolio.utils import confighandler, resource_gatherer


class AccountsToolBar(QToolBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Account Action
        self.addaccount_action = QAction(self.tr("Add Account"), self)
        self.addaccount_action.setStatusTip(
            self.tr("Create an account and add it on the database"))
        self.addaccount_action.triggered.connect(self.addAccountActionClick)
        self.addAction(self.addaccount_action)

        self.add_account_dialog = AddAccountDialog(self)
        self.add_account_dialog.setVisible(False)

        # Edit Account Action
        # TODO

        # Remove Account Action
        self.removeaccount_action = QAction(self.tr("Remove Account"), self)
        self.removeaccount_action.setStatusTip(
            self.tr("Delete account from the database"))
        self.removeaccount_action.triggered.connect(
            self.removeAccountActionClick)
        self.addAction(self.removeaccount_action)

        self.remove_account_dialog = RemoveAccountDialog(self)
        self.remove_account_dialog.setVisible(False)

        # Spacer
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        empty.setStyleSheet('background-color : transparent')
        self.addWidget(empty)
        self.addSeparator()

        # Refresh Action
        self.refresh_action = QAction(self.tr("Refresh"), self)
        self.refresh_action.setIcon(
            resource_gatherer.get_resource_QIcon('refresh.png'))
        self.refresh_action.setStatusTip(
            self.tr("Refresh all accounts to reflect changes"))
        self.addAction(self.refresh_action)

    def addAccountActionClick(self, event):
        "To add an account, a dialog will be displayed with a form"
        self.add_account_dialog.setVisible(True)

    def editAccountActionClick(self, event):
        self.edit_account_dialog.setVisible(True)

    def removeAccountActionClick(self, event):
        self.remove_account_dialog.setVisible(True)
