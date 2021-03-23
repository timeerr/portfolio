#!/usr/bin/python3
"""
Dialog to import results form a variety of spreadsheet files
Once imported, the results are added to the database
"""

import os
from datetime import datetime
import csv
import pandas as pd

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QTableWidget, QLabel, QComboBox
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QPushButton, QTableView
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QAbstractTableModel
from PyQt5.QtGui import QCursor, QPixmap

from gui.dbhandler import results

RESOURCES_PATH = os.path.join(os.path.expanduser(
    '~'), '.local', 'share', 'portfolio')

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

        self.setWindowTitle(self.tr("Import results from CSV"))

        # UI
        self.layout = QVBoxLayout()

        # File Selection field
        self.file_selection = FileSelection(
            self.tr("Drag or click to select csv file"))
        self.file_selection.fileselectedsignal.selected.connect(
            self.updateWithFile)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(100)
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
            lambda i: self.table.selectColumn(i))
        self.date_column_lyt.addWidget(self.date_column_select_label)
        self.date_column_lyt.addWidget(self.date_column_select)
        self.data_manip_bttns_lyt.addLayout(self.date_column_lyt)

        self.account_column_lyt = QVBoxLayout()
        self.account_column_select_label = QLabel(self.tr("Account Column"))
        self.account_column_select = QComboBox()
        self.account_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.account_column_select.currentIndexChanged.connect(
            lambda i: self.table.selectColumn(i))
        self.account_column_lyt.addWidget(self.account_column_select_label)
        self.account_column_lyt.addWidget(self.account_column_select)
        self.data_manip_bttns_lyt.addLayout(self.account_column_lyt)

        self.amount_column_lyt = QVBoxLayout()
        self.amount_column_select_label = QLabel(self.tr("Amount Column"))
        self.amount_column_select = QComboBox()
        self.amount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.amount_column_select.currentIndexChanged.connect(
            lambda i: lambda i: self.table.selectColumn(i)(i))
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

    def updateWithFile(self, url):
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
                        self.table.setItem(row_count, column,
                                           QTableWidgetItem(str(data)))
        else:
            error = QMessageBox(self)
            icon = QPixmap(os.path.join(
                RESOURCES_PATH, 'warning.svg')).scaledToHeight(40)
            error.setIconPixmap(icon)
            error.setText(self.tr("File Invalid"))
            error.setInformativeText(
                self.tr("File must be in csv format"))
            error.setWindowTitle(self.tr("File Invalid"))
            error.exec_()

    def saveResults(self):
        """
        Parse TableWidget and add results on db
        """
        dateformat = self.date_parse_options.currentText()

        date_column = int(self.date_column_select.currentText())-1
        account_column = int(self.account_column_select.currentText())-1
        amount_column = int(self.amount_column_select.currentText())-1

        resultslist = []
        for rownum in range(self.table.rowCount()):

            if rownum == 0 and self.headers_hide.isChecked() is True:
                # Skipping first row
                continue
            date = self.parseDate(self.table.item(
                rownum, date_column).text(), dateformat)
            account = self.table.item(rownum, account_column).text()
            if "/" in account:
                new_account = ""
                for l in account:
                    if l == "/":
                        new_account += "-"
                    else:
                        new_account += l
                account = new_account
            if self.caps_matter.isChecked() is False:
                account = account.upper()
            amount = self.table.item(rownum, amount_column).text()
            if amount == '':
                amount = 0

            resultslist.append([date, account, amount])

        # Now, we iterate resultslist and add each result to the db
        for r in resultslist:
            print(r[0])
            print(r[1])
            print(r[2])
            results.addResult(r[0], r[1], r[2])

        # Done Message
        done = QMessageBox(self)
        icon = QPixmap(os.path.join(
            RESOURCES_PATH, 'tick.svg')).scaledToHeight(40)
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

        self.setWindowTitle(self.tr("Import results from Excel"))

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
        self.table.setColumnCount(100)
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
            lambda i: self.table.selectColumn(i))
        self.date_column_lyt.addWidget(self.date_column_select_label)
        self.date_column_lyt.addWidget(self.date_column_select)
        self.data_manip_bttns_lyt.addLayout(self.date_column_lyt)

        self.account_column_lyt = QVBoxLayout()
        self.account_column_select_label = QLabel(self.tr("Account Column"))
        self.account_column_select = QComboBox()
        self.account_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.account_column_select.currentIndexChanged.connect(
            lambda i: self.table.selectColumn(i))
        self.account_column_lyt.addWidget(self.account_column_select_label)
        self.account_column_lyt.addWidget(self.account_column_select)
        self.data_manip_bttns_lyt.addLayout(self.account_column_lyt)

        self.amount_column_lyt = QVBoxLayout()
        self.amount_column_select_label = QLabel(self.tr("Amount Column"))
        self.amount_column_select = QComboBox()
        self.amount_column_select.addItems(
            [str(i) for i in range(1, self.table.columnCount()+1)])
        self.amount_column_select.currentIndexChanged.connect(
            lambda i: self.table.selectColumn(i))
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
                RESOURCES_PATH, 'warning.svg')).scaledToHeight(40)
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
        account_column = int(self.account_column_select.currentText())-1
        amount_column = int(self.amount_column_select.currentText())-1

        resultslist = []
        for rownum in range(self.table.model().rowCount()):
            # To access QTableView data, we call the model that is built upon
            raw_date = self.table.model().index(rownum, date_column).data()
            if raw_date in ['nan', 'NaT']:
                # Row is considered empty, skipped
                continue

            date = self.parseDate(raw_date, dateformat)
            account = self.table.model().index(rownum, account_column).data()
            if "/" in account:
                new_account = ""
                for l in account:
                    if l == "/":
                        new_account += "-"
                    else:
                        new_account += l
                account = new_account
            if self.caps_matter.isChecked() is False:
                account = account.upper()

            amount = self.table.model().index(rownum, amount_column).data()

            resultslist.append([date, account, amount])

        print(resultslist)
        # Now, we iterate resultslist and add each result to the db
        for r in resultslist:
            try:
                results.addResult(r[0], r[1], r[2])
            except:
                print("Error adding result", r[0], r[1], r[2])

        # Done Message
        done = QMessageBox(self)
        icon = QPixmap(os.path.join(
            RESOURCES_PATH, 'tick.svg')).scaledToHeight(40)
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
    """
    Dialog that shows whenever the date format does not
    match the one that the user has selected
    """

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warning_lyt = QVBoxLayout()
        self.warning_lyt_top = QHBoxLayout()

        self.icon = QLabel()
        pxmp = QPixmap(os.path.join(RESOURCES_PATH, "warning.svg")
                       ).scaledToHeight(40)
        self.icon.setPixmap(pxmp)
        self.warningtext = QLabel("Date format does not match data")

        self.warning_lyt_top.addWidget(self.icon)
        self.warning_lyt_top.addWidget(self.warningtext)

        self.closebttn = QPushButton("Close")
        self.closebttn.clicked.connect(lambda: self.close())

        self.warning_lyt.addLayout(self.warning_lyt_top)
        self.warning_lyt.addWidget(self.closebttn)
        self.setLayout(self.warning_lyt)


# --- Custom Signals----
class FileSelectedSignal(QObject):
    """
    Signal that is supposed to be emitted whenever 
    a file has been selected by the user
    """
    selected = pyqtSignal(str)
