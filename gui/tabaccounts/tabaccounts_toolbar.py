# /usr/bin/python3

from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QToolBar, QAction, QComboBox, QDialog, QFormLayout, QSizePolicy
from PyQt5.QtWidgets import QLineEdit, QLabel, QDoubleSpinBox, QVBoxLayout, QMessageBox, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

import os
import time

from gui.tabaccounts.tabaccounts_toolbar_dialogs import AddAccountDialog, RemoveAccountDialog, EditAccountDialog
from gui import confighandler

RESOURCES_PATH = confighandler.getUserDataPath()


class AccountsToolBar(QToolBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Account Action
        self.addaccount_action = QAction(self.tr("Add Account"), self)
        self.addaccount_action.setStatusTip(
            self.tr("Create an account and add it on the database"))
        self.addaccount_action.triggered.connect(self.addAccountActionClick)
        self.addAction(self.addaccount_action)

        self.add_account_dialog = AddAccountDialog()
        self.add_account_dialog.setVisible(False)

        # Edit Account Action
        """
        Still not ready for use. Things like icon changing and how to handle 
        previous results/transactions from the account have to be considered
        """
#        self.editaccount_action = QAction(self.tr("Edit Account"), self)
#        self.editaccount_action.setStatusTip(
#            self.tr("Change account balance/info"))
#        self.editaccount_action.triggered.connect(self.editAccountActionClick)
#        self.addAction(self.editaccount_action)

        #self.edit_account_dialog = EditAccountDialog()

        # Remove Account Action
        self.removeaccount_action = QAction(self.tr("Remove Account"), self)
        self.removeaccount_action.setStatusTip(
            self.tr("Delete account from the database"))
        self.removeaccount_action.triggered.connect(
            self.removeAccountActionClick)
        self.addAction(self.removeaccount_action)

        self.remove_account_dialog = RemoveAccountDialog(self)

        # Spacer
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        empty.setStyleSheet('background-color : transparent')
        self.addWidget(empty)
        self.addSeparator()

        # Refresh Action
        self.refresh_action = QAction(self.tr("Refresh"), self)
        self.refresh_action.setIcon(
            QIcon(os.path.join(RESOURCES_PATH, 'refresh.png')))
        self.refresh_action.setStatusTip(
            self.tr("Refresh all accounts to reflect changes"))
        self.addAction(self.refresh_action)

    def addAccountActionClick(self, event):
        "To add an accounts, a dialog will be displayed with a form"
        self.add_account_dialog.setVisible(True)

    def editAccountActionClick(self, event):
        self.edit_account_dialog.setVisible(True)

    def removeAccountActionClick(self, event):
        self.remove_account_dialog.setVisible(True)
