#!/usr/bin/python3

import os
from datetime import datetime
import calendar

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QPushButton, QScrollArea
from PyQt5.QtGui import QFont, QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import Qt, QDateTime, QEvent, QPropertyAnimation, QObject
from PyQt5.QtCore import QEasingCurve, QPoint, QSize, pyqtProperty, pyqtSignal


from gui.dbhandler import balances, historicalbalances
from gui.cdbhandler import cbalances, chistoricalbalances
from gui.prices import prices
from gui import confighandler, utils
from gui.tabdashboard.charts import TotalWealthHistoryChartView, LastMonthsHistogram, TotalEquityChartView
from gui.tabdashboard.charts import DistributionPieChart

RESOURCES_PATH = confighandler.getUserDataPath()
FIAT_CURRENCY = confighandler.get_fiat_currency()


class TotalWealthWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("totalwealthwidget")
        # Background image
        style = "#totalwealthwidget {background-image: url(" + os.path.join(
            RESOURCES_PATH, "red_gradient_background.png") + ")}"
        self.setStyleSheet(style)

        # Size
        self.setFixedSize(645, 213)

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
        totalwealth_portfolio = balances.getTotalBalanceAllAccounts()
        totalwealth_cportfolio = prices.btcToFiat(
            cbalances.getTotalBalanceAllAccounts())
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
        self.fiat_label = QLabel(FIAT_CURRENCY.upper())
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
        data = utils.get_totalWealthByDay()
        self.chart.setupChartWithData(data)

        # - Percentage -
        # The percentage is the difference between the first balance history and the las one
        first_balance = utils.get_firstBalance()
        last_balance = utils.get_lastBalance()
        percentage = ((last_balance/first_balance)-1)*100
        if percentage > 0:
            percentage_str = "+{}%".format(round(percentage, 1))
        else:
            percentage_str = "{}%".format(round(percentage, 1))

        self.percentage_label = QLabel(percentage_str)
        self.percentage_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-right:60")
        font = QFont()
        font.setFamily("Inter")
        font.setPointSize(24)
        self.percentage_label.setFont(font)
        self.percentage_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # - Arrow -
        self.arrow = QLabel()
        # pixmap =

        self.amountlyt.addWidget(self.amount_label)
        self.amountlyt.addWidget(self.fiat_label)
        self.amountlyt.addWidget(self.chart)
        self.amountlyt.addWidget(self.percentage_label)

        self.layout.addLayout(self.amountlyt)

        self.setLayout(self.layout)

    def enterEvent(self, event):
        pass

    def leaveEvent(self, event):
        pass


class LastMonthWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("lastmonthwidget")

        # Background image
        style = "#lastmonthwidget {background-image: url(" + os.path.join(
            RESOURCES_PATH, "lastmonthwidget_background.png") + ")}"
        self.setStyleSheet(style)

        # Size
        self.setFixedSize(240, 235)

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
        change_fiat_value = utils.get_change_last_month()
        change_fiat_value_str = "+" + \
            str(change_fiat_value) if change_fiat_value >= 0 else str(
                change_fiat_value)

        self.change_fiat = QLabel(change_fiat_value_str)
        self.change_fiat.setStyleSheet(
            "background-color: rgba(0,0,0,0); color:#D3EABD; margin-left: 8")
        font = QFont()
        font.setFamily("Roboto")
        # font.setWeight(QFont.Bold)
        font.setPointSize(15)
        self.change_fiat.setFont(font)
        self.change_fiat.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.second_row.addWidget(self.change_fiat)

        # -- Fiat label --
        self.fiat_label = QLabel(FIAT_CURRENCY.upper())
        self.fiat_label.setStyleSheet(
            "background-color: rgba(0,0,0,0);color:#D3EABD; margin-top:10px")
        font = QFont()
        font.setFamily("Roboto")
        font.setPointSize(7)
        self.fiat_label.setFont(font)
        self.fiat_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.second_row.addWidget(self.fiat_label)

        # -- Change (%) --
        change_percentage = 100 * \
            (utils.get_change_last_month() /
             utils.get_first_total_wealth_current_month())
        change_percentage = round(change_percentage, 1)

        change_percentage_str = "+{}%".format(str(
            change_percentage)) if change_percentage >= 0 else "{}%".format(str(change_percentage))

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
        data = utils.get_totalWealthByDay_LastMonth()
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
        style = "#lastmonthshistogram {background-image: url(" + os.path.join(
            RESOURCES_PATH, "lastmonthshistogram_background.png") + ")}"
        self.setStyleSheet(style)

        # Size
        self.setFixedSize(375, 235)

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
        self.histogram.setupChartWithData({"si": 1})

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.histogram)

        self.setLayout(self.layout)


class TotalEquityWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("totalequity")

        # Background image
        style = "#totalequity {background-image: url(" + os.path.join(
            RESOURCES_PATH, "totalequity_background.png") + ")}"
        self.setStyleSheet(style)

        #  Size
        self.setFixedSize(645, 396)

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
        data = utils.get_totalWealthByDay()
        self.chart.setupChartWithData(data)

        self.layout.addWidget(self.chart)

        self.setLayout(self.layout)


class DistributionWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("distribution")

        # Background image
        style = "#distribution {background-image: url(" + os.path.join(
            RESOURCES_PATH, "distributionwidget_background.png") + ")}"
        self.setStyleSheet(style)

        #  Size
        self.setFixedSize(645, 665)

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
        self.cryptoaccs = DistributionButton(self.tr("Crypto"), color=2)
        self.strategies = DistributionButton(self.tr("Currency"), color=3)

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

        self.setFixedSize(165, 38)
        font = QFont()
        font.setFamily('Roboto')
        font.setPointSize(15)
        font.setBold(True)
        self.setFont(font)

        # Functionality
        self.setCheckable(True)


class FilterLayout(QVBoxLayout):
    """
    Layout with all the filters that the user will select in order
    to create a query to show data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---------- Filter Buttons ----------
        self.filterbuttons = QHBoxLayout()

        self.acc = FilterButton(self.tr("Account"), color=1)
        self.stra = FilterButton(self.tr("Strategy"), color=2)
        self.period = FilterButton(self.tr("Period"), color=3)

        self.bttns = (self.acc,
                      self.stra, self.period)

        # Connect button checks to handle them
        self.acc.clicked.connect(
            lambda checked: self.handleCheck(self.acc, checked))
        self.stra.clicked.connect(
            lambda checked: self.handleCheck(self.stra, checked))
        self.period.clicked.connect(
            lambda checked: self.handleCheck(self.period, checked))

        for bttn in self.bttns:
            self.filterbuttons.addWidget(bttn)

        self.addLayout(self.filterbuttons)

        # ---------- Filter Accounts ----------
        self.filter_accounts_scrollarea = QScrollArea()
        self.filter_accounts_scrollarea.setFixedHeight(80)
        self.filter_accounts_scrollarea.horizontalScrollBar(
        ).setStyleSheet("QScrollBar:horizontal {height: 15px;}")
        self.filter_accounts = QHBoxLayout()

        ccolor = "#E43E53"
        color = "#3A634A"

        # Add crypto accounts
        for cacc in cbalances.getAllAccounts():
            bttn = FilterAccountButton(cacc, color=1)
            self.filter_accounts.addWidget(bttn)
        # Add fiat accounts
        for acc in balances.getAllAccountNames():
            bttn = FilterAccountButton(acc, color=2)
            self.filter_accounts.addWidget(bttn)

        self.filter_accounts_wrapper = QWidget()
        self.filter_accounts_wrapper.setLayout(self.filter_accounts)
        self.filter_accounts_scrollarea.setWidget(self.filter_accounts_wrapper)
        self.addWidget(self.filter_accounts_scrollarea)

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
            pass
        elif button == self.acc:
            pass
        elif button == self.stra:
            pass
        elif button == self.period:
            pass


class FilterButton(QPushButton):
    def __init__(self, *args, color=1, **kwargs):
        super().__init__(*args, **kwargs)

        # Color selection
        colors = {1: "#36526E", 2: "#58626C", 3: "#273B4F"}
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

        self.setFixedSize(200, 40)
        font = QFont()
        font.setFamily('Roboto')
        font.setPointSize(15)
        font.setBold(True)
        self.setFont(font)

        # Functionality
        self.setCheckable(True)


class FilterAccountButton(QPushButton):
    def __init__(self, *args, color=1, **kwargs):
        super().__init__(*args, **kwargs)

        # Color selection
        colors = {1: "#E43E53", 2: "#3A634A"}
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

        # Functionality
        self.setCheckable(True)
