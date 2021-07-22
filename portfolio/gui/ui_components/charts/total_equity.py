#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtChart import QChartView, QDateTimeAxis, QChart
from PyQt5.QtChart import QValueAxis, QSplineSeries

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen, QPainter

from portfolio.utils import confighandler


class TotalEquityChartView(QChartView):
    """
    Chart that displays the balance between several dates
    from an account, token or whole portfolio
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.chart = QChart()

    def setupChartWithData(self, data, linecolor='#422F8A'):
        """
        Chart gets updated displaying the new data.

        Data has to be expressed on a dictionary form:
            - keys are timestamps
            - values are total balance for that timestamp
        """
        self.chart = QChart()

        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor("transparent")))
#         self.chart.setTitle("")
#         self.chart.setTitleBrush(QBrush(QColor('white')))

        # Axis X (Dates)
        self.x_axis = QDateTimeAxis()
        self.x_axis.setTickCount(11)
        self.x_axis.setLabelsAngle(70)
        font = QFont()
        font.setFamily('Roboto')
        font.setLetterSpacing(QFont.PercentageSpacing, 110)
        font.setPointSize(8)
        self.x_axis.setLabelsFont(font)
        self.x_axis.setFormat("dd-MM-yy")
        self.x_axis.setTitleText(self.tr('Date'))
        self.x_axis.setTitleVisible(False)
        self.x_axis.setLineVisible(False)
        self.x_axis.setGridLineVisible(False)

        # Axis Y (Balances)
        self.y_axis = QValueAxis()
        if data != {}:
            self.y_axis.setMax(max(data.values())*1.05)
            self.y_axis.setMin(min(data.values())*0.95)
        # self.y_axis.setMinorGridLineVisible(False)
        self.y_axis.setLineVisible(False)
        self.y_axis.setGridLineColor(QColor("#ECE9F1"))

        self.chart.addAxis(self.y_axis, Qt.AlignLeft)
        self.chart.addAxis(self.x_axis, Qt.AlignBottom)

        # Series
        self.btcseries = QSplineSeries()
        for date in data:
            balance = data[date]
            date = QDateTime(datetime.fromtimestamp(int(float(date))))
            self.btcseries.append(date.toMSecsSinceEpoch(), balance)

        self.btcseries.setName("BTC")
        pen = QPen(QColor(linecolor))
        pen.setWidth(3)
        self.btcseries.setPen(pen)

        # Series functionality
        self.btcseries.hovered.connect(self.selectPoint)

        self.chart.addSeries(self.btcseries)
        self.btcseries.attachAxis(self.x_axis)
        self.btcseries.attachAxis(self.y_axis)

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: 0px; background-color: rgba(0,0,0,0); ")

        self.chart.legend().hide()

    def selectPoint(self, point, state):
        """ Shows point where mouse is hovered """
        self.chart.setTitle(
            f"{int(point.y())} {confighandler.get_fiat_currency().upper()}")
