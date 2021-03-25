#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from gui.dbhandler import transactions, balances, costbasis


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
    Table dinamycally showing transactions from the database
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Custom Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.lineremoved = LineRemovedSignal()  # Custom Signal

        # UI Tweaks
        self.verticalHeader().hide()
        self.setSortingEnabled(True)

        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Sender Account"),
             self.tr("Amount"), self.tr("Receiver Account"), self.tr("Type")])

        # When edited, change the data on the database too
        self.cellChanged.connect(self.changeCellOnDatabase)

        # A flag to prevent changeCellOnDatabase execution when needed
        self.updatingdata_flag = True

        # Initialization: show all transactions
        self.setData(datetime(1900, 1, 1),
                     datetime.today(), "All", "All")

    @updatingdata
    def setData(self, startdate, enddate, senderaccount, receiveraccount):
        """
        Ask the database for data within certain parameters,
        then shows that data on the table
        """
        # Clear table
        self.clear()
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Sender Account"),
             self.tr("Amount"), self.tr("Receiver Account"), self.tr("Type")])

        # Get desired data from db
        transactions_to_show = transactions.getTransactions_fromQuery(
            start_date=startdate, end_date=enddate, senderaccount=senderaccount, receiveraccount=receiveraccount)

        # If the data is empty, we are done
        if len(transactions_to_show) == 0:
            self.setRowCount(0)
            return

        # Resize table
        self.setRowCount(len(transactions_to_show))
        self.setColumnCount(len(transactions_to_show[0]))

        # Change content
        for rownum, row in enumerate(transactions_to_show):
            for colnum, data in enumerate(row):
                item = QTableWidgetItem()  # Item that will be inserted

                if colnum == 0:
                    # Ids can't be editable
                    item.setFlags(Qt.ItemIsSelectable)
                elif colnum == 1:
                    # Format date to display date better
                    data = datetime.fromtimestamp(data).strftime("%d-%m-%Y")
                elif colnum == 5:
                    # Format Deposit/Withdrawal
                    if data == 1:
                        data = self.tr("Deposit")
                    elif data == -1:
                        data = self.tr("Withdrawal")
                    elif data == 0:
                        data = self.tr("Transfer")

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
            self.lineremoved.lineremoved.emit()

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
            transactions.deleteTransaction(id_db)
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
            # so no errors is assumed

        # Getting edited item data
        new_item = self.item(row, column)
        new_item_data = new_item.text()
        database_entry_id = self.item(row, 0).text()

        previous_amount = transactions.getTransactionAmountById(
            database_entry_id)  # Useful for balance and costbasis adjustments later
        columnselected_name = self.horizontalHeaderItem(column).text()
        # Depending on from which column the item is, we check the data
        # proposed differently

        # Check which part of the transaction has been edited, and accting accordingly
        # -------------- id --------------------
        if columnselected_name == self.tr("id"):
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
                transactions.updateTransaction(
                    database_entry_id, newdate=new_date.timestamp())

            except ValueError:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("Has to be a date in format dd-mm-yyyy"))
                error_mssg.exec_()

                # Reset date to previous one
                previous_date_timestamp = transactions.getTransactionDateById(
                    database_entry_id)
                previous_date_text = datetime.fromtimestamp(
                    previous_date_timestamp).strftime("%d-%m-%Y")
                self.updatingdata_flag = True
                new_item.setData(0, previous_date_text)
                self.updatingdata_flag = False

        # -------------- Sender Account --------------------
        elif columnselected_name == self.tr("Sender Account"):
            # The account has to be an existing one
            all_sender_accounts = [a[0] for a in balances.getAllAccounts()]
            previous_sender_account = transactions.getTransactionSenderAccountById(
                database_entry_id)

            if new_item_data not in all_sender_accounts:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("The account has to be an existing one. \nAdd it first manually"))
                error_mssg.exec_()

                # Reset strategy to previous one
                self.updatingdata_flag = True
                new_item.setData(0, previous_sender_account)
                self.updatingdata_flag = False

            else:
                # The data is good
                # Change the transaction on the transactions table on the db
                transactions.updateTransaction(
                    database_entry_id, newsenderaccount=new_item_data)
                # Update the balance of the two accounts involved,
                # according to the transactions amount
                balances.updateBalances_withNewResult(
                    previous_sender_account,  previous_amount)
                balances.updateBalances_withNewResult(
                    new_item_data, - previous_amount)
                # Same with costbasis
                costbasis.updateCostBasis_withNewTransaction(
                    previous_sender_account, previous_amount)
                costbasis.updateCostBasis_withNewTransaction(
                    new_item_data, - previous_amount)

        # -------------- Amount --------------------
        elif columnselected_name == self.tr("Amount"):
            # The amount has to be an integer
            try:
                new_item_data = int(new_item_data)
                # Change the transaction on the transactions table on the db
                transactions.updateTransaction(
                    database_entry_id, newamount=new_item_data)
                # Update the balances and strategies with the difference
                # between the old and the new transaction
                diff_betweeen_transactions = new_item_data - previous_amount
                senderaccount_involved = transactions.getTransactionSenderAccountById(
                    database_entry_id)
                receiveraccount_involved = transactions.getTransactionReceiverAccountById(
                    database_entry_id)

                # Update the balance of the accounts involved,
                # according to the new amount
                balances.updateBalances_withNewResult(
                    senderaccount_involved, - diff_betweeen_transactions)
                balances.updateBalances_withNewResult(
                    receiveraccount_involved, diff_betweeen_transactions)
                # Same with costbasis
                costbasis.updateCostBasis_withNewTransaction(
                    senderaccount_involved, - diff_betweeen_transactions)
                costbasis.updateCostBasis_withNewTransaction(
                    receiveraccount_involved, diff_betweeen_transactions)

            except Exception:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("Has to be an integer"))
                error_mssg.exec_()

                # Reset to previous amount
                previous_amount = transactions.getTransactionAmountById(
                    database_entry_id)
                self.updatingdata_flag = True
                new_item.setData(0, previous_amount)
                self.updatingdata_flag = False

        # -------------- Receiver Account --------------------
        elif columnselected_name == self.tr("Receiver Account"):
            # The account has to be an existing one
            all_receiver_accounts = [a[0] for a in balances.getAllAccounts()]
            previous_receiver_account = transactions.getTransactionReceiverAccountById(
                database_entry_id)

            if new_item_data not in all_receiver_accounts:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("The account has to be an existing one. \nAdd it first manually"))
                error_mssg.exec_()

                # Reset strategy to previous one
                self.updatingdata_flag = True
                new_item.setData(0, previous_receiver_account)
                self.updatingdata_flag = False

            else:
                # The data is good
                # Change the transaction on the transactions table on the db
                transactions.updateTransaction(
                    database_entry_id, newreceiveraccount=new_item_data)
                # Update the balance of the two accounts involved,
                # according to the transactions amount
                balances.updateBalances_withNewResult(
                    previous_receiver_account,  - previous_amount)
                balances.updateBalances_withNewResult(
                    new_item_data, previous_amount)
                # Same with costbasis
                costbasis.updateCostBasis_withNewTransaction(
                    previous_receiver_account, - previous_amount)
                costbasis.updateCostBasis_withNewTransaction(
                    new_item_data, previous_amount)


class LineRemovedSignal(QObject):
    lineremoved = pyqtSignal()
