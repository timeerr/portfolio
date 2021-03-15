#!/usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QBoxLayout, QVBoxLayout, QLabel, QComboBox, QDateEdit, QFormLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt

from gui.resources.fonts import BoldFont

from datetime import datetime
from gui.dbhandler import balances


class ResultsQueryForm(QFormLayout):

    def __init__(self):
        super().__init__()

        # First line: Start Date
        self.label1 = QLabel(self.tr("Start Date"))
        self.start_date_edit = QDateEdit(datetime.now())
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setCalendarPopup(True)
        # Just making sure that the start date is always before the end date
        self.start_date_edit.dateTimeChanged.connect(self.checkDates_startdate)

        self.setWidget(0, self.LabelRole, self.label1)
        self.setWidget(0, self.FieldRole, self.start_date_edit)

        # Second line: End Date
        self.label2 = QLabel(self.tr("End Date"))
        self.end_date_edit = QDateEdit(datetime.now())
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.end_date_edit.setCalendarPopup(True)
        # Just making sure that the end date is always after the start date
        self.end_date_edit.dateTimeChanged.connect(self.checkDates_enddate)

        self.setWidget(1, self.LabelRole, self.label2)
        self.setWidget(1, self.FieldRole, self.end_date_edit)

        # Third line: Account selection
        self.label3 = QLabel(self.tr("Account"))
        self.account_select = AccountSelectResults(is_query=True)
        currentaccounts = [a[0] for a in balances.getAllAccounts()]
        self.account_select.addItems(currentaccounts)
        # Initializing a new attr, that we will use on parents to get current selected account
        self.currentaccount = self.account_select.currentText()
        # If current account is changed, we get the signal and process it
        self.account_select.currentIndexChanged.connect(self.getCurrentAccount)

        self.setWidget(2, self.LabelRole, self.label3)
        self.setWidget(2, self.FieldRole, self.account_select)

    def getCurrentAccount(self):
        return self.account_select.currentText()

    def getCurrentQuery(self):
        # Returns tuple with the start date, end date and current account of the query form
        return (self.start_date_edit.dateTime(), self.end_date_edit.dateTime(), self.account_select.currentText())

    def checkDates_startdate(self):
        if self.end_date_edit.dateTime() < self.start_date_edit.dateTime():
            # set end date same as start date
            self.end_date_edit.setDate(self.start_date_edit.date())

    def checkDates_enddate(self):
        if self.start_date_edit.dateTime() > self.end_date_edit.dateTime():
            # viceversa
            self.start_date_edit.setDate(self.end_date_edit.date())


class AccountSelectResults(QComboBox):
    def __init__(self, is_query=False):
        super().__init__()

        if is_query:
            # If we use this ComboBox for results addition, "All" is not necessary
            self.addItem("All", BoldFont())
        self.setEditable(True)
        self.setDuplicatesEnabled(False)
