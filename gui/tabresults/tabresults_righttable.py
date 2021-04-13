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

    def __init__(self):
        super().__init__()

        # Custom Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        # A signal that will be emited whenever a line is removed
        self.lineremoved = LineRemoved()

        # UI Tweaks
        self.verticalHeader().hide()
        self.setSortingEnabled(True)

        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Strategy"), self.tr("Amount")])

        # When edited, change the data on the database too
        self.cellChanged.connect(self.changeCellOnDatabase)

        # A flag to prevent changeCellOnDatabase execution when needed
        self.updatingdata_flag = True

        # Initialization: show all transactions
        self.setData(datetime(1980, 1, 1), datetime.today(), "All", "All")

    @updatingdata
    def setData(self, startdate, enddate, strategy, account):
        """
        Asks the database for results data within certain parameters,
        then shows that data on the table
        """
        # Clear table
        self.clear()
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Strategy"), self.tr("Amount"), self.tr("Description")])

        # Get desired data from db
        results_to_show = results.getResults_fromQuery(
            start_date=startdate, end_date=enddate, strategy=strategy, account=account)

        # If the data is empty, we are done
        if len(results_to_show) == 0:
            self.setRowCount(0)
            return

        # Resize table
        self.setRowCount(len(results_to_show))
        self.setColumnCount(len(results_to_show[0]))

        # Change content
        for rownum, row in enumerate(results_to_show):
            for colnum, data in enumerate(row):
                item = QTableWidgetItem()  # Item that will be inserted

                if colnum == 0:
                    # Ids can't be editable
                    item.setFlags(Qt.ItemIsSelectable)
                elif colnum == 1:
                    # Change format to display date better
                    data = datetime.fromtimestamp(data).strftime("%d-%m-%Y")

                # Data is now formatted, we can write it on table
                item.setData(0, data)
                self.setItem(rownum, colnum, item)

    def showMenu(self, event):
        """
        Custom Menu to show when an item is right-clicked

        Options:
        - Remove Line: removes line from table and database
        """
        menu = QMenu()

        # Actions
        remove_action = menu.addAction(self.tr("Remove Line"))

        # Getting action selected by user
        action = menu.exec_(QCursor.pos())

        # Act accordingly
        if action == remove_action:
            self.removeSelection()
            self.lineremoved.lineRemoved.emit()

    @updatingdata
    def removeSelection(self):
        """
        Removes the entire row of every selected item,
        and then does the same on the databse
        """

        # Getting selected indexes, and their corresponding ids
        # from the database
        selected_indexes_table, selected_ids = [], []
        for index in self.selectedIndexes():
            index = index.row()  # Row number
            if index not in selected_indexes_table:  # Avoid duplicates
                selected_indexes_table.append(index)
                selected_ids.append(int(self.item(index, 0).text()))

        # Removing the rows from the table and the database
        for index, id_db in zip(selected_indexes_table, selected_ids):
            results.deleteResult(id_db)
            self.removeRow(index)

        print("Removed rows with ids on db : ", selected_ids,
              "\n & ids on table: ", selected_indexes_table)

    def changeCellOnDatabase(self, row, column):
        """
        When a Table Item is edited by the user, 
        we want to check if it fits the type
        and edit it on the database too
        """

        if self.updatingdata_flag is True:
            return
            # The data is being modified internally (not by the user)
            # so no errors assumed

        new_item = self.item(row, column)
        new_item_data = new_item.text()
        database_entry_id = self.item(row, 0).text()

        previous_amount = results.getResultAmountById(
            database_entry_id)  # Useful for balance adjustments later
        columnselected_name = self.horizontalHeaderItem(column).text()
        # Depending on from which column the item is, we check the data
        # proposed differently

        # Check which part of the transaction has been edited, and accting accordingly
        # -------------- id --------------------
        if columnselected_name == self.tr("Id"):
            # Ids can't be edited
            error_mssg = QMessageBox()
            error_mssg.setIcon(QMessageBox.Warning)
            error_mssg.setText(self.tr("Ids can't be edited"))
            error_mssg.exec_()

        # -------------- Date --------------------
        elif columnselected_name == self.tr("Date"):
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
                self.updatingdata_flag = True
                new_item.setData(0, previous_date_text)
                self.updatingdata_flag = False

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
                self.updatingdata_flag = True
                new_item.setData(0, previous_account)
                self.updatingdata_flag = False

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
                self.updatingdata_flag = True
                new_item.setData(0, previous_strategy)
                self.updatingdata_flag = False
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
                self.updatingdata_flag = True
                new_item.setData(0, previous_amount)
                self.updatingdata_flag = False

        # -------------- Description --------------------
        elif columnselected_name == self.tr("Description"):
            # A description can be any data. So no checks
            results.updateResult(
                database_entry_id, newdescription=new_item_data)


class LineRemoved(QObject):
    lineRemoved = pyqtSignal()
