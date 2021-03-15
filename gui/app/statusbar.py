# /usr/bin/python3

from PyQt5.QtWidgets import QStatusBar, QLabel



class StatusBar(QStatusBar):

    def __init__(self):
        super().__init__()

        self.showMessage(self.tr("Bienvenido"), 1000)

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
