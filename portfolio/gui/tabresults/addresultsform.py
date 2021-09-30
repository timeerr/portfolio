#!/usr/bin/python3

from datetime import datetime
import os

from PyQt5.QtWidgets import QDateEdit, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSpinBox, QDialog, QFrame, QSpinBox, QLineEdit, QComboBox, QMessageBox
from PyQt5.QtCore import Qt, QMargins, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from portfolio.utils import confighandler
from portfolio.db.fdbhandler import balances, results, strategies
from portfolio.gui.ui_components.fonts import TitleFont


class AddResultsForm(QVBoxLayout):
    """
    Form with several entries to add a result on the database
    """
    resultAdded = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Title
        self.title = QLabel(self.tr("Add Results"))
        self.title.setFont(TitleFont())
        self.title.setAlignment(Qt.AlignCenter)

        # First line: Date
        self.label1 = QLabel(self.tr("Date"))
        self.label1.setFixedWidth(80)
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
        self.label2.setFixedWidth(80)
        self.account_select = QComboBox()
        currentaccounts = [a[0] for a in balances.get_all_accounts()]
        self.account_select.addItems(currentaccounts)

        self.line2 = QHBoxLayout()
        self.line2.addWidget(self.label2)
        self.line2.addWidget(self.account_select, Qt.AlignLeft)

        # Third Line: Strategy
        self.label3 = QLabel(self.tr("Strategy"))
        self.label3.setFixedWidth(80)
        self.strategy_select = QComboBox()
        self.strategy_select.setEditable(True)
        self.strategy_select.setDuplicatesEnabled(False)
        currentstrategies = [i[0] for i in strategies.get_all_strategies()]
        self.strategy_select.addItems(currentstrategies)

        self.line3 = QHBoxLayout()
        self.line3.addWidget(self.label3)
        self.line3.addWidget(self.strategy_select, Qt.AlignLeft)

        # Fourth Line: Amount
        self.label4 = QLabel(self.tr("Amount"))
        self.label4.setFixedWidth(80)
        self.amount_select = QSpinBox()
        self.amount_select.setSuffix(" €")
        self.amount_select.setMinimum(-2147483647)
        self.amount_select.setMaximum(2147483647)
        self.amount_select.setAccelerated(True)
        self.adjust_by_new_balance = QPushButton(self.tr("Adjust"))
        self.adjust_by_new_balance.clicked.connect(self.showAdjustDialog)

        self.line4 = QHBoxLayout()
        self.line4.addWidget(self.label4)
        self.line4.addWidget(self.amount_select, Qt.AlignLeft)
        self.line4.addWidget(self.adjust_by_new_balance)

        # Fifth Line: Description
        self.label5 = QLabel(self.tr("Description"))
        self.label5.setFixedWidth(80)
        self.description_select = QLineEdit()

        self.line5 = QHBoxLayout()
        self.line5.addWidget(self.label5)
        self.line5.addWidget(self.description_select, Qt.AlignLeft)

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

        self.addWidget(self.title)
        self.addLayout(self.line1)
        self.addLayout(self.line2)
        self.addLayout(self.line3)
        self.addLayout(self.line4)
        self.addLayout(self.line5)
        self.addLayout(self.button_layout)
        self.addWidget(self.insert_button)

    def setToday(self):
        self.date_edit.setDate(datetime.now())

    def insertResult(self):
        """ Insert current form state as a result on the database """
        current_date = datetime(
            self.date_edit.date().year(), self.date_edit.date(
            ).month(), self.date_edit.date().day()).timestamp()
        current_account = self.account_select.currentText()
        current_strategy = self.strategy_select.currentText()
        current_amount = self.amount_select.text()[:-2]
        current_description = self.description_select.text()

        results.add_result(current_date, current_account,
                           current_strategy, current_amount, description=current_description)

        # Resetting Account and Strategy QComboBoxes
        self.account_select.clear()
        self.strategy_select.clear()

        currentaccounts = [a[0] for a in balances.get_all_accounts()]
        self.account_select.addItems(currentaccounts)
        currentstrategies = [i[0] for i in strategies.get_all_strategies()]
        self.strategy_select.addItems(currentstrategies)

        self.resultAdded.emit()

    def showAdjustDialog(self):
        """
        Shows Dialog to add a result by new balance
        """
        currentdate = self.date_edit.text()
        currentaccount = self.account_select.currentText()
        self.adjust_by_new_balance_dlg = AdjustResultNewBalanceDialog(
            currentdate, currentaccount)
        self.adjust_by_new_balance_dlg.show()


class AdjustResultNewBalanceDialog(QDialog):
    """
    Dialog that lets the user calculate a result to add
    such that the account gets a new selected balance
    """

    def __init__(self, date, account,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("Opening Adjust Balance Dialog from account {}".format(account))
        # Data
        previous_balance = balances.get_account_balance(account)
        # UI
        self.setFixedSize(250, 250)

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
        self.account_select.addItems(
            [i[0] for i in balances.get_all_accounts()])
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

        # Sixth Line: Strategy
        self.label6 = QLabel(self.tr("Strategy"))
        self.label6.setFixedWidth(60)
        self.strategy_select = QComboBox()
        self.strategy_select.setEditable(True)
        self.strategy_select.setDuplicatesEnabled(False)
        currentstrategies = [i[0] for i in strategies.get_all_strategies()]
        self.strategy_select.addItems(currentstrategies)

        self.line6 = QHBoxLayout()
        self.line6.addWidget(self.label6)
        self.line6.addWidget(self.strategy_select)
        self.layout.addLayout(self.line6)

        # Seventh Line: Description
        self.label7 = QLabel(self.tr("Description"))
        self.label7.setFixedWidth(60)
        self.description_select = QLineEdit()

        self.line7 = QHBoxLayout()
        self.line7.addWidget(self.label7)
        self.line7.addWidget(self.description_select)

        self.layout.addLayout(self.line7)

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
        previousbalance = balances.get_account_balance(
            self.account_select.currentText())
        newbalance = self.new_balance.value()

        result_amount = newbalance - previousbalance
        self.result.setText(str(result_amount) + " " +
                            confighandler.get_fiat_currency().upper())

    def updateWithAccount(self, account):
        """
        Updates the rest of fields with the new account that has been selected
        """
        previous_balance = balances.get_account_balance(account)
        self.previous_balance.setText(str(previous_balance))
        self.new_balance.setValue(previous_balance)

    def addResult(self):
        """ Insert current form state as a result on the database """
        date = datetime.strptime(self.date.text(), "%d/%m/%Y").timestamp()
        account = self.account_select.currentText()
        strategy = self.strategy_select.currentText()
        description = self.description_select.text()
        amount = self.result.text().split(" ")[0]

        print("Added result: ", date, account, amount)
        results.add_result(date, account, strategy,
                           amount, description=description)

        # Set self.previous_balance with the new balance
        self.previous_balance.setText(str(self.new_balance.value()))

        # Added Message
        added_msg = QMessageBox()
        added_msg.setText("Added")
        added_msg.setWindowTitle("Added")
        added_msg.exec_()
