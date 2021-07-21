#!/usr/bin/python3

from datetime import datetime

from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from portfolio.db.fdbhandler import transactions, balances, costbasis


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

        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Sender Account"),
             self.tr("Amount"), self.tr("Receiver Account"), self.tr("Type"), self.tr("Description")])

        # When edited, change the data on the database too
        self.cellChanged.connect(self.changeCellOnDatabase)

        # A flag to prevent changeCellOnDatabase execution when needed
        self.updatingdata_flag = True

        # Initialization: show all transactions
        self.setData(datetime(1980, 1, 1),
                     datetime.today(), "All", "All")

    @updatingdata
    def setData(self, startdate, enddate, senderaccount, receiveraccount):
        """
        Ask the database for data within certain parameters,
        then shows that data on the table
        """
        # Clear table
        self.clear()
        self.horizontalheaders = ["id", self.tr("Date"), self.tr("Sender Account"),
                                  self.tr("Amount"), self.tr("Receiver Account"), self.tr("Type"), self.tr("Description")]
        self.setHorizontalHeaderLabels(self.horizontalheaders)

        # Get desired data from db
        transactions_to_show = transactions.get_transactions_from_query(
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

                if colnum == self.horizontalheaders.index("id"):
                    # Ids can't be editable
                    item.setFlags(Qt.ItemIsSelectable)
                elif colnum == self.horizontalheaders.index(self.tr("Date")):
                    # Format date to display date better
                    data = datetime.fromtimestamp(data).strftime("%d-%m-%Y")
                elif colnum == self.horizontalheaders.index(self.tr("Type")):
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

    @ updatingdata
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
            transactions.delete_transaction(id_db)
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

        previous_amount = transactions.get_transaction_amount_by_id(
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
                transactions.update_transaction(
                    database_entry_id, newdate=new_date.timestamp())

            except ValueError:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("Has to be a date in format dd-mm-yyyy"))
                error_mssg.exec_()

                # Reset date to previous one
                previous_date_timestamp = transactions.get_transaction_date_by_id(
                    database_entry_id)
                previous_date_text = datetime.fromtimestamp(
                    previous_date_timestamp).strftime("%d-%m-%Y")
                self.updatingdata_flag = True
                new_item.setData(0, previous_date_text)
                self.updatingdata_flag = False

        # -------------- Sender Account --------------------
        elif columnselected_name == self.tr("Sender Account"):
            # The account has to be an existing one
            all_sender_accounts = [a[0] for a in balances.get_all_accounts()]
            previous_sender_account = transactions.get_transaction_sender_account_by_id(
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
                transactions.update_transaction(
                    database_entry_id, new_sender == new_item_data)
                # Update the balance of the two accounts involved,
                # according to the transactions amount
                balances.update_balances_with_new_result(
                    previous_sender_account,  previous_amount)
                balances.update_balances_with_new_result(
                    new_item_data, - previous_amount)
                # Same with costbasis
                costbasis.update_cost_basis_with_new_transaction(
                    previous_sender_account, previous_amount)
                costbasis.update_cost_basis_with_new_transaction(
                    new_item_data, - previous_amount)

                # If the sender account is now Cash, the transaction turns into a deposit
                if new_item_data == "Cash":
                    transactions.update_transaction(
                        database_entry_id, new_d_or_w=1)
                    type_item = self.item(
                        row, self.horizontalheaders.index(self.tr("Type")))
                    type_item.setData(0, self.tr("Deposit"))

                # If the sender account was Cash, the transaction turns into a transfer
                elif previous_sender_account == "Cash":
                    transactions.update_transaction(
                        database_entry_id, new_d_or_w=0)
                    type_item = self.item(
                        row, self.horizontalheaders.index(self.tr("Type")))
                    type_item.setData(0, self.tr("Transfer"))

        # -------------- Amount --------------------
        elif columnselected_name == self.tr("Amount"):
            # The amount has to be an integer
            try:
                new_item_data = int(new_item_data)
                # Change the transaction on the transactions table on the db
                transactions.update_transaction(
                    database_entry_id, new_amount=new_item_data)
                # Update the balances and strategies with the difference
                # between the old and the new transaction
                diff_betweeen_transactions = new_item_data - previous_amount
                senderaccount_involved = transactions.get_transaction_sender_account_by_id(
                    database_entry_id)
                receiveraccount_involved = transactions.get_transaction_receiver_account_by_id(
                    database_entry_id)

                # Update the balance of the accounts involved,
                # according to the new amount
                balances.update_balances_with_new_result(
                    senderaccount_involved, - diff_betweeen_transactions)
                balances.update_balances_with_new_result(
                    receiveraccount_involved, diff_betweeen_transactions)
                # Same with costbasis
                costbasis.update_cost_basis_with_new_transaction(
                    senderaccount_involved, - diff_betweeen_transactions)
                costbasis.update_cost_basis_with_new_transaction(
                    receiveraccount_involved, diff_betweeen_transactions)

            except Exception:
                error_mssg = QMessageBox()
                error_mssg.setIcon(QMessageBox.Warning)
                error_mssg.setText(
                    self.tr("Has to be an integer"))
                error_mssg.exec_()

                # Reset to previous amount
                previous_amount = transactions.get_transaction_amount_by_id(
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
                transactions.update_transaction(
                    database_entry_id, new_receiver=new_item_data)
                # Update the balance of the two accounts involved,
                # according to the transactions amount
                balances.update_balances_with_new_result(
                    previous_receiver_account,  - previous_amount)
                balances.update_balances_with_new_result(
                    new_item_data, previous_amount)
                # Same with costbasis
                costbasis.update_cost_basis_with_new_transaction(
                    previous_receiver_account, - previous_amount)
                costbasis.update_cost_basis_with_new_transaction(
                    new_item_data, previous_amount)

                # If the receiver account is now Cash, the transaction turns into a withdrawal
                if new_item_data == "Cash":
                    transactions.update_transaction(
                        database_entry_id, new_d_or_w=-1)
                    type_item = self.item(
                        row, self.horizontalheaders.index(self.tr("Type")))
                    type_item.setData(0, self.tr("Withdrawal"))

                # If the receiver account was Cash, the transaction turns into a transfer
                elif previous_receiver_account == "Cash":
                    transactions.update_transaction(
                        database_entry_id, new_d_or_w=0)
                    type_item = self.item(
                        row, self.horizontalheaders.index(self.tr("Type")))
                    type_item.setData(0, self.tr("Transfer"))

        # -------------- Description --------------------
        elif columnselected_name == self.tr("Description"):
            # A description can be any data. So no checks
            transactions.update_transaction(
                database_entry_id, newdescription=new_item_data)


class LineRemovedSignal(QObject):
    lineremoved = pyqtSignal()
