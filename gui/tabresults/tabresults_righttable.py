#!/usr/bin/python3

from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QAbstractItemView, QMenu, QHeaderView
from PyQt5.QtGui import QMouseEvent, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from datetime import datetime

from dbhandler import results


class RightTable(QTableWidget):

    def __init__(self, data):
        super().__init__()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)
        self.rl = Communicate()  # A signal that will be emited whenever a line is removed

        self.verticalHeader().hide()
        self.setSortingEnabled(True)
        self.setHorizontalHeaderLabels(
            ["id", self.tr("Date"), self.tr("Account"), self.tr("Amount")])
        """
        XK NO FUNCIONA?
        """
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Not editable

        self.data = data

        if len(self.data) > 0:
            self.data = data
            self.setRowCount(len(self.data))
            self.setColumnCount(len(self.data[0]))
        self.setHorizontalHeaderLabels(['id', 'Date', 'Account', 'Amount'])

    def resetData(self):
        self.clear()
        results_all = results.getResult_all()

        self.setRowCount(len(results_all))
        self.setColumnCount(len(results_all[0]))

        self.setData(newdata=results_all)

    def changeData(self, new_data):
        """ Refreshes with new data """
        self.clearData()
        self.data = new_data

        if new_data != []:
            self.setData(newdata=new_data)

            self.setRowCount(len(self.data))

#            self.updateGeometry()  # ?
#            self.resizeColumnsToContents()
#            self.resizeRowsToContents()

        else:
            self.setRowCount(0)

    def setData(self, newdata=None):
        if newdata != None:
            self.data = newdata

        for nrow, row in enumerate(self.data):
            for ncol, d in enumerate(row):
                if ncol == 1:
                    # Change format to display date better
                    d = datetime.fromtimestamp(d).strftime("%d-%m-%Y")
                # Since we skipped the first item, ncol has to be one less
                item = QTableWidgetItem()
                item.setData(0, d)
                self.setItem(nrow, ncol, item)

    def clearData(self):
        self.clear()

    def showMenu(self, event):
        menu = QMenu()
        remove_action = menu.addAction(self.tr("Remove Line"))

        action = menu.exec_(QCursor.pos())

        if action == remove_action:
            self.removeSelection()
            # Emit custom removed line signal, so that we can call the accounts tab to be updated from the outside
            self.rl.lineRemoved.emit()
            self.repaint()
            """BUG CONOCIDO: POR ALGUNA RAZON AL BORRAR UNA SELECCIÓN MÚLTIPLE NO SE TERMINAN DE BORRAR TODAS LAS FILAS DE LA TABLA"""

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


class Communicate(QObject):
    """Just a custom signal"""
    lineRemoved = pyqtSignal()
