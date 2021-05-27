#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QScrollArea, QPushButton, QLabel, QFrame, QDateEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate, QObject, pyqtSignal

from portfolio.utils import confighandler
from portfolio.db import dbhandler
from portfolio.db.dbhandler import balances
from portfolio.db.cdbhandler import cbalances
from portfolio.gui.tabdashboard.charts import TotalEquityChartView


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
            dbhandler.getWealthByDay(), linecolor='white')
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
        wealthbyday = dbhandler.getWealthByDay(
            query['fiataccs'], query['cryptoaccs'], query['startdate'], query['enddate'])

        if len(wealthbyday) == 0:
            self.header_totalresult.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.startbalance.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.endbalance.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.drawdown.setText(f"0 %")
            self.drawdown_fiat.setText(f"0 {FIAT_CURRENCY.upper()}")
            self.chart.setupChartWithData(
                dbhandler.getWealthByDay(), linecolor='white')
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
