#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QAbstractItemView, QMenu, QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from gui.dbhandler import results, strategies, balances


def updatingdata(func):
    """
    Decorator to flag self.updatingdata_flag whenever a function
    that edits data without user intervention is being run
    """

    def wrapper(self, *args, **kwargs):
        self.updatingdata_flag = True
        func(self, *args, **kwargs)
        self.updatingdata_flag = False
    return wrapper


class RightTable(QTableWidget):
    """
    Table dynamically showing results
    """

    def __init__(self, data):
        super().__init__()

        # Custom Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.rl = Communicate()  # A signal that will be emited whenever a line is removed

        # UI
        self.verticalHeader().hide()
        self.setSortingEnabled(True)
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Strategy"), self.tr("Amount")])

        # Not editable
        # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # When edited, change the data on the database too
        self.cellChanged.connect(self.changeCellOnDatabase)

        # Data
        self.data = data
        # A flag to prevent changeCellOnDatabase execution when needed
        self.updatingdata_flag = True

        if len(self.data) > 0:
            self.data = data
            self.setRowCount(len(self.data))
            self.setColumnCount(len(self.data[0]))
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Strategy"), self.tr("Amount"), self.tr("Description")])

    @updatingdata
    def resetData(self):
        """
        Resets table, getting all results from database,
        and showing them
        """
        self.clear()
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Strategy"), self.tr("Amount"), self.tr("Description")])

        results_all = results.getResult_all()
        self.setRowCount(len(results_all))
        self.setColumnCount(len(results_all[0]))

        self.setData(newdata=results_all)

    def changeData(self, new_data):
        """ Refreshes with new data """
        self.clear()
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Strategy"), self.tr("Amount"), self.tr("Description")])

        self.data = new_data
        if new_data != []:
            self.setData(newdata=new_data)
            self.setRowCount(len(self.data))
#            self.updateGeometry()  # ?
#            self.resizeColumnsToContents()
#            self.resizeRowsToContents()
        else:
            self.setRowCount(0)

    @updatingdata
    def setData(self, newdata=None):
        if newdata is not None:
            self.data = newdata

        for nrow, row in enumerate(self.data):
            for ncol, d in enumerate(row):
                if ncol == 1:
                    # Change format to display date better
                    d = datetime.fromtimestamp(d).strftime("%d-%m-%Y")
                item = QTableWidgetItem()
                if ncol == 0:
                    # Ids can't be editable
                    item.setFlags(Qt.ItemIsSelectable)
                item.setData(0, d)
                self.setItem(nrow, ncol, item)

    def showMenu(self, event):
        menu = QMenu()
        remove_action = menu.addAction(self.tr("Remove Line"))

        action = menu.exec_(QCursor.pos())

        if action == remove_action:
            self.removeSelection()
            # Emit custom removed line signal,
            # so that we can call the accounts tab to be updated from the outside
            self.rl.lineRemoved.emit()
            self.repaint()
            """BUG CONOCIDO: POR ALGUNA RAZON AL BORRAR UNA SELECCIÓN MÚLTIPLE NO SE TERMINAN DE BORRAR TODAS LAS FILAS DE LA TABLA"""

    @updatingdata
    def removeSelection(self):
        indexes_on_table, indexes_on_db = self.getSelectionIndexes()

        print("Removing rows with ids on db : ", indexes_on_db,
              "\n & ids on table: ", indexes_on_table)

        for i, idb in zip(indexes_on_table, indexes_on_db):
            results.deleteResult(idb)
            self.removeRow(i)

    def getSelectionIndexes(self):
        indexes, indexes_on_db = [], []

        for i in self.selectedIndexes():
            i = i.row()
            if i not in indexes:
                indexes.append(i)
                indexes_on_db.append(int(self.item(i, 0).text()))

        return (indexes, indexes_on_db)

    def changeCellOnDatabase(self, row, column):
        """
        When a Table Item is edited by the user, 
        we want to check if it fits the type
        and edit it on the database too
        """

        if self.updatingdata_flag is True:
            return
            # The data is being modified internally, not by the user,
            # so no errors assumed

        new_item = self.item(row, column)
        new_item_data = self.item(row, column).text()
        database_entry_id = self.item(row, 0).text()

        previous_amount = results.getResultAmountById(
            database_entry_id)  # Useful for balance adjustments later
        columnselected_name = self.horizontalHeaderItem(column).text()
        # Depending on from which column the item is, we check the data
        # proposed differently
        if columnselected_name == self.tr("Id"):
            # Ids can't be edited
            error_mssg = QMessageBox()
            error_mssg.setIcon(QMessageBox.Warning)
            error_mssg.setText(self.tr("Ids can't be edited"))
            error_mssg.exec_()

        # -------------- Date --------------------
        elif columnselected_name == self.tr("Date"):
            print(self.tr("Date"))
            # The new text has to be a date
            try:
                new_date = datetime.strptime(new_item_data, "%d-%m-%Y")
                results.updateResult(
                    database_entry_id, newdate=new_date.timestamp())

            except ValueError:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("Has to be a date in format dd-mm-yyyy"))
                error_mssg.exec_()

                # Reset date to previous one
                previous_date_timestamp = results.getResultDateById(
                    database_entry_id)
                previous_date_text = datetime.fromtimestamp(
                    previous_date_timestamp).strftime("%d-%m-%Y")
                new_item.setData(0, previous_date_text)

        # -------------- Account --------------------
        elif columnselected_name == self.tr("Account"):
            # The account has to be an existing one
            all_accounts = [a[0] for a in balances.getAllAccounts()]
            previous_account = results.getResultAccountById(
                database_entry_id)

            if new_item_data not in all_accounts:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("The account has to be an existing one. \nAdd it first manually"))
                error_mssg.exec_()

                # Reset strategy to previous one
                new_item.setData(0, previous_account)

            else:
                # The data is good
                # Change the result on the results table on the db
                results.updateResult(
                    database_entry_id, newaccount=new_item_data)
                # Update the balance of the two accounts involved,
                # according to the result amount
                balances.updateBalances_withNewResult(
                    previous_account, - previous_amount)
                balances.updateBalances_withNewResult(
                    new_item_data, previous_amount)

        # -------------- Strategy --------------------
        elif columnselected_name == self.tr("Strategy"):
            # The strategy has to be an existing one
            previous_strategy = results.getResultStrategyById(
                database_entry_id)
            all_strategies = [s[0] for s in strategies.getAllStrategies()]

            if new_item_data not in all_strategies:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("The strategy has to be an existing one. \nAdd it first manually"))
                error_mssg.exec_()

                # Reset strategy to previous one
                new_item.setData(0, previous_strategy)
            else:
                # The data is good
                # Change the result on the results table of the db
                results.updateResult(
                    database_entry_id, newstrategy=new_item_data)
                # Update the pnl of the two strategies involved,
                # according to the result amount
                strategies.updateStrategies_withNewResult(
                    previous_strategy, - previous_amount)
                strategies.updateStrategies_withNewResult(
                    new_item_data, previous_amount)

        # -------------- Amount --------------------
        elif columnselected_name == self.tr("Amount"):
            # The amount has to be an integer
            try:
                new_item_data = int(new_item_data)
                # Change the result on the results table of the db
                results.updateResult(
                    database_entry_id, newamount=new_item_data)
                # Update the balances and strategies with the difference
                # between the old and the new result
                diff_betweeen_results = new_item_data - previous_amount
                account_involved = results.getResultAccountById(
                    database_entry_id)
                strategy_involved = results.getResultStrategyById(
                    database_entry_id)

                balances.updateBalances_withNewResult(
                    account_involved, diff_betweeen_results)
                strategies.updateStrategies_withNewResult(
                    strategy_involved, diff_betweeen_results)

            except Exception:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("Has to be an integer"))
                error_mssg.exec_()

                # Reset to previous amount
                previous_amount = results.getResultAmountById(
                    database_entry_id)
                new_item.setData(0, previous_amount)

        # -------------- Description --------------------
        # A description can be any data. So no checks
        results.updateResult(database_entry_id, newdescription=new_item_data)


class Communicate(QObject):
    """Just a custom signal"""
    lineRemoved = pyqtSignal()
