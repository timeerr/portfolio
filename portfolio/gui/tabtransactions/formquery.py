#!/usr/bin/python3
"""
Form to get transactions form the database
"""

from datetime import datetime

from PyQt5.QtWidgets import QLabel, QDateEdit, QComboBox, QFormLayout

from portfolio.gui.ui_components.fonts import BoldFont
from portfolio.db.fdbhandler import transactions


class TransactionsQueryForm(QFormLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        # Third line: Sender Account selection
        self.label3 = QLabel(self.tr("Sender Account"))
        self.senderaccount_select = QComboBox()
        self.senderaccount_select.addItem("All", BoldFont())
        self.senderaccount_select.setEditable(True)
        self.senderaccount_select.setDuplicatesEnabled(False)
        currentsenderaccounts = [a[0]
                                 for a in transactions.get_all_sender_accounts()]
        self.senderaccount_select.addItems(currentsenderaccounts)

        self.setWidget(2, self.LabelRole, self.label3)
        self.setWidget(2, self.FieldRole, self.senderaccount_select)

        # Fourth line: Receiver Account selection
        self.label4 = QLabel(self.tr("Receiver Account"))
        self.receiveraccount_select = QComboBox()
        self.receiveraccount_select.addItem("All", BoldFont())
        self.receiveraccount_select.setEditable(True)
        self.receiveraccount_select.setDuplicatesEnabled(False)
        currentreceiveraccounts = [a[0]
                                   for a in transactions.get_all_receiver_accounts()]
        self.receiveraccount_select.addItems(currentreceiveraccounts)

        self.setWidget(3, self.LabelRole, self.label4)
        self.setWidget(3, self.FieldRole, self.receiveraccount_select)

    def getCurrentQuery(self):
        """
        Returns tuple with the start date, end date and
        current sender and receiver accounts of the query form
        """
        startdate = datetime.strptime(
            self.start_date_edit.date().toString("dd.MM.yyyy"), "%d.%m.%Y")
        enddate = datetime.strptime(
            self.end_date_edit.date().toString("dd.MM.yyyy"), "%d.%m.%Y")
        senderaccount = self.senderaccount_select.currentText()
        receiveraccount = self.receiveraccount_select.currentText()

        return (startdate, enddate, senderaccount, receiveraccount)

    def checkDates_startdate(self):
        """
        Making sure that the start date is not bigger than the end date
        """
        if self.end_date_edit.dateTime() < self.start_date_edit.dateTime():
            # set end date same as start date
            self.end_date_edit.setDate(self.start_date_edit.date())

    def checkDates_enddate(self):
        """
        Making sure that the start date is not bigger than the end date
        """
        if self.start_date_edit.dateTime() > self.end_date_edit.dateTime():
            # viceversa
            self.start_date_edit.setDate(self.end_date_edit.date())
