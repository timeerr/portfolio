#!/usr/bin/python3

import os
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QScrollArea, QLabel, QFrame
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont, QPalette, QPainter, QBrush, QColor, QRgba64, QPen
from PyQt5.QtCore import Qt, QDateTime

from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QLineSeries, QDateTimeAxis, QValueAxis, QSplineSeries

from gui.cdbhandler import cbalances, chistoricalbalances
from gui.dbhandler import balances, historicalbalances
from gui.tabdashboard.widgets import TotalWealthWidget, LastMonthWidget, LastMonthsHistogramWidget
from gui.tabdashboard.widgets import TotalEquityWidget, DistributionWidget, FilterLayout

from gui.prices import prices

from gui import confighandler


RESOURCES_PATH = confighandler.getUserDataPath()


class TabDashboard(QWidget):
    """
    Displays all the main information about the portfolio
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # UI
        self.setWindowTitle(self.tr("Dashboard"))
        self.setStyleSheet("border: 0px")

        # Layout
        self.mainlayout = QHBoxLayout()

        # ------------  Left layout: General portfolio data ---------------
        self.leftlayout = QVBoxLayout()
        self.leftlayout.setSpacing(30)

        # -- First Widget: Total wealth --
        self.totalwealth = TotalWealthWidget(self)

        # -- Second & Third Widgets: Last Month and Histogram --
        self.secondrow_lyt = QHBoxLayout()
        self.secondrow_lyt.setSpacing(30)

        self.lastmonth = LastMonthWidget(self)
        self.secondrow_lyt.addWidget(self.lastmonth)

        self.histogram = LastMonthsHistogramWidget(self)
        self.secondrow_lyt.addWidget(self.histogram)

        # -- Fourth Widget: Total Equity Chart --
        self.totalequity = TotalEquityWidget(self)

        # -- Fourth Widget: Distribution Chart --
        self.distribution = DistributionWidget(self)

        self.leftlayout.addWidget(self.totalwealth)
        self.leftlayout.addLayout(self.secondrow_lyt)
        self.leftlayout.addWidget(self.totalequity)
        self.leftlayout.addWidget(self.distribution)

        # Make Left Layout Scroll Area
        self.leftlayout_scrollarea = QScrollArea(self)
        self.leftlayout_scrollarea.setStyleSheet(
            "border:0;margin:0 0 0 0; padding: 0 0 0 0")
        self.leftlayout_scrollarea.setFixedWidth(680)
        self.leftlayout_scrollarea.horizontalScrollBar().hide()  # Hide horizontalScrollBar
        self.leftlayout_scrollarea.verticalScrollBar().setStyleSheet(
            "QScrollBar:vertical {width: 3px;}")  # Customize verticalScrollBar
        self.leftlayout_scrollarea.verticalScrollBar().setSingleStep(10)

        self.leftlayout_scrollarea_wrapper = QWidget()  # Wrap leftlayout inside QWidget
        self.leftlayout_scrollarea_wrapper.setStyleSheet(
            "border:0;margin:0 0 0 0; padding: 0 0 0 0")
        self.leftlayout_scrollarea_wrapper.setLayout(self.leftlayout)
        self.leftlayout_scrollarea.setWidget(
            self.leftlayout_scrollarea_wrapper)  # Set wrapper widget as QScrollArea's Widget

        # ------------  Right layout: General portfolio data ---------------
        self.rightlayout = QVBoxLayout()
        self.rightlayout.setContentsMargins(10, 0, 0, 0)

        # -- First Widget: Filter buttons --
        self.filterbuttons = FilterLayout()

        self.rightlayout.addLayout(self.filterbuttons)
        self.rightlayout.addWidget(QLabel("Test"))
        self.rightlayout.addWidget(QLabel("Test"))
        self.rightlayout.addWidget(QLabel("Test"))
        self.rightlayout.addWidget(QLabel("Test"))

        self.mainlayout.addWidget(self.leftlayout_scrollarea)
        self.mainlayout.addLayout(self.rightlayout)

        self.setLayout(self.mainlayout)
