#!/usr/bin/python3

from PyQt5.QtWidgets import QLineEdit, QDateEdit, QVBoxLayout, QLabel, QFormLayout, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox
from PyQt5.QtCore import Qt, QMargins
from datetime import datetime

from tabresults.tabresults_formquery import AccountSelectResults
from fonts import TitleFont
from tabresults.tabresults_import_dialog import SelectTypeDialog
from dbhandler import balances, results


class AddResultsForm(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__()

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
        self.label2.setMaximumWidth(70)
        self.account_select = AccountSelectResults()
        currentaccounts = [a[0] for a in balances.getAllAccounts()]
        self.account_select.addItems(currentaccounts)

        self.line2 = QHBoxLayout()
        self.line2.addWidget(self.label2)
        self.line2.addWidget(self.account_select, Qt.AlignLeft)

        # Third Line: Amount
        self.label3 = QLabel(self.tr("Amount"))
        self.label3.setMaximumWidth(70)
        self.amount_select = QSpinBox()
        self.amount_select.setSuffix(" €")
        self.amount_select.setMinimum(-2147483647)
        self.amount_select.setMaximum(2147483647)
        self.amount_select.setAccelerated(True)

        self.line3 = QHBoxLayout()
        self.line3.addWidget(self.label3)
        self.line3.addWidget(self.amount_select, Qt.AlignLeft)

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
        self.current_date = datetime(
            self.date_edit.date().year(), self.date_edit.date(
            ).month(), self.date_edit.date().day()).timestamp()
        self.current_account = self.account_select.currentText()
        self.current_amount = self.amount_select.text()[:-2]

        results.addResult(self.current_date, self.current_account,
                          self.current_amount)
