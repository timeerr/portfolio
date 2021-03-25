#!/usr/bin/python3
"""
Form to add results on database
"""

from datetime import datetime

from PyQt5.QtWidgets import QLabel, QComboBox, QDateEdit, QFormLayout

from gui.dbhandler import balances, strategies
from gui.resources.fonts import BoldFont


class ResultsQueryForm(QFormLayout):

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

        # Third line: Account selection
        self.label3 = QLabel(self.tr("Account"))
        self.account_select = QComboBox()
        all_accounts = balances.getAllAccountNames()
        self.account_select.addItem("All")
        self.account_select.addItems(all_accounts)

        self.setWidget(2, self.LabelRole, self.label3)
        self.setWidget(2, self.FieldRole, self.account_select)

        # Fourth Line: Strategy Selection
        self.label4 = QLabel(self.tr("Strategy"))
        self.strategy_select = QComboBox()
        all_strategies = strategies.getAllStrategyNames()
        self.strategy_select.addItem("All")
        self.strategy_select.addItems(all_strategies)

        self.setWidget(3, self.LabelRole, self.label4)
        self.setWidget(3, self.FieldRole, self.strategy_select)

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
