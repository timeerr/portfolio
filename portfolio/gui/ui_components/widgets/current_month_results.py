#!/usr/bin/python3

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from portfolio.utils import confighandler
from portfolio.db import dbhandler
from portfolio.gui.ui_components.styles import LinearStyle
from portfolio.gui.ui_components.charts.total_wealth_history import TotalWealthHistoryChartView


class CurrentMonthResultsWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("lastmonthwidget")

        # Background image
        self.setStyleSheet(LinearStyle.get(self.objectName(), '#273B4F'))

        # Size
        self.setMaximumSize(240, 235)

        # ---- Content ----
        self.layout = QVBoxLayout()
        # -- Header --
        self.header = QLabel(self.tr("Last Month"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-top: 15; margin-left: 8 ")
        font = QFont('Roboto', pointSize=20, weight=QFont.Bold)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # -- Second Row : Changes --
        self.second_row = QHBoxLayout()
        self.second_row.setSpacing(0)
        self.second_row.setContentsMargins(0, 0, 0, 0)
        # Change (Fiat)
        change_fiat_value = dbhandler.get_change_last_month()
        change_fiat_value_str = "+" + \
            str(change_fiat_value) if change_fiat_value >= 0 else str(
                change_fiat_value)
        self.change_fiat = QLabel(change_fiat_value_str)
        self.change_fiat.setStyleSheet(
            "background-color: rgba(0,0,0,0); color:#D3EABD; margin-left: 8")
        font = QFont('Roboto', pointSize=15)
        self.change_fiat.setFont(font)
        self.change_fiat.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.second_row.addWidget(self.change_fiat)
        # Fiat label
        self.fiat_label = QLabel(confighandler.get_fiat_currency().upper())
        self.fiat_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);color:#D3EABD; margin-top:10px")
        self.fiat_label.setFont(QFont('Roboto', pointSize=7))
        self.fiat_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.second_row.addWidget(self.fiat_label)
        # Change (%)
        first_total_wealth_current_month = dbhandler.get_first_total_wealth_current_month()
        change_last_month = dbhandler.get_change_last_month()
        if first_total_wealth_current_month > 0:
            change_percentage = 100 * \
                (change_last_month /
                 first_total_wealth_current_month)
            change_percentage = round(change_percentage, 1)

            change_percentage_str = "+{}%".format(str(
                change_percentage)) if change_percentage >= 0 else "{}%".format(str(change_percentage))
        else:
            # No change this month
            change_percentage_str = "0%"

        self.change_percentage = QLabel(change_percentage_str)
        self.change_percentage.setStyleSheet(
            "background-color: rgba(0,0,0,0);color:#D3EABD; margin-right: 8")
        font = QFont()
        font.setFamily("Roboto")
        font.setPointSize(15)
        self.change_percentage.setFont(font)
        self.change_percentage.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.second_row.addWidget(self.change_percentage)

        # -- Chart --
        self.lastmonthchart = TotalWealthHistoryChartView(self)
        data = dbhandler.get_total_wealth_by_day_current_month()
        self.lastmonthchart.setupChartWithData(data)

        self.layout.addWidget(self.header)
        self.layout.addLayout(self.second_row)
        self.layout.addWidget(self.lastmonthchart)

        self.setLayout(self.layout)
