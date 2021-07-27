#!/usr/bin/python3

from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QFrame, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from portfolio.gui.ui_components.charts.balance_distribution_pie import DistributionPieChart
from portfolio.gui.ui_components.styles import GradientStyle, DistributionButtonStyle


class DistributionWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("distribution")
        # ---- UI ----
        # Background image
        self.setStyleSheet(GradientStyle.get(
            self.objectName(), '#65B585', '#273B4F'))
        #  Size
        #self.setMaximumSize(645, 665)
        # ---- Content ----
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(45, 45, 45, 45)
        self.layout.setSpacing(30)
        # -- Header --
        self.header = QLabel(self.tr("Distribution"))
        self.header.setStyleSheet(
            "background-color: rgba(0,0,0,0);")
        self.header.setFont(QFont('Roboto', pointSize=20, weight=QFont.Bold))
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.addWidget(self.header)
        # -- Buttons --
        self.buttons_layout = QHBoxLayout()
        self.accs = DistributionButton(self.tr("Accounts"))
        self.cryptoaccs = DistributionButton(self.tr("Crypto"))
        self.strategies = DistributionButton(self.tr("Currency"))
        self.bttns = (self.accs, self.cryptoaccs, self.strategies)
        for bttn in self.bttns:
            self.buttons_layout.addWidget(bttn)
        self.layout.addLayout(self.buttons_layout)
        # -- Chart --
        self.chart = DistributionPieChart()
        self.layout.addWidget(self.chart)

        # ---- Functionality ----
        # Connect button checks to handle them
        self.accs.clicked.connect(
            lambda checked: self.handleCheck(self.accs, checked))
        self.cryptoaccs.clicked.connect(
            lambda checked: self.handleCheck(self.cryptoaccs, checked))
        self.strategies.clicked.connect(
            lambda checked: self.handleCheck(self.strategies, checked))

        self.setLayout(self.layout)

    def handleCheck(self, button, checked):
        """ Only one button can be selected at a time """
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
    def __init__(self, *args, color_num=1, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- UI ----
        self.setStyleSheet(DistributionButtonStyle.get(color_num=color_num))
        self.setFont(QFont('Roboto', pointSize=15, weight=QFont.Bold))
        self.setCheckable(True)
