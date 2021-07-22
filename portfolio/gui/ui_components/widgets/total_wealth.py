#!/usr/bin/python3

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from portfolio.utils import confighandler
from portfolio.utils.prices import prices
from portfolio.db import dbhandler
from portfolio.db.fdbhandler import balances
from portfolio.db.cdbhandler import cbalances
from portfolio.gui.ui_components.styles import GradientStyle
from portfolio.gui.ui_components.charts.total_wealth_history import TotalWealthHistoryChartView


class TotalWealthWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("totalwealthwidget")
        # Background image
        self.setStyleSheet(GradientStyle.get(
            self.objectName(), "#F06814", "#E43E53"))

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
        self.header.setFont(QFont('Roboto', pointSize=40, weight=QFont.Bold))
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
