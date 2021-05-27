# /usr/bin/python3

from datetime import datetime
import calendar

from PyQt5.QtGui import QFont, QBrush, QColor, QPen, QPainter, QPalette
from PyQt5.QtCore import Qt, QDateTime

from PyQt5.QtChart import QPieSlice, QLineSeries, QDateTimeAxis, QValueAxis, QSplineSeries, QAbstractBarSeries
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis

from portfolio.utils import confighandler
from portfolio.db import dbhandler
from portfolio.db.fdbhandler import balances
from portfolio.db.cdbhandler import cbalances


class TotalWealthHistoryChartView(QChartView):
    """
    Chart that displays the balance between several dates
    from an account, token or whole portfolio
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.chart = QChart()

    def setupChartWithData(self, data):
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
        self.x_axis.setFormat("dd-MM-yy")
        self.x_axis.setTitleText(self.tr('Date'))
        self.x_axis.hide()

        # Axis Y (Balances)
        self.y_axis = QValueAxis()
        if data != {}:
            self.y_axis.setMax(max(data.values())*1.05)
            self.y_axis.setMin(min(data.values())*0.95)
        self.y_axis.hide()

        self.chart.addAxis(self.y_axis, Qt.AlignLeft)
        self.chart.addAxis(self.x_axis, Qt.AlignBottom)

        self.btcseries = QSplineSeries()
        for date in data:
            balance = data[date]
            date = datetime.fromtimestamp(int(float(date)))
            dateQ = QDateTime(date)
            # self.btcseries.append(dateQ.toMSecsSinceEpoch(), balance)
            self.btcseries.append(dateQ.toMSecsSinceEpoch(), balance)

        self.btcseries.setName("BTC")
        # self.btcseries.pen().setBrush(QBrush(QColor(207, 255, 170)))
        pen = QPen(QColor(207, 255, 170))
        pen.setWidth(2)
        self.btcseries.setPen(pen)

        self.chart.addSeries(self.btcseries)
        self.btcseries.attachAxis(self.x_axis)
        self.btcseries.attachAxis(self.y_axis)

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: 0px; background-color: rgba(0,0,0,0)")

        self.chart.legend().hide()


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
        dates = []
        amounts = []
        currentmonth = datetime.today().month
        currentyear = datetime.today().year

        # Get 5 previous month numbers
        for _ in range(5):
            dates.append((currentmonth, currentyear))
            currentmonth -= 1
            if currentmonth == 0:
                currentmonth = 12

        # Get amounts for each month
        for d in dates:
            month = d[0]
            year = d[1]
            amounts.append(
                dbhandler.get_total_wealth_on_month(month, year=year))

        # Iterate months and amount and insert them into the histogram appropiately
        barset = QBarSet('total wealth')
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
            date = datetime.fromtimestamp(int(float(date)))
            dateQ = QDateTime(date)
            # self.btcseries.append(dateQ.toMSecsSinceEpoch(), balance)
            self.btcseries.append(dateQ.toMSecsSinceEpoch(), balance)

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
        self.setStyleSheet(
            "border: 0px; background-color: rgba(0,0,0,0); ")

        self.chart.legend().hide()

    def selectPoint(self, point, state):
        """
        Shows point where mouse is hovered
        """
        self.chart.setTitle(
            f"{int(point.y())} {confighandler.get_fiat_currency().upper()}")


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
            data = balances.getAllAccounts(
            ) + cbalances.getAllAccountsWithAmount_fiat()

        elif mode == "accounts":
            data = balances.getAllAccounts()

        elif mode == "crypto":
            data = cbalances.getAllAccountsWithAmount_fiat()

        elif mode == "currency":
            data = [(confighandler.get_fiat_currency().upper(), balances.getTotalBalanceAllAccounts(
            )),  ("BTC", cbalances.getTotalBalanceAllAccounts_fiat())]

        # Sort
        data.sort(key=lambda x: x[1])

        # Set Chart Title
        self.total = sum([i[1] for i in data])
        self.setDefaultTitle()

        # Add to series
        for d in data:
            self.series.append(d[0], d[1])

        # Hide little slices
        self.series.setLabelsVisible(True)
        for slc in self.series.slices():
            if slc.angleSpan() < 5:
                slc.setLabelVisible(False)
                slc.setLabelArmLengthFactor(0.05)

        # Signals and functionality
        self.series.hovered.connect(self.selectSlice)

        self.chart.addSeries(self.series)

    def selectSlice(self, _slice, state):
        """
        Highlight selected slice
        """
        font = QFont()
        font.setFamily('Roboto')
        font.setPointSize(10)
        font.setBold(True)

        if state:
            font.setPointSize(20)
            font.setBold(True)
            _slice.setLabelVisible(True)
            # _slice.setExploded(True)
            self.chart.setTitle(
                f"{int(_slice.value())} {confighandler.get_fiat_currency().upper()} {round(_slice.percentage()*100,1)}%")
        else:
            font.setPointSize(10)
            font.setBold(False)
            if _slice.angleSpan() < 5:
                _slice.setLabelVisible(False)
            _slice.setExploded(False)
            self.setDefaultTitle()

        _slice.setLabelFont(font)

    def setDefaultTitle(self):
        """
        Sets title as total balance from all pie slices
        """
        self.chart.setTitle(
            f"{int(self.total)} {confighandler.get_fiat_currency().upper()}")
        titlefont = QFont()
        titlefont.setFamily('Roboto')
        titlefont.setPointSize(20)
        titlefont.setBold(True)
        self.chart.setTitleFont(titlefont)
