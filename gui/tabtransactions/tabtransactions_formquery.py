#!/usr/bin/python3

from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QBoxLayout, QVBoxLayout, QLabel, QDateEdit, QComboBox, QFormLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart

from fonts import BoldFont

from datetime import datetime
from dbhandler import db_initialize, transactions


class TransactionsQueryForm(QFormLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # First line: Start Date
        self.label1 = QLabel("Start Date")
        self.start_date_edit = QDateEdit(datetime.now())
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setCalendarPopup(True)
        # Just making sure that the start date is always before the end date
        self.start_date_edit.dateTimeChanged.connect(self.checkDates_startdate)

        self.setWidget(0, self.LabelRole, self.label1)
        self.setWidget(0, self.FieldRole, self.start_date_edit)

        # Second line: End Date
        self.label2 = QLabel("End Date")
        self.end_date_edit = QDateEdit(datetime.now())
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.end_date_edit.setCalendarPopup(True)
        # Just making sure that the end date is always after the start date
        self.end_date_edit.dateTimeChanged.connect(self.checkDates_enddate)

        self.setWidget(1, self.LabelRole, self.label2)
        self.setWidget(1, self.FieldRole, self.end_date_edit)

        # Third line: Sender Account selection
        self.label3 = QLabel("Sender Account")
        self.senderaccount_select = QComboBox()
        self.senderaccount_select.addItem("All", BoldFont())
        self.senderaccount_select.setEditable(True)
        self.senderaccount_select.setDuplicatesEnabled(False)
        currentsenderaccounts = [a[0]
                                 for a in transactions.getAllSenderAccounts()]
        self.senderaccount_select.addItems(currentsenderaccounts)

        self.setWidget(2, self.LabelRole, self.label3)
        self.setWidget(2, self.FieldRole, self.senderaccount_select)

        # Fourth line: Receiver Account selection
        self.label4 = QLabel("Receiver Account")
        self.receiveraccount_select = QComboBox()
        self.receiveraccount_select.addItem("All", BoldFont())
        self.receiveraccount_select.setEditable(True)
        self.receiveraccount_select.setDuplicatesEnabled(False)
        currentreceiveraccounts = [a[0]
                                   for a in transactions.getAllReceiverAccounts()]
        self.receiveraccount_select.addItems(currentreceiveraccounts)

        self.setWidget(3, self.LabelRole, self.label4)
        self.setWidget(3, self.FieldRole, self.receiveraccount_select)

    def getCurrentQuery(self):
        # Returns tuple with the start date, end date and current sender and receiver accounts of the query form
        startdate = datetime.strptime(
            self.start_date_edit.date().toString("dd.MM.yyyy"), "%d.%m.%Y")  # Y in caps because its expressed in 4 digits
        enddate = datetime.strptime(
            self.end_date_edit.date().toString("dd.MM.yyyy"), "%d.%m.%Y")  # Y in caps because its expressed in 4 digits
        senderaccount = self.senderaccount_select.currentText()
        receiveraccount = self.receiveraccount_select.currentText()

        return (startdate, enddate, senderaccount, receiveraccount)

    def checkDates_startdate(self):
        if self.end_date_edit.dateTime() < self.start_date_edit.dateTime():
            # set end date same as start date
            self.end_date_edit.setDate(self.start_date_edit.date())

    def checkDates_enddate(self):
        if self.start_date_edit.dateTime() > self.end_date_edit.dateTime():
            # viceversa
            self.start_date_edit.setDate(self.end_date_edit.date())
