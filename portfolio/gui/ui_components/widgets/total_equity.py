#!/usr/bin/python3

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


from portfolio.db import dbhandler
from portfolio.gui.ui_components.charts.total_equity import TotalEquityChartView
from portfolio.gui.ui_components.styles import GradientStyle


class TotalEquityWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("totalequity")

        # ---- UI ----
        # Background image
        self.setStyleSheet(GradientStyle.get(
            self.objectName(), '#506273', '#506273'))
        #  Size
        #self.setMaximumSize(645, 396)
        self.setMaximumWidth(645)

        # ---- Content ----
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(20, 30, 30, 30)
        # -- Header --
        self.header = QLabel(self.tr("Equity"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0);margin-left:25")
        self.header.setFont(QFont('Roboto', pointSize=20, weight=QFont.Bold))
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.header)
        # -- Chart --
        self.chart = TotalEquityChartView()
        data = dbhandler.get_wealth_by_day()
        self.chart.setupChartWithData(data)
        self.layout.addWidget(self.chart)

        self.setLayout(self.layout)
