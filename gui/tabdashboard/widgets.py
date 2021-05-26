#!/usr/bin/python3

import os
from datetime import datetime
import calendar

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QBoxLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QScrollArea, QDateEdit
from PyQt5.QtGui import QFont, QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import Qt, QDateTime, QEvent, QPropertyAnimation, QObject
from PyQt5.QtCore import QEasingCurve, QPoint, QSize, pyqtProperty, pyqtSignal, QDate


from gui.dbhandler import balances, historicalbalances, strategies, results
from gui.cdbhandler import cbalances, chistoricalbalances
from gui.prices import prices
from gui import confighandler, utils
from gui.tabdashboard.charts import TotalWealthHistoryChartView, LastMonthsHistogram, TotalEquityChartView
from gui.tabdashboard.charts import DistributionPieChart

RESOURCES_PATH = confighandler.getUserDataPath()


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
        data = utils.get_totalWealthByDay()
        self.chart.setupChartWithData(data)

        # - Percentage -
        # The percentage is the difference between the first balance history and the las one
        first_balance = utils.get_firstBalance()
        last_balance = utils.get_lastBalance()

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
        first_total_wealth_current_month = utils.get_first_total_wealth_current_month()
        change_last_month = utils.get_change_last_month()
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

        # UI
        self.setSpacing(0)

        # ---------- Filter Accounts ----------
        # Fiat accounts
        self.fiataccount_buttons_scrollarea = QScrollArea()
        self.fiataccount_buttons_scrollarea.setFixedHeight(80)
        self.fiataccount_buttons_scrollarea.horizontalScrollBar(
        ).setStyleSheet("QScrollBar:horizontal {height: 10px;}")

        self.fiataccount_buttons_lyt = QHBoxLayout()
        self.fiataccount_buttons_lyt.setContentsMargins(0, 0, 0, 0)

        self.fiataccount_buttons = []  # To manipulate them later
        # Add "all" button
        self.all_bttn = FilterAccountOrStrategyButton(
            'allaccounts', "All")
        self.all_bttn.toggled.connect(
            lambda checked: self.handleCheck(self.all_bttn, checked))
        self.fiataccount_buttons_lyt.addWidget(self.all_bttn)

        for acc in balances.getAllAccountNames():
            bttn = FilterAccountOrStrategyButton('fiat', acc)
            bttn.clicked.connect(self.sendQuery)
            self.fiataccount_buttons_lyt.addWidget(bttn)
            self.fiataccount_buttons.append(bttn)

        self.fiataccount_buttons_wrapper = QWidget()
        self.fiataccount_buttons_wrapper.setLayout(
            self.fiataccount_buttons_lyt)
        self.fiataccount_buttons_scrollarea.setWidget(
            self.fiataccount_buttons_wrapper)
        self.addWidget(self.fiataccount_buttons_scrollarea)

        # Add crypto accounts
        self.cryptoaccount_buttons_scrollarea = QScrollArea()
        self.cryptoaccount_buttons_scrollarea.setFixedHeight(80)
        self.cryptoaccount_buttons_scrollarea.horizontalScrollBar(
        ).setStyleSheet("QScrollBar:horizontal {height: 10px;}")

        self.cryptoaccount_buttons_lyt = QHBoxLayout()
        self.cryptoaccount_buttons_lyt.setContentsMargins(0, 0, 0, 0)

        self.cryptoaccount_buttons = []
        # Add "all" button
        self.all_cbttn = FilterAccountOrStrategyButton('allaccounts', "All")
        self.all_cbttn.toggled.connect(
            lambda checked: self.handleCheck(self.all_cbttn, checked))
        self.cryptoaccount_buttons_lyt.addWidget(self.all_cbttn)

        for cacc in cbalances.getAllAccounts():
            bttn = FilterAccountOrStrategyButton('crypto', cacc)
            bttn.clicked.connect(self.sendQuery)
            self.cryptoaccount_buttons_lyt.addWidget(bttn)
            self.cryptoaccount_buttons.append(bttn)

        self.cryptoaccount_buttons_wrapper = QWidget()
        self.cryptoaccount_buttons_wrapper.setLayout(
            self.cryptoaccount_buttons_lyt)
        self.cryptoaccount_buttons_scrollarea.setWidget(
            self.cryptoaccount_buttons_wrapper)
        self.addWidget(self.cryptoaccount_buttons_scrollarea)

        # ---------- Filter Period ----------
        self.filter_period_wrapper = QWidget()
        self.filter_period_wrapper.setMaximumHeight(150)
        self.filter_period_layout = QVBoxLayout()
        self.filter_period_layout.setSpacing(0)

        # Labels
        self.filter_period_labels_layout = QHBoxLayout()
        labelfont = QFont()
        labelfont.setBold(True)
        labelfont.setPointSize(15)
        self.start_date_label = QLabel(self.tr("Start Date"))
        self.start_date_label.setFont(labelfont)
        self.start_date_label.setFixedHeight(30)
        self.end_date_label = QLabel(self.tr("End Date"))
        self.end_date_label.setFont(labelfont)
        self.end_date_label.setFixedHeight(30)
        self.end_date_label.setStyleSheet(
            "margin-left:5px;")  # For alignment purposes
        self.filter_period_labels_layout.addWidget(self.start_date_label)
        self.filter_period_labels_layout.addWidget(self.end_date_label)
        self.filter_period_layout.addLayout(self.filter_period_labels_layout)

        # Date selection
        self.filter_period_dates_layout = QHBoxLayout()
        self.filter_period_start_date = DateEdit()
        self.filter_period_end_date = DateEdit()
        self.filter_period_dates_layout.addWidget(
            self.filter_period_start_date)
        self.filter_period_dates_layout.addWidget(self.filter_period_end_date)
        self.filter_period_layout.addLayout(self.filter_period_dates_layout)

        self.filter_period_start_date.dateChanged.connect(self.sendQuery)
        self.filter_period_end_date.dateChanged.connect(self.sendQuery)

        # Button shortcuts
        self.bttn_shortcuts_lyt = QHBoxLayout()
        self.bttn_shortcuts_lyt.setSpacing(5)
        self.mtd = QPushButton(self.tr("MTD"))
        self.mtd.setStyleSheet("margin-left:5px; border-radius:10px")
        self.mtd.clicked.connect(self.set_mtd)
        self.ytd = QPushButton(self.tr("YTD"))
        self.ytd.setStyleSheet("margin-left:5px; border-radius:10px")
        self.ytd.clicked.connect(self.set_ytd)
        self.bttn_shortcuts_lyt.addWidget(self.mtd)
        self.bttn_shortcuts_lyt.addWidget(self.ytd)
        self.filter_period_layout.addLayout(self.bttn_shortcuts_lyt)

        self.filter_period_wrapper.setLayout(self.filter_period_layout)
        self.addWidget(self.filter_period_wrapper)

        # Query data structure, to parse all info better and make database queries
        self.query_data = {}
        self.query_data['fiataccs'] = [bttn.text()
                                       for bttn in self.fiataccount_buttons]
        self.query_data['cryptoaccs'] = [bttn.text()
                                         for bttn in self.cryptoaccount_buttons]
        self.query_data['startdate'] = self.filter_period_start_date.date()
        self.query_data['enddate'] = self.filter_period_end_date.date()
        # Signal to emit when a new query should be made
        self.querysignal = QuerySignal()

        # Initialization
        self.set_mtd()

    def handleCheck(self, button, checked):
        """
        Checks buttons appropiately
        """
        # Select all fiat accounts
        if button == self.all_bttn:
            if checked:
                for bttn in self.fiataccount_buttons:
                    bttn.setChecked(True)
            else:
                for bttn in self.fiataccount_buttons:
                    bttn.setChecked(False)

        # Select all crypto accounts
        elif button == self.all_cbttn:
            if checked:
                for bttn in self.cryptoaccount_buttons:
                    bttn.setChecked(True)
            else:
                for bttn in self.cryptoaccount_buttons:
                    bttn.setChecked(False)

        self.sendQuery()

    def sendQuery(self):
        """ 
        Parses all filters, and structures a query dictionary,
        then returns it
        """
        self.query_data['fiataccs'] = [bttn.text()
                                       for bttn in self.fiataccount_buttons if bttn.isChecked() is True]
        self.query_data['cryptoaccs'] = [bttn.text()
                                         for bttn in self.cryptoaccount_buttons if bttn.isChecked() is True]

        startdate = self.filter_period_start_date.date()
        self.query_data['startdate'] = datetime(
            startdate.year(), startdate.month(), startdate.day()).timestamp()
        enddate = self.filter_period_end_date.date()
        self.query_data['enddate'] = datetime(
            enddate.year(), enddate.month(), enddate.day()).timestamp()

        self.querysignal.newquery.emit(self.query_data)

    def set_ytd(self):
        today = datetime.today()
        self.filter_period_start_date.setDate(QDate(today.year, 1, 1))
        self.filter_period_end_date.setDate(QDate.currentDate())

    def set_mtd(self):
        today = datetime.today()
        self.filter_period_start_date.setDate(
            QDate(today.year, today.month, 1))
        self.filter_period_end_date.setDate(QDate.currentDate())


class FilterModeButton(QPushButton):
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


class FilterAccountOrStrategyButton(QPushButton):
    """
    buttontype in ('fiat','crypto','all')
    """

    def __init__(self, buttontype, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Color selection
        self.setColors()
        color = self.colors[buttontype]

        self.checkButtonType(buttontype)

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

        if self.text() == "All":
            font = QFont()
            font.setPointSize(15)
            font.setBold(True)
            self.setFont(font)
            self.setFixedWidth(20)

            # Functionality
        self.setCheckable(True)

    def setColors(self):
        self.colors = {'fiat': "#E43E53", 'crypto': "#3A634A",
                       'strategy': '#273B4F', 'allaccounts': '#3C556E', 'allstrategies': '#3C556E'}

    def checkButtonType(self, buttontype):
        assert(buttontype in ('fiat', 'crypto',
                              'strategy', 'allaccounts', 'allstrategies'))
        self.type = buttontype


class DateEdit(QDateEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setCalendarPopup(True)
        self.setAlignment(Qt.AlignCenter)
        self.setDisplayFormat("d MMM yyyy")
        self.setDate(QDate().currentDate())
        self.setStyleSheet(
            "QDateEdit"
            "{"
            "background-color: #C7CFD8;margin-left:7px; font-size:15px;"
            "border: 0px;"
            "color: #19232D;"
            "}"
            "QDateEdit::drop-down"
            "{"
            "border: 0.5px #C7CFD8;"
            "color: #8398AD"
            "}")


class QueryResultsWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("queryresultswidget")

        # Background image
        style = """#queryresultswidget {
        background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 #65B585, stop:1 #325440);
        border-radius: 15px}"""
        self.setStyleSheet(style)

        # ---------------------------------
        # ------------ Content ------------
        # ---------------------------------
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)

        # ------ Header --------
        self.header_lyt_wrapper = QWidget()
        self.header_lyt_wrapper.setStyleSheet(
            "background-color: rgba(0,0,0,0)")
        self.header_lyt = QHBoxLayout()
        self.header_lyt.setSpacing(40)
        self.header = QLabel(self.tr("Total Result"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-top: 15;")
        self.header.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setFamily("Roboto")
        font.setWeight(QFont.Bold)
        font.setPointSize(35)
        font.setBold(True)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.header_totalresult = QLabel()
        self.header_totalresult.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-top: 15;")
        font.setPointSize(50)
        font.setBold(False)
        self.header_totalresult.setFont(font)
        self.header_totalresult.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.header_lyt.addWidget(self.header)
        self.header_lyt.addWidget(self.header_totalresult)
        self.header_lyt_wrapper.setLayout(self.header_lyt)

        self.layout.addWidget(self.header_lyt_wrapper, Qt.AlignHCenter)

        # ----------------- Low layout ----------
        self.low_lyt_wrapper = QWidget()
        self.low_lyt_wrapper.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-bottom: 40px; ")
        self.low_lyt = QHBoxLayout()
        # ------ Left part --------
        self.left_lyt = QHBoxLayout()
        self.left_lyt.setAlignment(Qt.AlignCenter)

        # Labels
        labelfont = QFont()
        labelfont.setPointSize(20)
        labelfont.setBold(True)
        self.left_lyt_labels = QVBoxLayout()
        self.startbalance_lbl = QLabel(self.tr("Start Balance"))
        self.startbalance_lbl.setFont(labelfont)
        self.startbalance_lbl.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.startbalance_lbl.setAlignment(Qt.AlignCenter)
        self.endbalance_lbl = QLabel(self.tr("End Balance"))
        self.endbalance_lbl.setFont(labelfont)
        self.endbalance_lbl.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.endbalance_lbl.setAlignment(Qt.AlignCenter)
        self.drawdown_lbl = QLabel(self.tr("Max Drawdown"))
        self.drawdown_lbl.setFont(labelfont)
        self.drawdown_lbl.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.drawdown_lbl.setAlignment(Qt.AlignCenter)
        self.left_lyt_labels.addWidget(self.startbalance_lbl)
        self.left_lyt_labels.addWidget(self.endbalance_lbl)
        self.left_lyt_labels.addWidget(self.drawdown_lbl)

        self.left_lyt.addLayout(self.left_lyt_labels)

        # Content
        contentfont = QFont()
        contentfont.setPointSize(20)
        contentfont.setWeight(QFont.Light)
        self.left_lyt_content = QVBoxLayout()
        self.startbalance = QLabel()
        self.startbalance.setAlignment(Qt.AlignCenter)
        self.startbalance.setFont(contentfont)
        self.endbalance = QLabel()
        self.endbalance.setAlignment(Qt.AlignCenter)
        self.endbalance.setFont(contentfont)
        self.drawdown_lyt = QHBoxLayout()
        self.drawdown_lyt.setSpacing(0)
        self.drawdown = QLabel()
        self.drawdown.setAlignment(Qt.AlignCenter)
        self.drawdown.setFont(contentfont)
        self.drawdown_fiat = QLabel()
        #self.drawdown_fiat.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        contentfont.setPointSize(10)
        self.drawdown_fiat.setFont(contentfont)
        self.drawdown_lyt.addWidget(self.drawdown)
        self.drawdown_lyt.addWidget(self.drawdown_fiat)

        self.left_lyt_content.addWidget(self.startbalance)
        self.left_lyt_content.addWidget(self.endbalance)
        self.left_lyt_content.addLayout(self.drawdown_lyt)

        self.left_lyt.addLayout(self.left_lyt_content)

        self.low_lyt.addLayout(self.left_lyt)

#        # ------ Right part --------
#        self.right_lyt_wrapper = QWidget()
#        self.right_lyt_wrapper.setMinimumWidth(400)
#        self.right_lyt_wrapper_lyt = QVBoxLayout()
        self.chart = TotalEquityChartView()
        self.chart.setupChartWithData(
            utils.getWealthByDay(), linecolor='white')
        # self.right_lyt_wrapper_lyt.addWidget(self.chart)
        # self.right_lyt_wrapper.setLayout(self.right_lyt_wrapper_lyt)

        self.low_lyt.addWidget(self.chart)
        # self.low_lyt.addLayout(self.right_lyt)

        self.low_lyt_wrapper.setLayout(self.low_lyt)
        self.layout.addWidget(self.low_lyt_wrapper, Qt.AlignRight)

        self.setLayout(self.layout)

    def updateData(self, query):
        """
        Sets all the data according to the new query parameters

        Parameters:
         - query: dict
            structure -> ["fiataccs"] = list of selected fiat accounts
                         ["cryptoaccs"] = list of selected crypto accounts
                         ["startdate"]  = start date in timestamp
                         ["enddate"]    = end date in timestamp
        """
        FIAT_CURRENCY = confighandler.get_fiat_currency()
        wealthbyday = utils.getWealthByDay(
            query['fiataccs'], query['cryptoaccs'], query['startdate'], query['enddate'])

        if len(wealthbyday) == 0:
            self.header_totalresult.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.startbalance.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.endbalance.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.drawdown.setText(f"0 %")
            self.drawdown_fiat.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.chart.setupChartWithData(
                utils.getWealthByDay(), linecolor='white')
            return

        startbalance = int(wealthbyday[min(wealthbyday.keys())])
        endbalance = int(wealthbyday[max(wealthbyday.keys())])

        self.header_totalresult.setText(
            f"{endbalance-startbalance} {FIAT_CURRENCY.upper()}")

        self.startbalance.setText(f"{startbalance} {FIAT_CURRENCY.upper()}")
        self.endbalance.setText(f"{endbalance} {FIAT_CURRENCY.upper()}")

        # Drawdown
        wealthbyday_list = list(wealthbyday.values())
        import pandas as pd
        wbd = pd.Series(wealthbyday_list)
        drawdown = (100*(- max(1-(wbd/wbd.cummax()))))
        import math
        if math.isnan(drawdown) is False:
            drawdown = int(drawdown)

        drawdown_fiat = int(min(wbd-wbd.cummax()))
        self.drawdown.setText(f"{drawdown} %")
        self.drawdown_fiat.setText(f"{drawdown_fiat} {FIAT_CURRENCY.upper()}")

        # Chart
        self.chart.setupChartWithData(wealthbyday, linecolor='white')


# -------------- Signals --------------
class QuerySignal(QObject):
    newquery = pyqtSignal(dict)
