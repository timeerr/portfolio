#!/usr/bin/python3

from datetime import datetime
import calendar

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter

from PyQt5.QtChart import QChartView, QChart, QValueAxis, QBarSet
from PyQt5.QtChart import QAbstractBarSeries, QBarSeries, QBarCategoryAxis

from portfolio.db import dbhandler


class LastMonthsHistogram(QChartView):
    """
    Chart that displays the balance
    from the whole portfolio from the last months
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.chart = QChart()

    def setupChartWithData(self):
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

        # Series
        self.barseries = QBarSeries()

        currentyear, currentmonth = datetime.today().year, datetime.today().month
        dates, amounts = [], []
        # Get 5 previous month numbers
        for _ in range(5):
            dates.append((currentmonth, currentyear))
            currentmonth -= 1
            if currentmonth == 0:
                currentmonth = 12
                currentyear -= 1
        # Get amounts for each month
        for d in dates:
            month, year = d
            amounts.append(
                dbhandler.get_total_wealth_on_month(month, year=year))

        # Iterate months and amount and insert them into the histogram appropiately
        barset = QBarSet('Total wealth')
        labelsfont = QFont()
        labelsfont.setFamily('Inter')
        labelsfont.setBold(True)
        barset.setLabelFont(labelsfont)
        barset.setColor(QColor("#D3EABD"))
        x_values = []
        for d, a in zip(reversed(dates), reversed(amounts)):
            if a > 0:
                barset.append(int(a))
                x_values.append(calendar.month_name[d[0]])

        self.barseries.append(barset)
        self.barseries.setName("Last Months")
        self.barseries.setLabelsVisible(True)
        self.barseries.setBarWidth(0.2)
        self.barseries.setLabelsPosition(QAbstractBarSeries.LabelsOutsideEnd)
        self.chart.addSeries(self.barseries)

        # Axis X (Dates)
        self.x_axis = QBarCategoryAxis()
        self.x_axis.setTitleText(self.tr('Date'))
        labelsfont = QFont()
        labelsfont.setFamily('Roboto')
        labelsfont.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        labelsfont.setWeight(QFont.Light)
        labelsfont.setPointSize(9)
        self.x_axis.setLabelsFont(labelsfont)
        self.x_axis.setGridLineVisible(False)
        self.x_axis.setLineVisible(False)
        self.x_axis.setLinePenColor(QColor("#D3EABD"))
        self.x_axis.setTitleVisible(False)

        self.x_axis.append(x_values)
        self.chart.addAxis(self.x_axis, Qt.AlignBottom)

        # Axis Y (Balances)
        self.y_axis = QValueAxis()
        self.y_axis.setMax(max(amounts)*1.3)
        self.y_axis.setMin(min(amounts)*0.95)
        self.y_axis.hide()

        labelsfont = QFont()
        labelsfont.setPointSize(4)
        self.y_axis.setLabelsFont(labelsfont)
        self.chart.addAxis(self.y_axis, Qt.AlignLeft)

        # Attach axis to series
        self.barseries.attachAxis(self.x_axis)
        self.barseries.attachAxis(self.y_axis)

        # Legend
        self.chart.legend().hide()

        # Set up chart on ChartView
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: 0px; background-color: rgba(0,0,0,0)")
