# /usr/bin/python3

from PyQt5.QtWidgets import QStatusBar, QLabel
import pandas_datareader as pdr


class StatusBar(QStatusBar):

    def __init__(self):
        super().__init__()

        self.showMessage("Bienvenido", 1000)

        # self.getLastSP500Close()

#    def getLastSP500Close(self):
#
#        try:
#            sp500 = (pdr.get_data_yahoo('^GSPC'))
#            price = str(sp500.iloc[-1].Close)
#        except:
#            price = "Error"
#        finally:
#            price = ("API Error SP500")
#
#        currentSP500Price = QLabel(price)
#
#        self.addPermanentWidget(currentSP500Price)
