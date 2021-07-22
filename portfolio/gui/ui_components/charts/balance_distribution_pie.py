#!/usr/bin/python3

from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtChart import QChartView, QChart, QPieSeries

from portfolio.utils import confighandler
from portfolio.db.fdbhandler import balances
from portfolio.db.cdbhandler import cbalances
from portfolio.gui.ui_components.fonts import ChartTitleFont


class DistributionPieChart(QChartView):
    """
    Pie chart that shows the distribution of capital according
    to several criteria
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)

        # Chart
        self.chart = QChart()
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().hide()
        self.chart.createDefaultAxes()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundVisible(False)

        self.chart.setTitle("  ")
        self.chart.setTitleBrush(QBrush(QColor('white')))

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: 0px; background-color: rgba(0,0,0,0)")

        self.setupSeries()  # Initialize to all mode

    def setupSeries(self, mode="all"):
        """
        Chart gets updated displaying the new data.
        Modes:
            - all : distribution between all accounts
            - accs : distribution between portfolio accounts
            - cryptoaccs : distribution between crypto accounts
            - strategies : distribution between strategies

        """
        # Series
        self.chart.removeAllSeries()  # Remove any previous series
        self.series = QPieSeries()

        # Get data
        if mode == "all":
            data = balances.get_all_accounts(
            ) + cbalances.get_all_accounts_with_amount_fiat()

        elif mode == "accounts":
            data = balances.get_all_accounts()

        elif mode == "crypto":
            data = cbalances.get_all_accounts_with_amount_fiat()

        elif mode == "currency":
            data = [(confighandler.get_fiat_currency().upper(), balances.get_total_balance_all_accounts(
            )),  ("BTC", cbalances.get_total_balance_all_accounts_fiat())]
        data.sort(key=lambda x: x[1])  # Sort

        # Set Chart Title
        self.total = sum([i[1] for i in data])
        self.setDefaultTitle()

        # Add to series
        for d in data:
            self.series.append(d[0], d[1])

        # Hide little slices' labels
        self.series.setLabelsVisible(True)
        for slc in self.series.slices():
            if slc.angleSpan() < 5:
                slc.setLabelVisible(False)
                slc.setLabelArmLengthFactor(0.05)

        self.chart.addSeries(self.series)

        # Signals and functionality
        self.series.hovered.connect(self.selectSlice)

    def selectSlice(self, _slice, state):
        """ Highlight selected slice """
        font = ChartTitleFont()
        if state:
            font.setPointSize(20)
            _slice.setLabelVisible(True)
            self.chart.setTitle(
                f"{int(_slice.value())} {confighandler.get_fiat_currency().upper()} {round(_slice.percentage()*100,1)}%")
        else:
            font.setBold(False)
            if _slice.angleSpan() < 5:
                _slice.setLabelVisible(False)
            _slice.setExploded(False)
            self.setDefaultTitle()
        _slice.setLabelFont(font)

    def setDefaultTitle(self):
        """ Sets title as total balance from all pie slices """
        self.chart.setTitle(
            f"{int(self.total)} {confighandler.get_fiat_currency().upper()}")
        font = ChartTitleFont(fontsize=20)
        self.chart.setTitleFont(font)
