# /usr/bin/python3

from datetime import datetime

from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import QDateTime, Qt

from PyQt5.QtChart import QChartView, QChart, QDateTimeAxis, QValueAxis
from PyQt5.QtChart import QSplineSeries


class TotalWealthHistoryChartView(QChartView):
    """
    Chart that displays the balance between several dates
    from an account, token or whole portfolio
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.chart = QChart()

    def setupChartWithData(self, data: dict):
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
            date = QDateTime(datetime.fromtimestamp(int(float(date))))
            self.btcseries.append(date.toMSecsSinceEpoch(), balance)

        self.btcseries.setName("BTC")
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
