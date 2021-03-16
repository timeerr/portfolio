#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt, QMargins

from gui.dbhandler import transactions
from .tabtransactions_leftlayout import LeftLayout
from .tabtransactions_righttable import RightTable


class TabTransactions(QSplitter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Transactions"))
        self.setHandleWidth(2)
        # self.setWindowIcon(QIcon(os.path.join("icons", "FSA_circular.png")))

        self.mainlayout = QHBoxLayout()
        self.leftlayout = LeftLayout()  # It's actually a QSplitter
        self.rightlayout = QVBoxLayout()

        self.rightlayout_widget = QWidget()
        self.leftlayout_widget = QWidget()

        # Just limiting the max width so that it cannot be expanded too much
        self.leftlayout_widget.setMaximumWidth(600)
        self.leftlayout_widget.setContentsMargins(QMargins(20, 20, 20, 20))

        # ------Left Layout Widgets------
        # Functionality between layouts
        #   Adding a link between the left layout pushbutton and the right layout data that is displayer
        self.leftlayout.update_query_pushbutton.clicked.connect(
            self.updateRightLayout)
        self.leftlayout.add_transactions_form.insert_button.clicked.connect(
            self.updateRightLayout)

        # ------Right Layout Widgets------
        all_transactions = transactions.getTransactions_All()
        self.righttable = RightTable()
        self.righttable.changeData(all_transactions)
        self.rightlayout.addWidget(self.righttable, Qt.AlignCenter)

        # ------Main Layout----------------
        self.rightlayout_widget.setLayout(self.rightlayout)
        self.leftlayout_widget.setLayout(self.leftlayout)

        self.insertWidget(0, self.leftlayout_widget)
        self.insertWidget(1, self.rightlayout_widget)

    def updateRightLayout(self):

        # Getting current form state
        current_query = self.leftlayout.form.getCurrentQuery()
        newdata = transactions.getTransactions_fromQuery(
            start_date=current_query[0], end_date=current_query[1], senderaccount=current_query[2], receiveraccount=current_query[3])

        # Changing with new data
        self.righttable.changeData(newdata)
        self.righttable.changeData(
            newdata)
        # """ THIS IS A BUG, AS IF THE DATA IS CHANGED JUST ONCE, THE TABLE GRID RESIZES, BUT THE DATA DOES NOT SHOW UP UNTIL UPDATED FOR A SECOND TIME"""

        # Show message on status bar with the new transaction info
        self.parent().parent().parent().parent().statusBar().showMessage(
            "".join([self.tr("New transaction added: "), current_query[0].strftime("%d/%m/%Y"),
                     current_query[1].strftime("%d/%m/%Y"), current_query[2], current_query[3]]))
