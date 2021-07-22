#!/usr/bin/python3

import os
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QScrollArea, QLabel, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont, QPalette, QPainter, QBrush, QColor, QRgba64, QPen
from PyQt5.QtCore import Qt, QDateTime

from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QLineSeries, QDateTimeAxis, QValueAxis, QSplineSeries

from portfolio.utils import confighandler
from portfolio.gui.ui_components.widgets.total_wealth import TotalWealthWidget
from portfolio.gui.ui_components.widgets.current_month_results import CurrentMonthResultsWidget
from portfolio.gui.ui_components.widgets.last_months_balance import LastMonthsHistogramWidget
from portfolio.gui.ui_components.widgets.total_equity import TotalEquityWidget
from portfolio.gui.ui_components.widgets.balances_distribution import DistributionWidget


class TabDashboard(QWidget):
    """ Displays all the main information about the portfolio """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- UI ----
        self.setWindowTitle(self.tr("Dashboard"))
        self.setStyleSheet("border: 0px")

        # ---- Content ----
        self.mainlayout = QHBoxLayout()

        # ---  Left layout ---
        self.leftlayout = QVBoxLayout()
        self.leftlayout.setSpacing(30)

        # Total wealth
        self.totalwealth = TotalWealthWidget(self)
        self.leftlayout.addWidget(self.totalwealth)

        # Last Month and Histogram
        self.secondrow_lyt = QHBoxLayout()
        self.secondrow_lyt.setSpacing(30)
        self.lastmonth = CurrentMonthResultsWidget(self)
        self.secondrow_lyt.addWidget(self.lastmonth)
        self.histogram = LastMonthsHistogramWidget(self)
        self.secondrow_lyt.addWidget(self.histogram)
        self.leftlayout.addLayout(self.secondrow_lyt)

        #  Total Equity Chart
        self.totalequity = TotalEquityWidget(self)
        self.leftlayout.addWidget(self.totalequity)

        # Wrap Left Layout inside QWidget
        self.wrapper = QWidget()
        self.wrapper.setStyleSheet(
            "border:0;margin:0 0 0 0; padding: 0 0 0 0")
        self.wrapper.setLayout(self.leftlayout)

        # Wrap wrapper inside Scroll Area
        self.leftlayout_scrollarea = QScrollArea(self)
        self.leftlayout_scrollarea.setStyleSheet(
            "border:0;margin:0 0 0 0; padding: 0 0 0 0")
        self.leftlayout_scrollarea.setFixedWidth(680)
        self.leftlayout_scrollarea.horizontalScrollBar().hide()  # Hide horizontalScrollBar
        self.leftlayout_scrollarea.verticalScrollBar().setStyleSheet(
            "QScrollBar:vertical {width: 3px;}")  # Customize verticalScrollBar
        self.leftlayout_scrollarea.verticalScrollBar().setSingleStep(10)
        self.leftlayout_scrollarea.setWidget(
            self.wrapper)

        self.mainlayout.addWidget(self.leftlayout_scrollarea)

        # ---  Right layout ---
        self.rightlayout = QVBoxLayout()
        self.rightlayout.setContentsMargins(10, 0, 0, 0)
        self.rightlayout.setSpacing(30)

        # Distribution Chart
        self.distribution = DistributionWidget(self)
        self.rightlayout.addWidget(self.distribution)

        self.mainlayout.addLayout(self.rightlayout)

        self.setLayout(self.mainlayout)

        # ---- Functionality ----
        # TODO
