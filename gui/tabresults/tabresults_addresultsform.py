#!/usr/bin/python3

from datetime import datetime
import os

from PyQt5.QtWidgets import QDateEdit, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSpinBox, QDialog, QFrame, QSpinBox, QLineEdit, QComboBox, QMessageBox
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont, QIcon

from gui.dbhandler import balances, results
from gui.resources.fonts import TitleFont
from gui.tabresults.tabresults_formquery import AccountSelectResults
from gui.tabresults.tabresults_import_dialog import SelectTypeDialog
from gui import confighandler

RESOURCES_PATH = os.path.join(os.path.expanduser(
    '~'), '.local', 'share', 'portfolio')


class AddResultsForm(QVBoxLayout):
    """
    Form with several entries to add a result on the database
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Title
        self.title = QLabel(self.tr("Add Results"))
        self.title.setFont(TitleFont())
        self.title.setAlignment(Qt.AlignCenter)

        # First line: Date
        self.label1 = QLabel(self.tr("Date"))
        self.label1.setMinimumWidth(60)
        self.label1.setMaximumWidth(60)
        self.date_edit = QDateEdit(datetime.now())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setCalendarPopup(True)
        self.label1_checkbox = QPushButton(self.tr("Today"))
        self.label1_checkbox.setMaximumWidth(50)
        self.label1_checkbox.clicked.connect(self.setToday)

        self.line1 = QHBoxLayout()
        self.line1.addWidget(self.label1)
        self.line1.addWidget(self.date_edit)
        self.line1.addWidget(self.label1_checkbox)

        # Second Line: Account
        self.label2 = QLabel(self.tr("Account"))
        self.label2.setMinimumWidth(60)
        self.label2.setMaximumWidth(60)
        self.account_select = AccountSelectResults()
        currentaccounts = [a[0] for a in balances.getAllAccounts()]
        self.account_select.addItems(currentaccounts)

        self.line2 = QHBoxLayout()
        self.line2.addWidget(self.label2)
        self.line2.addWidget(self.account_select, Qt.AlignLeft)

        # Third Line: Amount
        self.label3 = QLabel(self.tr("Amount"))
        self.label3.setMinimumWidth(60)
        self.label3.setMaximumWidth(60)
        self.amount_select = QSpinBox()
        self.amount_select.setSuffix(" €")
        self.amount_select.setMinimum(-2147483647)
        self.amount_select.setMaximum(2147483647)
        self.amount_select.setAccelerated(True)
        self.adjust_by_new_balance = QPushButton(self.tr("Adjust"))
        self.adjust_by_new_balance.clicked.connect(self.showAdjustDialog)

        self.line3 = QHBoxLayout()
        self.line3.addWidget(self.label3)
        self.line3.addWidget(self.amount_select, Qt.AlignLeft)
        self.line3.addWidget(self.adjust_by_new_balance)

        # Dialogs
        self.importdialog = SelectTypeDialog()

        # Buttons
        self.button_layout = QHBoxLayout()

        self.insert_button = QPushButton(self.tr("Insert"))
        self.insert_button.setMaximumWidth(50)
        self.button_layout.setAlignment(
            Qt.AlignHCenter | Qt.AlignTop)  # Centering it
        self.button_layout.setContentsMargins(
            QMargins(10, 10, 10, 10))  # A little bit of margin
        self.insert_button.clicked.connect(self.insertResult)
        self.button_layout.addWidget(
            self.insert_button, Qt.AlignVCenter)

        self.import_button = QPushButton(self.tr("Import from"))
        self.import_button.setMaximumWidth(50)
        self.import_button.clicked.connect(
            lambda: self.importdialog.setVisible(True))
        self.button_layout.addWidget(self.import_button)

        self.addWidget(self.title)
        self.addLayout(self.line1)
        self.addLayout(self.line2)
        self.addLayout(self.line3)
        self.addLayout(self.button_layout)

    def setToday(self):
        self.date_edit.setDate(datetime.now())

    def insertResult(self):
        """
        Insert current form state as a result on the database
        """
        current_date = datetime(
            self.date_edit.date().year(), self.date_edit.date(
            ).month(), self.date_edit.date().day()).timestamp()
        current_account = self.account_select.currentText()
        current_amount = self.amount_select.text()[:-2]

        results.addResult(current_date, current_account,
                          current_amount)

    def showAdjustDialog(self):
        """
        Shows Dialog to add a result by new balance
        """
        currentdate = self.date_edit.text()
        currentaccount = self.account_select.currentText().upper()
        self.adjust_by_new_balance_dlg = AdjustResultNewBalanceDialog(
            currentdate, currentaccount)
        self.adjust_by_new_balance_dlg.show()

    def setResultForm(self, date, account, amount):
        """
        Sets the form fields according as desired
        """
        self.date_edit.setDate(date)
        self.account_select.setCurrentText(account)
        self.amount_select.setValue(amount)


class AdjustResultNewBalanceDialog(QDialog):
    """
    Dialog that lets the user calculate a result to add
    such that the account gets a new selected balance
    """

    def __init__(self, date, account,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Data
        previous_balance = balances.getAccountBalance(account)
        # UI
        self.setFixedSize(250, 200)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # First Line: Date
        self.label1 = QLabel(self.tr("Date"))
        self.label1.setMinimumWidth(60)
        self.label1.setMaximumWidth(60)
        self.date = QLabel(date)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        self.line1 = QHBoxLayout()
        self.line1.addWidget(self.label1)
        self.line1.addWidget(line)
        self.line1.addWidget(self.date)
        self.layout.addLayout(self.line1)

        # Second Line: Account
        self.label2 = QLabel(self.tr("Account"))
        self.label2.setMinimumWidth(60)
        self.label2.setMaximumWidth(60)
        self.account_select = QComboBox()
        self.account_select.addItems([i[0] for i in balances.getAllAccounts()])
        self.account_select.setCurrentText(account)
        # Whenever an account is changed, we change the previousbalance
        self.account_select.currentTextChanged.connect(self.updateWithAccount)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        self.line2 = QHBoxLayout()
        self.line2.addWidget(self.label2)
        self.line2.addWidget(line)
        self.line2.addWidget(self.account_select, Qt.AlignLeft)
        self.layout.addLayout(self.line2)

        # Third Line: Previous Balance
        self.label3 = QLabel(self.tr("Previous"))
        self.label3.setMinimumWidth(60)
        self.label3.setMaximumWidth(60)
        self.previous_balance = QLineEdit()
        self.previous_balance.setText(
            str(previous_balance) + " " + confighandler.get_fiat_currency().upper())
        self.previous_balance.setReadOnly(True)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        self.line3 = QHBoxLayout()
        self.line3.addWidget(self.label3)
        self.line3.addWidget(line)
        self.line3.addWidget(self.previous_balance)
        self.layout.addLayout(self.line3)

        # Fourth Line: New Balance
        self.label4 = QLabel(self.tr("New"))
        self.label4.setMinimumWidth(60)
        self.label4.setMaximumWidth(60)
        self.new_balance = QSpinBox()
        self.new_balance.setMinimum(0)
        self.new_balance.setMaximum(999999)
        self.new_balance.setSuffix(
            " " + confighandler.get_fiat_currency().upper())
        self.new_balance.setValue(previous_balance)
        # Whenever a new balance is written, we recalculate the
        # resulting result
        self.new_balance.valueChanged.connect(self.updateResult)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        self.line4 = QHBoxLayout()
        self.line4.addWidget(self.label4)
        self.line4.addWidget(line)
        self.line4.addWidget(self.new_balance)
        self.layout.addLayout(self.line4)

        # Fifth Line: Result
        self.label5 = QLabel(self.tr("Result"))
        self.label5.setMinimumWidth(60)
        self.label5.setMaximumWidth(60)
        self.result = QLabel("")
        font = QFont()
        font.setBold(True)
        self.result.setFont(font)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        self.line5 = QHBoxLayout()
        self.line5.addWidget(self.label5)
        self.line5.addWidget(line)
        self.line5.addWidget(self.result)
        self.layout.addLayout(self.line5)

        # Add result button
        self.add_result_bttn = QPushButton("Add Result")
        self.add_result_bttn.clicked.connect(self.addResult)
        self.layout.addWidget(self.add_result_bttn)

        self.setLayout(self.layout)

    def updateResult(self):
        """
        Updates the result field as the difference between
        the previous and new balance
        """
        previousbalance = balances.getAccountBalance(
            self.account_select.currentText())
        newbalance = self.new_balance.value()

        result_amount = newbalance - previousbalance
        self.result.setText(str(result_amount) + " " +
                            confighandler.get_fiat_currency().upper())

    def updateWithAccount(self, account):
        """
        Updates the rest of fields with the new account that has been selected
        """
        previous_balance = balances.getAccountBalance(account)
        self.previous_balance.setText(str(previous_balance))
        self.new_balance.setValue(previous_balance)

    def addResult(self):
        """
        Insert current form state as a result on the database
        """
        date = datetime.strptime(self.date.text(), "%d/%m/%Y").timestamp()
        account = self.account_select.currentText()
        amount = self.result.text().split(" ")[0]

        print("Added result: ", date, account, amount)
        results.addResult(date, account, amount)

        # Set self.previous_balance with the new balance
        self.previous_balance.setText(str(self.new_balance.value()))

        # Added Message
        added_msg = QMessageBox()
        added_msg.setText("Added")
        added_msg.setWindowTitle("Added")
        added_msg.exec_()
