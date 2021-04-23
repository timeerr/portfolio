#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtWidgets import QDateEdit, QLabel, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QSpinBox, QCheckBox, QButtonGroup
from PyQt5.QtCore import Qt, QMargins

from gui.dbhandler import transactions, balances
from gui.resources.fonts import TitleFont


class AddTransactionsForm(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Title
        self.title = QLabel(self.tr("Add Transaction"))
        self.title.setFont(TitleFont())
        self.title.setAlignment(Qt.AlignCenter)

        # First line: Date
        self.label1 = QLabel(self.tr("Date"))
        # self.label1.setMinimumWidth(120)
        self.label1.setMaximumWidth(120)
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
        self.label2 = QLabel(self.tr("Sender Account"))
        self.label2.setMinimumWidth(120)
        self.label2.setMaximumWidth(120)
        self.senderaccount_select = QComboBox()
        self.senderaccount_select.setEditable(True)
        self.senderaccount_select.setDuplicatesEnabled(False)
        currentaccounts = [a[0]
                           for a in balances.getAllAccounts()]
        self.senderaccount_select.addItems(currentaccounts)

        self.line2 = QHBoxLayout()
        self.line2.addWidget(self.label2)
        self.line2.addWidget(self.senderaccount_select, Qt.AlignLeft)

        # Third Line: Receiver Account
        self.label3 = QLabel(self.tr("Receiver Account"))
        self.label3.setMinimumWidth(120)
        self.label3.setMaximumWidth(120)
        self.receiveraccount_select = QComboBox()
        self.receiveraccount_select.setEditable(True)
        self.receiveraccount_select.setDuplicatesEnabled(False)
        currentaccounts = [a[0]
                           for a in balances.getAllAccounts()]
        self.receiveraccount_select.addItems(currentaccounts)
        self.receiveraccount_select.setCurrentIndex(1)

        self.line3 = QHBoxLayout()
        self.line3.addWidget(self.label3)
        self.line3.addWidget(self.receiveraccount_select, Qt.AlignLeft)

        # Fourth Line: Amount
        self.label4 = QLabel(self.tr("Amount"))
        self.label4.setMinimumWidth(120)
        self.label4.setMaximumWidth(120)
        self.amount_select = QSpinBox()
        self.amount_select.setSuffix(" €")
        self.amount_select.setMinimum(0)
        self.amount_select.setMaximum(999999999)
        self.amount_select.setAccelerated(True)

        self.line4 = QHBoxLayout()
        self.line4.addWidget(self.label4)
        self.line4.addWidget(self.amount_select, Qt.AlignLeft)

        # Fifth Line: Deposit or Withdrawal
        self.group = QButtonGroup(self)
        self.deposit_checkbox = QCheckBox('Deposit')
        self.deposit_checkbox.stateChanged.connect(self.handlechecks)
        self.withdrawal_checkbox = QCheckBox('Withdrawal')
        self.withdrawal_checkbox.stateChanged.connect(self.handlechecks)
        self.transfer_checkbox = QCheckBox('Transfer')
        self.transfer_checkbox.stateChanged.connect(self.handlechecks)

        self.line5 = QHBoxLayout()
        self.line5.addWidget(self.deposit_checkbox)
        self.line5.addWidget(self.withdrawal_checkbox)
        self.line5.addWidget(self.transfer_checkbox)

        # Sixth Line: Description
        self.label6 = QLabel(self.tr("Description"))
        self.label6.setFixedWidth(120)
        self.description_edit = QLineEdit()

        self.line6 = QHBoxLayout()
        self.line6.addWidget(self.label6)
        self.line6.addWidget(self.description_edit)

        # Buttons
        self.button_layout = QHBoxLayout()

        self.insert_button = QPushButton(self.tr("Insert"))
        self.insert_button.setMaximumWidth(50)
        self.button_layout.setAlignment(
            Qt.AlignHCenter | Qt.AlignTop)  # Centering it
        self.button_layout.setContentsMargins(
            QMargins(10, 10, 10, 10))  # A little bit of margin
        self.insert_button.clicked.connect(self.insertTransaction)
        self.button_layout.addWidget(
            self.insert_button, Qt.AlignVCenter)

        self.addWidget(self.title)
        self.addLayout(self.line1)
        self.addLayout(self.line2)
        self.addLayout(self.line3)
        self.addLayout(self.line4)
        self.addLayout(self.line5)
        self.addLayout(self.line6)
        self.addLayout(self.button_layout)

        # Signal handle
        self.receiveraccount_select.currentTextChanged.connect(
            self.handleselections)
        self.senderaccount_select.currentTextChanged.connect(
            self.handleselections)

    def setToday(self):
        self.date_edit.setDate(datetime.now())

    def insertTransaction(self):
        # Current data
        self.current_date = datetime(
            self.date_edit.date().year(), self.date_edit.date(
            ).month(), self.date_edit.date().day()).timestamp()
        self.current_senderaccount = self.senderaccount_select.currentText()
        self.current_receiveraccount = self.receiveraccount_select.currentText()
        self.current_amount = int(float(self.amount_select.text()[:-2]))

        # Deposit/Withdrawal/Transfer
        if self.deposit_checkbox.isChecked():
            self.currenttype = 1
        elif self.withdrawal_checkbox.isChecked():
            self.currenttype = -1
        else:
            # No checked defaults to transfer
            self.currenttype = 0

        # If there is a new account involved, it should be created first
        all_accounts = [i[0] for i in balances.getAllAccounts()]
        if self.current_senderaccount not in all_accounts:
            balances.addAccount(self.current_senderaccount, 0)
        if self.current_receiveraccount not in all_accounts:
            balances.addAccount(self.current_receiveraccount, 0)

        # Adding the transaction on db
        transactions.addTransaction(self.current_date, self.current_senderaccount,
                                    self.current_amount, self.current_receiveraccount,
                                    self.currenttype, description=self.description_edit.text())

    def handlechecks(self, state):
        """
        Proper checkbox behavour
        """
        # Checking if state is checked
        if state == Qt.Checked:

            if self.sender() == self.deposit_checkbox:
                # making others unchecked
                self.withdrawal_checkbox.setChecked(False)
                self.transfer_checkbox.setChecked(False)

            elif self.sender() == self.withdrawal_checkbox:
                # making others unchecked
                self.deposit_checkbox.setChecked(False)
                self.transfer_checkbox.setChecked(False)

            elif self.sender() == self.transfer_checkbox:
                # making others unchecked
                self.deposit_checkbox.setChecked(False)
                self.withdrawal_checkbox.setChecked(False)

        # Now that only one checkbox is checked, we change the form according to the transfer type
        if self.deposit_checkbox.isChecked():
            self.senderaccount_select.setCurrentText("Cash")

        if self.withdrawal_checkbox.isChecked():
            self.receiveraccount_select.setCurrentText("Cash")

        else:
            pass

    def handleselections(self):
        """
        Establishing certain retrictions
        """
        if self.receiveraccount_select.currentText() == self.senderaccount_select.currentText():
            # We move the currentIndex, so that both accounts can't be the same
            self.senderaccount_select.setStyleSheet("color: red")
            self.receiveraccount_select.setStyleSheet("color:red")
            self.insert_button.hide()
        else:
            self.senderaccount_select.setStyleSheet("")
            self.receiveraccount_select.setStyleSheet("")
            self.insert_button.show()

        # 'Cash' special cases
        if self.senderaccount_select.currentText() != 'Cash' and \
                self.receiveraccount_select.currentText() != 'Cash':
            self.transfer_checkbox.setChecked(True)
