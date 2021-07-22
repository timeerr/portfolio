#!/usr/bin/python3

from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from portfolio.gui.ui_components.styles import GradientStyle
from portfolio.gui.ui_components.charts.last_months_balance_histogram import LastMonthsHistogram


class LastMonthsHistogramWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("lastmonthshistogram")

        # ---- UI ----
        # Background image
        self.setStyleSheet(GradientStyle.get(
            self.objectName(), '#36526E', '#57616B'))
        # Size
        self.setMaximumSize(375, 235)

        # ---- Content ----
        self.layout = QVBoxLayout()
        # -- Header --
        self.header = QLabel(self.tr("Last Months"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0); margin-top: 15; margin-left: 8 ")
        self.header.setFont(QFont('Roboto', pointSize=20, weight=QFont.Bold))
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.header)
        # -- Histogram --
        self.histogram = LastMonthsHistogram()
        self.histogram.setupChartWithData()
        self.layout.addWidget(self.histogram)

        self.setLayout(self.layout)
