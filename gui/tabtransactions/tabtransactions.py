#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt, QMargins

from gui.dbhandler import transactions
from gui.tabtransactions.tabtransactions_leftlayout import LeftLayout
from gui.tabtransactions.tabtransactions_righttable import RightTable


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
        self.righttable = RightTable()
        self.rightlayout.addWidget(self.righttable, Qt.AlignCenter)

        # ------Main Layout----------------
        self.rightlayout_widget.setLayout(self.rightlayout)
        self.leftlayout_widget.setLayout(self.leftlayout)

        self.insertWidget(0, self.leftlayout_widget)
        self.insertWidget(1, self.rightlayout_widget)

    def updateRightLayout(self):

        # Getting current form state
        current_startdate = datetime.strptime(
            self.leftlayout.form.start_date_edit.date().toString("dd.MM.yyyy"), "%d.%m.%Y")
        current_enddate = datetime.strptime(
            self.leftlayout.form.end_date_edit.date().toString("dd.MM.yyyy"), "%d.%m.%Y")
        current_senderaccount = self.leftlayout.form.senderaccount_select.currentText()
        current_receiveraccount = self.leftlayout.form.receiveraccount_select.currentText()

        # Changing with new data
        self.righttable.setData(
            current_startdate, current_enddate, current_senderaccount, current_receiveraccount)

        # Show message on status bar with the new transaction info
        self.parent().parent().parent().parent().statusBar().showMessage(
            "".join([self.tr("New transaction added: "), current_startdate.strftime("%d/%m/%Y"),
                     current_enddate.strftime("%d/%m/%Y"), current_senderaccount, current_receiveraccount]))
