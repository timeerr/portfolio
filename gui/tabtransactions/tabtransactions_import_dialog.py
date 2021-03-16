#!/usr/bin/python3
"""
Dialog to import transactions form a variety of spreadsheet files
Once imported, the transactions are added to the database
"""


import os
import csv
from datetime import datetime
import pandas as pd

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QComboBox, QPushButton, QTableView
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QTableWidget, QLabel
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QAbstractTableModel
from PyQt5.QtGui import QCursor, QPixmap

from gui.dbhandler import transactions

DATE_FORMATS = ["UNIX", "DD/MM/YYYY",  "DD-MM-YYY",
                "MM/DD/YYYY", "MM-DD-YYYY", "YYYY-MM-DD",
                "DD/MM/YYYY HH:MM:SS", "DD-MM-YYYY HH:MM:SS",
                "MM/DD/YYYY HH:MM:SS",
                "MM-DD-YYYY HH:MM:SS",
                "YYYY-MM-DD HH:MM:SS"]


class SelectTypeDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Select File Type"))
        self.layout = QVBoxLayout()

        # CSV Button and Dialog
        self.csvbttn = QPushButton("CSV")
        self.csvbttn.clicked.connect(self.csvSelected)
        self.csvimportdialog = CSVImportDialog(self)
        self.csvimportdialog.hide()

        # Excel Button and Dialog
        self.xlsxbttn = QPushButton("Excel")
        self.xlsxbttn.clicked.connect(self.xlsxSelected)
        self.xlsximportdialog = ExcelImportDialog(self)
        self.xlsximportdialog.hide()

        self.layout.addWidget(self.csvbttn)
        self.layout.addWidget(self.xlsxbttn)
        self.setLayout(self.layout)

    def csvSelected(self):
        """
        Displaying the CSVImportDialog
        """
        self.csvimportdialog.show()
        self.close()

    def xlsxSelected(self):
        """
        Displaying the ExcelImportDialog
        """
        self.xlsximportdialog.show()
        self.close()


class CSVImportDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Import transactions from CSV"))

        # UI
        self.layout = QVBoxLayout()

        # File Selection field
        self.file_selection = FileSelection(
            self.tr("Drag or click to select csv file"))
        self.file_selection.fileselectedsignal.selected.connect(
            lambda url: self.updateWithFile(url))

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table_lyt = QVBoxLayout()
        self.table_lyt.addWidget(self.table)

        # Data manipulation buttons
        self.data_manip_bttns_lyt = QHBoxLayout()

        self.parse_date_lyt = QVBoxLayout()
        self.date_parse_options = QComboBox()
        self.date_parse_options.addItems(DATE_FORMATS)
        self.date_parse_label = QLabel(self.tr("Date Format"))
        self.parse_date_lyt.addWidget(self.date_parse_label)
        self.parse_date_lyt.addWidget(self.date_parse_options)
        self.data_manip_bttns_lyt.addLayout(self.parse_date_lyt)

        self.date_column_lyt = QVBoxLayout()
        self.date_column_select_label = QLabel(self.tr("Date Column"))
        self.date_column_select = QComboBox()
        self.date_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.date_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.date_column_lyt.addWidget(self.date_column_select_label)
        self.date_column_lyt.addWidget(self.date_column_select)
        self.data_manip_bttns_lyt.addLayout(self.date_column_lyt)

        # Select which column correspond to the sender accounts
        self.senderaccount_column_lyt = QVBoxLayout()
        self.senderaccount_column_select_label = QLabel(
            self.tr("Sender Account Column"))
        self.senderaccount_column_select = QComboBox()
        self.senderaccount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.senderaccount_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.senderaccount_column_lyt.addWidget(
            self.senderaccount_column_select_label)
        self.senderaccount_column_lyt.addWidget(
            self.senderaccount_column_select)
        self.data_manip_bttns_lyt.addLayout(self.senderaccount_column_lyt)

        # Select which column correspond to the receiver accounts
        self.receiveraccount_column_lyt = QVBoxLayout()
        self.receiveraccount_column_select_label = QLabel(
            self.tr("Receiver Account Column"))
        self.receiveraccount_column_select = QComboBox()
        self.receiveraccount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.receiveraccount_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.receiveraccount_column_lyt.addWidget(
            self.receiveraccount_column_select_label)
        self.receiveraccount_column_lyt.addWidget(
            self.receiveraccount_column_select)
        self.data_manip_bttns_lyt.addLayout(
            self.receiveraccount_column_lyt)

        # Select which column correspond to the amounts
        self.amount_column_lyt = QVBoxLayout()
        self.amount_column_select_label = QLabel(self.tr("Amount Column"))
        self.amount_column_select = QComboBox()
        self.amount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.amount_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.amount_column_lyt.addWidget(self.amount_column_select_label)
        self.amount_column_lyt.addWidget(self.amount_column_select)
        self.data_manip_bttns_lyt.addLayout(self.amount_column_lyt)

        self.headers_hide = QPushButton(self.tr("Skip Headers"))
        self.headers_hide.setCheckable(True)
        self.headers_hide.setMaximumHeight(55)
        self.data_manip_bttns_lyt.addWidget(self.headers_hide)

        # Distinguish between caps
        self.caps_matter = QPushButton(self.tr("Distinguish Caps"))
        self.caps_matter.setCheckable(True)
        self.caps_matter.setMaximumHeight(55)
        self.data_manip_bttns_lyt.addWidget(self.caps_matter)

        # Save results button
        self.save_results = QPushButton(self.tr("Save Results"))
        self.save_results.clicked.connect(self.saveResults)

        self.layout.addWidget(self.file_selection)
        self.layout.addLayout(self.table_lyt)
        self.layout.addLayout(self.data_manip_bttns_lyt)
        self.layout.addWidget(self.save_results)
        self.setLayout(self.layout)

        # Incorrect Date Format Error
        self.dateformat_error = BadDateError()
        self.dateformat_error.hide()

        # Data
        self.url = ''

    def updateWithFile(self, url, sheet=None):
        """Updating the table with the new file selected"""

        if url.split('.')[-1] == 'csv':

            self.url = url
            with open(url, newline='') as file:  # Getting data size
                getlenghts = csv.reader(file, delimiter=',', quotechar='|')
                row_lenght = sum(1 for row in getlenghts)
                self.table.setRowCount(row_lenght)

            with open(url, newline='') as file:
                filerows = csv.reader(file, delimiter=',', quotechar='|')

                # Populating table
                for row_count, row in enumerate(filerows):
                    for column, data in enumerate(row):
                        data = str(data)
                        self.table.setItem(row_count, column,
                                           QTableWidgetItem(data))
        else:
            self.error = QMessageBox(self)
            icon = QPixmap(os.path.join(
                'resources', 'warning.svg')).scaledToHeight(40)
            self.error.setIconPixmap(icon)
            self.error.setText(self.tr("File Invalid"))
            self.error.setInformativeText(
                self.tr("File must be in csv format"))
            self.error.setWindowTitle(self.tr("File Invalid"))
            self.error.exec_()

    def saveResults(self):
        """
        Parse TableWidget and add results on db
        """
        dateformat = self.date_parse_options.currentText()

        date_column = int(self.date_column_select.currentText())-1
        senderaccount_column = int(self.account_column_select.currentText())-1
        receiveraccount_column = int(
            self.account_column_select.currentText())-1
        amount_column = int(self.amount_column_select.currentText())-1

        transactionslist = []
        for rownum in range(self.table.rowCount()):

            if rownum == 0 and self.headers_hide.isChecked() is True:
                # Skipping first row
                continue
            date = self.parseDate(self.table.item(
                rownum, date_column).text(), dateformat)
            senderaccount = self.table.item(
                rownum, senderaccount_column).text()
            for letter in senderaccount:
                formatted = ""
                if letter == '-':
                    formatted += '/'
                else:
                    formatted += letter
            senderaccount = formatted
            if self.caps_matter.isChecked() is False:
                senderaccount = senderaccount.upper()
            receiveraccount = self.table.item(
                rownum, receiveraccount_column).text()
            for letter in receiveraccount:
                formatted = ""
                if letter == '-':
                    formatted += '/'
                else:
                    formatted += letter
            receiveraccount = formatted
            if self.caps_matter.isChecked() is False:
                receiveraccount = receiveraccount.upper()
            amount = self.table.item(rownum, amount_column).text()

            transactionslist.append(
                [date, senderaccount, amount, receiveraccount])

        # Now, we iterate resultslist and add each result to the db
        for t in transactionslist:
            print(t[0])
            print(t[1])
            print(t[2])
            print(t[3])
            transactions.addTransaction(t[0], t[1], t[2], t[3], 0)

        # Done Message
        done = QMessageBox(self)
        icon = QPixmap(os.path.join(
            'resources', 'tick.svg')).scaledToHeight(40)
        done.setIconPixmap(icon)
        done.setText(self.tr("Results Succesfully Added"))
        done.setInformativeText(self.tr("Restart App required"))
        done.setWindowTitle(self.tr("Done"))
        done.exec_()
        self.close()

    def parseDate(self, date, dateformat):
        """
        Converts date string into datetime object according to the dateformat specification
        """
        try:
            if dateformat == "UNIX":
                result = datetime.fromtimestamp(int(date))
            elif dateformat == "DD/MM/YYYY":
                result = datetime.strptime(date, "%d/%m/%Y")
            elif dateformat == "DD-MM-YYY":
                result = datetime.strptime(date, "%d-%m-%Y")
            elif dateformat == "MM/DD/YYYY":
                result = datetime.strptime(date, "%m/%d/%Y")
            elif dateformat == "MM-DD-YYYY":
                result = datetime.strptime(date, "%m-%d-%Y")
            elif dateformat == "YYYY-MM-DD":
                result = datetime.strptime(date, "%Y/%m/%d")

            elif dateformat == "DD/MM/YYYY HH:MM:SS":
                result = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
            elif dateformat == "DD-MM-YYYY HH:MM:SS":
                result = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
            elif dateformat == "MM/DD/YYYY HH:MM:SS":
                result = datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
            elif dateformat == "MM-DD-YYYY HH:MM:SS":
                result = datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
            elif dateformat == "YYYY-MM-DD HH:MM:SS":
                result = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            self.dateformat_error.hide()

        except:
            self.dateformat_error.show()
            raise TypeError("Date does not match format")

        return result.timestamp()


class ExcelImportDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Import transactions from Excel"))

        # UI
        self.layout = QVBoxLayout()

        # File Selection field
        self.file_selection = FileSelection(
            self.tr("Drag or click to select xlsx/xlsxm file"))
        self.file_selection.fileselectedsignal.selected.connect(
            self.updateWithFile)

        # Sheet selection (for xlsx files)
        self.sheetselection = QComboBox()
        self.sheetselection.currentTextChanged.connect(
            lambda sheet: self.updateWithFileAndSheet(self.url, sheet))

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table_lyt = QVBoxLayout()
        self.table_lyt.addWidget(self.table)

        # Data manipulation buttons
        self.data_manip_bttns_lyt = QHBoxLayout()

        self.parse_date_lyt = QVBoxLayout()
        self.date_parse_options = QComboBox()
        self.date_parse_options.addItems(DATE_FORMATS)
        self.date_parse_label = QLabel(self.tr("Date Format"))
        self.parse_date_lyt.addWidget(self.date_parse_label)
        self.parse_date_lyt.addWidget(self.date_parse_options)
        self.data_manip_bttns_lyt.addLayout(self.parse_date_lyt)

        self.date_column_lyt = QVBoxLayout()
        self.date_column_select_label = QLabel(self.tr("Date Column"))
        self.date_column_select = QComboBox()
        self.date_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.date_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.date_column_lyt.addWidget(self.date_column_select_label)
        self.date_column_lyt.addWidget(self.date_column_select)
        self.data_manip_bttns_lyt.addLayout(self.date_column_lyt)

        # Select which column correspond to the sender accounts
        self.senderaccount_column_lyt = QVBoxLayout()
        self.senderaccount_column_select_label = QLabel(
            self.tr("Sender Account Column"))
        self.senderaccount_column_select = QComboBox()
        self.senderaccount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.senderaccount_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.senderaccount_column_lyt.addWidget(
            self.senderaccount_column_select_label)
        self.senderaccount_column_lyt.addWidget(
            self.senderaccount_column_select)
        self.data_manip_bttns_lyt.addLayout(self.senderaccount_column_lyt)

        # Select which column correspond to the sender accounts
        self.receiveraccount_column_lyt = QVBoxLayout()
        self.receiveraccount_column_select_label = QLabel(
            self.tr("Receiver Account Column"))
        self.receiveraccount_column_select = QComboBox()
        self.receiveraccount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.receiveraccount_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.receiveraccount_column_lyt.addWidget(
            self.receiveraccount_column_select_label)
        self.receiveraccount_column_lyt.addWidget(
            self.receiveraccount_column_select)
        self.data_manip_bttns_lyt.addLayout(self.receiveraccount_column_lyt)

        self.amount_column_lyt = QVBoxLayout()
        self.amount_column_select_label = QLabel(self.tr("Amount Column"))
        self.amount_column_select = QComboBox()
        self.amount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.amount_column_select.currentIndexChanged.connect(
            self.table.selectColumn)
        self.amount_column_lyt.addWidget(self.amount_column_select_label)
        self.amount_column_lyt.addWidget(self.amount_column_select)
        self.data_manip_bttns_lyt.addLayout(self.amount_column_lyt)

        # Distinguish between caps
        self.caps_matter = QPushButton(self.tr("Distinguish Caps"))
        self.caps_matter.setCheckable(True)
        self.caps_matter.setMaximumHeight(55)
        self.data_manip_bttns_lyt.addWidget(self.caps_matter)

        # Save results button
        self.save_results = QPushButton(self.tr("Save Results"))
        self.save_results.clicked.connect(self.saveResults)

        self.layout.addWidget(self.file_selection)
        self.layout.addWidget(self.sheetselection)
        self.layout.addLayout(self.table_lyt)
        self.layout.addLayout(self.data_manip_bttns_lyt)
        self.layout.addWidget(self.save_results)
        self.setLayout(self.layout)

        # Incorrect Date Format Error
        self.dateformat_error = BadDateError()
        self.dateformat_error.hide()

        # Data
        self.url = ''

    def updateWithFile(self, url):
        if url.split('.')[-1] in ['xlsx', 'xlsm']:
            self.url = url
            sheetnames = pd.ExcelFile(url).sheet_names
            self.sheetselection.clear()
            self.sheetselection.addItems(sheetnames)

        else:
            error = QMessageBox(self)
            icon = QPixmap(os.path.join(
                'resources', 'warning.svg')).scaledToHeight(40)
            error.setIconPixmap(icon)
            error.setText(self.tr("File Invalid"))
            error.setInformativeText(self.tr("File must be in csv format"))
            error.setWindowTitle(self.tr("File Invalid"))
            error.exec_()

    def updateWithFileAndSheet(self, url, sheet):
        df_file = pd.read_excel(url, sheet_name=sheet, engine='openpyxl')
        model = PandasModel(df_file)
        print(df_file)
        table = QTableView()
        table.setModel(model)
        self.table.deleteLater()
        self.table = table
        self.table_lyt.addWidget(self.table)

    def saveResults(self):
        # Parse TableWidget and add results on db
        dateformat = self.date_parse_options.currentText()

        date_column = int(self.date_column_select.currentText())-1
        senderaccount_column = int(
            self.senderaccount_column_select.currentText())-1
        receiveraccount_column = int(
            self.receiveraccount_column_select.currentText())-1
        amount_column = int(self.amount_column_select.currentText())-1

        transactionslist = []
        # To access QTableView data, we call the model that is built upon
        for rownum in range(self.table.model().rowCount()):
            # Date
            raw_date = self.table.model().index(rownum, date_column).data()
            if raw_date in ['nan', 'NaT']:
                # Row is considered empty, skipped
                continue
            date = self.parseDate(raw_date, dateformat)

            # Sender Account
            senderaccount = self.table.model().index(rownum, senderaccount_column).data()
            # Dealing with string formatting
            if "/" in senderaccount:
                new_senderaccount = ""
                for l in senderaccount:
                    if l == "/":
                        new_senderaccount += "-"
                    else:
                        new_senderaccount += l
                senderaccount = new_senderaccount
            if self.caps_matter.isChecked() is False:
                senderaccount = senderaccount.upper()
            # Receiver Account
            receiveraccount = self.table.model().index(
                rownum, receiveraccount_column).data()
            if "/" in receiveraccount:
                new_receiveraccount = ""
                for l in receiveraccount:
                    if l == "/":
                        new_receiveraccount += "-"
                    else:
                        new_receiveraccount += l
                receiveraccount = new_receiveraccount
            if self.caps_matter.isChecked() is False:
                receiveraccount = receiveraccount.upper()
            # Amount
            amount = self.table.model().index(rownum, amount_column).data()
            if amount in ['nan', 'NaT']:
                # Row is considered empty, skipped
                continue

            transactionslist.append(
                [date, senderaccount, amount, receiveraccount])
            print("Adding transaction on db: ", date,
                  senderaccount, amount, receiveraccount)

        # Now, we iterate resultslist and add each result to the db
        for t in transactionslist:
            transactions.addTransaction(t[0], t[1], t[2], t[3], 0)

        # Done Message
        done = QMessageBox(self)
        icon = QPixmap(os.path.join(
            'resources', 'tick.svg')).scaledToHeight(40)
        done.setIconPixmap(icon)
        done.setText(self.tr("Results Succesfully Added"))
        done.setInformativeText(self.tr("Restart App required"))
        done.setWindowTitle(self.tr("Done"))
        done.exec_()
        self.close()

    def parseDate(self, date, dateformat):
        # Converts date string into datetime object according to the dateformat specification
        try:
            if dateformat == "UNIX":
                result = datetime.fromtimestamp(int(date))
            elif dateformat == "DD/MM/YYYY":
                result = datetime.strptime(date, "%d/%m/%Y")
            elif dateformat == "DD-MM-YYYY":
                result = datetime.strptime(date, "%d-%m-%Y")
            elif dateformat == "MM/DD/YYYY":
                result = datetime.strptime(date, "%m/%d/%Y")
            elif dateformat == "MM-DD-YYYY":
                result = datetime.strptime(date, "%m-%d-%Y")
            elif dateformat == "YYYY-MM-DD":
                result = datetime.strptime(date, "%Y/%m/%d")

            elif dateformat == "DD/MM/YYYY HH:MM:SS":
                result = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
            elif dateformat == "DD-MM-YYYY HH:MM:SS":
                result = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
            elif dateformat == "MM/DD/YYYY HH:MM:SS":
                result = datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
            elif dateformat == "MM-DD-YYYY HH:MM:SS":
                result = datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
            elif dateformat == "YYYY-MM-DD HH:MM:SS":
                result = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            self.dateformat_error.hide()  # In case it was previously shown due to an error

        except:
            self.dateformat_error.show()  # Show Dialog explaining error
            raise TypeError("Date does not match format")

        return result.timestamp()


class FileSelection(QLabel):
    """This is the part where a file gets selected, either through dragging and dropping a file
    or selecting it from a dialog

    When the file is finally selected, this object will emit a signal"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(
            "border: 2px grey; border-style: dashed; font-style: italic")
        self.setMinimumHeight(60)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)

        # Signals
        self.fileselectedsignal = FileSelectedSignal()

    def dragEnterEvent(self, event):
        # Only accept if dragged file is a local file
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = (event.mimeData().urls())[0].path()
        self.fileselectedsignal.selected.emit(url)

    def mousePressEvent(self, event):
        self.filedialog = QFileDialog()
        self.filedialog.show()
        self.filedialog.fileSelected.connect(
            self.fileselectedsignal.selected.emit)


class PandasModel(QAbstractTableModel):
    """
    Table model to properly show a pandas dataframe
    """

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class BadDateError(QDialog):

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warning_lyt = QVBoxLayout()
        self.warning_lyt_top = QHBoxLayout()

        self.icon = QLabel()
        pxmp = QPixmap(os.path.join("resources", "warning.svg")
                       ).scaledToHeight(40)
        self.icon.setPixmap(pxmp)
        self.warningtext = QLabel(self.tr("Date format does not match data"))

        self.warning_lyt_top.addWidget(self.icon)
        self.warning_lyt_top.addWidget(self.warningtext)

        self.closebttn = QPushButton(self.tr("Close"))
        self.closebttn.clicked.connect(lambda: self.close())

        self.warning_lyt.addLayout(self.warning_lyt_top)
        self.warning_lyt.addWidget(self.closebttn)
        self.setLayout(self.warning_lyt)


# --- Custom Signals----
class FileSelectedSignal(QObject):
    selected = pyqtSignal(str)
