#!/usr/bin/python3
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QDialog, QPushButton, QLineEdit, QDoubleSpinBox, QFormLayout, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QObject

import os

from gui.dbhandler import balances, costbasis


RESOURCES_PATH = os.path.join(os.path.expanduser(
    '~'), '.local', 'share', 'portfolio')


class AddAccountDialog(QDialog):

    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

        self.setWindowTitle(self.tr("Add Account"))
        self.layout = QVBoxLayout()
        self.formlayout = QFormLayout()

        # Account Name
        self.name = QLabel(self.tr("Account Name"))
        self.name_edit = QLineEdit()

        self.formlayout.setWidget(0, self.formlayout.LabelRole, self.name)
        self.formlayout.setWidget(0, self.formlayout.FieldRole, self.name_edit)

        # Starting Amount
        self.startingamount = QLabel(self.tr("Starting Amount"))
        self.startingamount_edit = QDoubleSpinBox()
        self.startingamount_edit.setValue(0)
        self.startingamount_edit.setMaximum(10000000000)
        self.startingamount_edit.setSuffix(" EUR")

        self.formlayout.setWidget(
            1, self.formlayout.LabelRole, self.startingamount)
        self.formlayout.setWidget(1, self.formlayout.FieldRole,
                                  self.startingamount_edit)

        # Functionality
        self.create_bttn = QPushButton(self.tr("Create"))
        self.create_bttn.clicked.connect(self.createAccount)

        self.layout.addLayout(self.formlayout)
        self.layout.addWidget(self.create_bttn)
        self.setLayout(self.layout)
        self.show()

        # Signals
        self.customSignal = SignalAccountAdded()

    def createAccount(self):
        self.current_form_state = (
            self.name_edit.text(), int(float(self.startingamount_edit.text()[:-4])))

        balances.addAccount(
            self.current_form_state[0], self.current_form_state[1])

        self.customSignal.accountAdded.emit()
        self.close()


class EditAccountDialog(QDialog):

    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

        self.setWindowTitle(self.tr("Edit Account"))
        self.layout = QVBoxLayout()

        # Account selection
        self.account_selection_combobox = QComboBox()
        for acc in balances.getAllAccounts():
            self.account_selection_combobox.addItem(acc[0])

        # Edit account form
        self.layout_form = QFormLayout()
        self.name_change_label = QLabel(self.tr("New Name"))
        self.name_change_field = QLineEdit()
        self.layout_form.setWidget(
            0, self.layout_form.LabelRole, self.name_change_label)
        self.layout_form.setWidget(
            0, self.layout_form.FieldRole, self.name_change_field)

        self.balance_change_label = QLabel(self.tr("Balance"))
        self.balance_change_field = QLineEdit()
        self.balance_change_field.setReadOnly(True)
        self.layout_form.setWidget(
            1, self.layout_form.LabelRole, self.balance_change_label)
        self.layout_form.setWidget(
            1, self.layout_form.FieldRole, self.balance_change_field)  # We'll tell the user that any account balance change should be done differently

        # Save changes button
        self.save_changes_bttn = QPushButton(self.tr("Save Changes"))
        self.save_changes_bttn.clicked.connect(self.saveChanges)

        self.layout.addWidget(self.account_selection_combobox)
        self.layout.addSpacing(30)
        self.layout.addLayout(self.layout_form)
        self.layout.addWidget(self.save_changes_bttn)
        self.setLayout(self.layout)

        # Functionality
        self.account_selection_combobox.currentTextChanged.connect(
            self.fillFields)

        # Initialization
        self.fillFields(self.account_selection_combobox.currentText())

        # Custom Signal
        self.customSignal = SignalEditAccount()

    def fillFields(self, account_name):
        """ Fill Form fields with current combobox selection """
        account_balance = balances.getAccount(account_name)
        if account_balance != []:
            account_balance = account_balance[1]
        self.name_change_field.setText(account_name)
        self.balance_change_field.setText(str(account_balance))

    def saveChanges(self):
        # Edit account on Database
        accountname = self.account_selection_combobox.currentText()
        new_accountname = self.name_change_field.text()
        balances.editAccount(accountname, new_accountname)
        costbasis.editCostBasis(accountname, new_accountname)

        self.customSignal.accountEdited.emit([
            self.account_selection_combobox.currentText(), self.name_change_field.text()])  # Triggered with name change info so that the account label can be changed from the outside

        self.close()


class RemoveAccountDialog(QDialog):

    def __init__(self, *args, **kwargs):
        """ A simple dialog to select between the current account on the db and remove one of them """
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Remove Account"))
        self.layout = QVBoxLayout()
        self.formlayout = QFormLayout()

        # Account Name
        self.name = QLabel(self.tr("Account Name"))
        self.name_select = QComboBox()
        for acc in balances.getAllAccounts():
            self.name_select.addItem(acc[0])

        self.formlayout.setWidget(0, self.formlayout.LabelRole, self.name)
        self.formlayout.setWidget(
            0, self.formlayout.FieldRole, self.name_select)

        # Functionality
        self.remove_bttn = QPushButton(self.tr("Remove"))
        self.remove_account_warning = RemoveAccountWarning(self)
        self.remove_bttn.clicked.connect(self.showWarning)

        self.layout.addLayout(self.formlayout)
        self.layout.addWidget(self.remove_bttn)
        self.setLayout(self.layout)

    def showWarning(self):
        self.close()
        selected_account = self.name_select.currentText()
        self.remove_account_warning.setSelectedAccount(selected_account)
        self.remove_account_warning.setVisible(True)


class RemoveAccountWarning(QDialog):

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warning_lyt = QVBoxLayout()
        self.warning_lyt_top = QHBoxLayout()

        self.icon = QLabel()
        pxmp = QPixmap(os.path.join(RESOURCES_PATH, "warning.svg")
                       ).scaledToHeight(40)
        self.icon.setPixmap(pxmp)
        self.warningtext = QLabel(
            self.tr("Are you sure? \nThis cannot be undone"))

        self.warning_lyt_top.addWidget(self.icon)
        self.warning_lyt_top.addWidget(self.warningtext)

        # Remove button
        self.warning_bttn = QPushButton()
        self.warning_bttn.clicked.connect(
            lambda: self.removeAccount())

        self.warning_lyt.addLayout(self.warning_lyt_top)
        self.warning_lyt.addWidget(self.warning_bttn)
        self.setLayout(self.warning_lyt)

        # Data
        self.selected_account = ' '

    def setSelectedAccount(self, selected_account):
        self.selected_account = selected_account
        self.warning_bttn.setText(
            self.tr("Yes, remove {}".format(selected_account)))

    def removeAccount(self):
        # Remove from Database
        balances.deleteAccount(self.selected_account)

        # Remove from GUI
        """ For now, it will be required to restart the app for the changes to take effect """

        self.warning_lyt.addWidget(
            QLabel("Done. Restart required for changes to take effect"))
        close_bttn = QPushButton(self.tr("Close App"))

        self.warning_lyt.addWidget(close_bttn)
        close_bttn.clicked.connect(lambda: self.parent().parent().parent(
        ).parent().parent().parent().parent().close())  # Closing MainWindow

        # Deleting old widgets from layout
        self.warningtext.deleteLater()
        self.warning_bttn.deleteLater()


# Custom Signals
class SignalEditAccount(QObject):
    accountEdited = pyqtSignal(list)


class SignalAccountAdded(QObject):
    accountAdded = pyqtSignal()
