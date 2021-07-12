#!/usr/bin/python3

import os
from datetime import datetime
import calendar

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QBoxLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QScrollArea, QDateEdit
from PyQt5.QtGui import QFont, QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import Qt, QDateTime, QEvent, QPropertyAnimation, QObject
from PyQt5.QtCore import QEasingCurve, QPoint, QSize, pyqtProperty, pyqtSignal, QDate


from portfolio.utils import confighandler
from portfolio.db import dbhandler
from portfolio.utils.prices import prices
from portfolio.db.fdbhandler import balances
from portfolio.db.cdbhandler import cbalances
from portfolio.gui.tabdashboard.charts import TotalWealthHistoryChartView, LastMonthsHistogram, TotalEquityChartView
from portfolio.gui.tabdashboard.charts import DistributionPieChart


class TotalWealthWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("totalwealthwidget")
        # Background image
        style = """#totalwealthwidget {
        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #F06814, stop:1 #E43E53);
        border-radius: 15px}"""
        self.setStyleSheet(style)

        # Size
        self.setMaximumSize(645, 213)

        # ------------ Content ------------
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)

        # --Header---
        self.header = QLabel(self.tr("Total Wealth"))
        self.header.setMaximumHeight(80)
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-top:25")
        font = QFont()
        font.setFamily("Roboto")
        font.setWeight(QFont.Bold)
        font.setPointSize(40)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.header, Qt.AlignCenter)

        # -- Amount Layout --
        self.amountlyt = QHBoxLayout()
        self.amountlyt.setSpacing(0)

        # - Amount Label -
        totalwealth_portfolio = balances.get_total_balance_all_accounts()
        totalwealth_cportfolio = prices.btc_to_fiat(
            cbalances.get_total_balance_all_accounts())
        totalwealth_amount = int(
            totalwealth_portfolio + totalwealth_cportfolio)
        self.amount_label = QLabel(str(totalwealth_amount))
        self.amount_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-left:60; margin-right: 0")
        font = QFont()
        font.setFamily("Inter")
        font.setWeight(QFont.Medium)
        font.setPointSize(40)
        self.amount_label.setFont(font)
        self.amount_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # - Fiat Label -
        self.fiat_label = QLabel(confighandler.get_fiat_currency().upper())
        self.fiat_label.setMaximumHeight(40)
        self.fiat_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-top:15;margin-left:0;margin-right:0")
        font = QFont()
        font.setFamily("Inter")
        font.setPointSize(18)
        self.fiat_label.setFont(font)
        self.fiat_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # - Chart -
        self.chart = TotalWealthHistoryChartView()
        data = dbhandler.get_wealth_by_day()
        self.chart.setupChartWithData(data)

        # - Percentage -
        # The percentage is the difference between the first balance history and the last one
        first_balance = dbhandler.get_first_balance()
        last_balance = dbhandler.get_last_balance()

        if first_balance != 0:
            percentage = ((last_balance/first_balance)-1)*100
            if percentage > 0:
                percentage_str = "+{}%".format(round(percentage, 1))
            else:
                percentage_str = "{}%".format(round(percentage, 1))
        else:
            # No first balance, so no change
            percentage_str = "na"

        self.percentage_label = QLabel(percentage_str)
        self.percentage_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-right:60")
        font = QFont()
        font.setFamily("Inter")
        font.setPointSize(24)
        self.percentage_label.setFont(font)
        self.percentage_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.amountlyt.addWidget(self.amount_label)
        self.amountlyt.addWidget(self.fiat_label)
        self.amountlyt.addWidget(self.chart)
        self.amountlyt.addWidget(self.percentage_label)

        self.layout.addLayout(self.amountlyt)

        self.setLayout(self.layout)


class LastMonthWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("lastmonthwidget")

        # Background image
        style = """#lastmonthwidget {
        background-color: #273B4F;
        border-radius: 15px}"""
        self.setStyleSheet(style)

        # Size
        self.setMaximumSize(240, 235)

        # ---------------------------------
        # ------------ Content ------------
        # ---------------------------------
        self.layout = QVBoxLayout()

        # ------ Header --------
        self.header = QLabel(self.tr("Last Month"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-top: 15; margin-left: 8 ")
        font = QFont()
        font.setFamily("Roboto")
        font.setWeight(QFont.Bold)
        font.setPointSize(20)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # ------ Second Row : Changes --------
        self.second_row = QHBoxLayout()
        self.second_row.setSpacing(0)
        self.second_row.setContentsMargins(0, 0, 0, 0)

        # -- Change (Fiat) --
        change_fiat_value = dbhandler.get_change_last_month()
        change_fiat_value_str = "+" + \
            str(change_fiat_value) if change_fiat_value >= 0 else str(
                change_fiat_value)

        self.change_fiat = QLabel(change_fiat_value_str)
        self.change_fiat.setStyleSheet(
            "background-color: rgba(0,0,0,0); color:#D3EABD; margin-left: 8")
        font = QFont()
        font.setFamily("Roboto")
        font.setPointSize(15)
        self.change_fiat.setFont(font)
        self.change_fiat.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.second_row.addWidget(self.change_fiat)

        # -- Fiat label --
        self.fiat_label = QLabel(confighandler.get_fiat_currency().upper())
        self.fiat_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);color:#D3EABD; margin-top:10px")
        font = QFont()
        font.setFamily("Roboto")
        font.setPointSize(7)
        self.fiat_label.setFont(font)
        self.fiat_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.second_row.addWidget(self.fiat_label)

        # -- Change (%) --
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

        # ------ Chart --------
        self.lastmonthchart = TotalWealthHistoryChartView(self)
        data = dbhandler.get_total_wealth_by_day_current_month()
        self.lastmonthchart.setupChartWithData(data)

        self.layout.addWidget(self.header)
        self.layout.addLayout(self.second_row)
        self.layout.addWidget(self.lastmonthchart)

        self.setLayout(self.layout)


class LastMonthsHistogramWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("lastmonthshistogram")

        # Background image
        style = """#lastmonthshistogram {
        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #36526E, stop:1 #57616B);
        border-radius: 15px}"""
        self.setStyleSheet(style)

        # Size
        self.setMaximumSize(375, 235)

        # ---------------------------------
        # ------------ Content ------------
        # ---------------------------------
        self.layout = QVBoxLayout()

        # ------ Header --------
        self.header = QLabel(self.tr("Last Months"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-top: 15; margin-left: 8 ")
        font = QFont()
        font.setFamily("Roboto")
        font.setWeight(QFont.Bold)
        font.setPointSize(20)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # ------ Histogram -------
        self.histogram = LastMonthsHistogram()
        self.histogram.setupChartWithData()

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.histogram)

        self.setLayout(self.layout)


class TotalEquityWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("totalequity")

        # Background image
        style = """#totalequity {
        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #506273, stop:1 #8997A6);
        border-radius: 15px}"""
        self.setStyleSheet(style)

        #  Size
        self.setMaximumSize(645, 396)

        # ------------ Content ------------
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(20, 30, 30, 30)

        # ------ Header --------
        self.header = QLabel(self.tr("Equity"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-left:25")
        font = QFont()
        font.setFamily("Roboto")
        font.setWeight(QFont.Bold)
        font.setPointSize(20)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.layout.addWidget(self.header)

        # ------ Chart
        self.chart = TotalEquityChartView()
        data = dbhandler.get_wealth_by_day()
        self.chart.setupChartWithData(data)

        self.layout.addWidget(self.chart)

        self.setLayout(self.layout)


class DistributionWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("distribution")

        # Background image
        style = """#distribution {
        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #65B585, stop:1 #273B4F);
        border-radius: 15px}"""
        self.setStyleSheet(style)

        #  Size
        self.setMaximumSize(645, 665)

        # ------------ Content ------------
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(45, 45, 45, 45)
        self.layout.setSpacing(30)

        # ------ Header --------
        self.header = QLabel(self.tr("Distribution"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0);")
        font = QFont()
        font.setFamily("Roboto")
        font.setWeight(QFont.Bold)
        font.setPointSize(20)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.layout.addWidget(self.header)

        # ------ Buttons --------
        self.buttons_layout = QHBoxLayout()
        self.accs = DistributionButton(self.tr("Accounts"), color=1)
        self.cryptoaccs = DistributionButton(self.tr("Crypto"), color=1)
        self.strategies = DistributionButton(self.tr("Currency"), color=1)

        self.bttns = (self.accs,
                      self.cryptoaccs, self.strategies)

        # Connect button checks to handle them
        self.accs.clicked.connect(
            lambda checked: self.handleCheck(self.accs, checked))
        self.cryptoaccs.clicked.connect(
            lambda checked: self.handleCheck(self.cryptoaccs, checked))
        self.strategies.clicked.connect(
            lambda checked: self.handleCheck(self.strategies, checked))

        for bttn in self.bttns:
            self.buttons_layout.addWidget(bttn)
        self.layout.addLayout(self.buttons_layout)

        # ------ Chart --------
        self.chart = DistributionPieChart()

        self.layout.addWidget(self.chart)

        self.setLayout(self.layout)

    def handleCheck(self, button, checked):
        """
        Only one button can be selected at a time
        """
        for bttn in self.bttns:
            if bttn != button:
                # Uncheck previously checked button
                bttn.setChecked(False)

        # Change chart according to new mode
        if not checked:
            # No button checked, show total distribution
            self.chart.setupSeries(mode="all")
        elif button == self.accs:
            # Show distribution between portfolio accs
            self.chart.setupSeries(mode="accounts")
        elif button == self.cryptoaccs:
            # Show distribution between crypto accs
            self.chart.setupSeries(mode="crypto")
        elif button == self.strategies:
            # Show distribution between strategies
            self.chart.setupSeries(mode="currency")


class DistributionButton(QPushButton):
    def __init__(self, *args, color=1, **kwargs):
        super().__init__(*args, **kwargs)

        # Color selection
        colors = {1: "#325059", 2: "#3C6361", 3: "#65B585"}
        color = colors[color]

        # UI
        self.setStyleSheet("QPushButton"
                           "{"
                           f"background-color: {color} ; border-width: 2px; border-radius: 15px;"
                           f"border-color: {color}; padding-top:8px; padding-bottom:8px"
                           "}"
                           "QPushButton::hover"
                           "{"
                           f"background-color: {color}; border-width: 1px; border-radius: 15px;"
                           "border-color: white; border-style: solid; padding-top:8px; padding-bottom:8px"
                           "}"
                           "QPushButton::checked"
                           "{"
                           f"background-color: white; border-width: 2px; border-radius: 15px;"
                           f"border-color: {color} ; border-style: solid; padding-top:8px; padding-bottom:8px;"
                           f"color: {color}"
                           "}"
                           )
        font = QFont()
        font.setFamily('Roboto')
        font.setPointSize(15)
        font.setBold(True)
        self.setFont(font)

        # Functionality
        self.setCheckable(True)
