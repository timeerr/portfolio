# /usr/bin/python3

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QMenu, QDialog, QFrame, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QCursor, QFont
from PyQt5.QtCore import Qt, QMargins, pyqtSignal, QSize, QObject

import os
import shutil
import time

from fonts import AccountBalanceTextFont, AccountBalanceHeaderFont
from dbhandler import balances, costbasis
from tabaccounts.account import Account


class AccountsLayout(QScrollArea):

    def __init__(self, accounts):
        super().__init__()

        # This ScrollArea has one Widget with one Layout that stores rows with each account info
        self.widget = QWidget()
        self.layout = QGridLayout()
        self.layout.setColumnMinimumWidth(1, 350)
        self.layout.setColumnMinimumWidth(2, 350)

        # Headers
        self.setHeaders()

        # Account Rows
        self.rowwidgets = {}  # Here we'll store all balance objects to edit them if needed
        for row_number, account in enumerate(accounts):
            # First row is aleady taken (headers)
            self.addAccountRow(account, row_number+1)

        # UI Tweaks
        self.layout.setVerticalSpacing(40)

        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

    def setHeaders(self):
        # "Name" Header
        name_header = HeaderLabel("Name")

        # "Balance" Header
        balance_header = HeaderLabel("Balance (EUR)")

        # "Cost Basis" Header
        costbasis_header = HeaderLabel("Cost Basis")

        self.layout.addWidget(name_header, 0, 1)
        self.layout.addWidget(balance_header, 0, 2)
        self.layout.addWidget(costbasis_header, 0, 3)

    def addAccountRow(self, account: Account, row_number):
        row_maxheight = 90

        # Account Icon
        icon = AccountIcon(account.iconpath, row_maxheight)
        icon.setObjectName("icon")

        # Account Name
        accname = QLabel(account.account_name)
        accname.setAlignment(Qt.AlignCenter)
        accname.setFont(AccountBalanceTextFont())
        accname.setObjectName("accname")
        accname.setMaximumHeight(row_maxheight)

        # Account Balance
        accbalance = QLabel()
        accbalance.setAlignment(Qt.AlignCenter)
        accbalance.setObjectName(str(account.account_name))
        # So that we can find this balance label later by the account name
        # Getting the balance of the account from the db
        balance = balances.getAccount(account.account_name)[1]
        accbalance.setText(str(balance) + " EUR")
        accbalance.setFont(AccountBalanceTextFont())

        # Cost Basis
        acccostbasis = QLabel()
        acccostbasis.setAlignment(Qt.AlignCenter)
        acccostbasis.setText(str(costbasis.getCostBasis(account.account_name)))
        acccostbasis.setFont(AccountBalanceTextFont())

        self.layout.addWidget(icon, row_number, 0)
        self.layout.addWidget(accname, row_number, 1)
        self.layout.addWidget(accbalance, row_number, 2)
        self.layout.addWidget(acccostbasis, row_number, 3)

        # Storing the widget inside a well structured dictionary will enable editing later
        if account.account_name not in self.rowwidgets.keys():
            self.rowwidgets[account.account_name] = {}

        self.rowwidgets[account.account_name]['name'] = accname
        self.rowwidgets[account.account_name]['balance'] = accbalance
        self.rowwidgets[account.account_name]['costbasis'] = acccostbasis
        self.rowwidgets[account.account_name]['icon'] = icon

    def refreshIcon(self, account_name):
        self.rowwidgets[account_name]['icon'].refreshIcon()

    def forceRefresh(self):
        rng = [i+1 for i in range(self.layout.rowCount())]
        del rng[-1]
        for i in rng:
            self.layout.itemAtPosition(i, 0).widget().refreshIcon()


class HeaderLabel(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # "Name" Header
        self.setFont(AccountBalanceHeaderFont())
        # self.setStyleSheet("border: none ; color: rgb(128,02,168);")
        self.setMaximumHeight(15)
        self.setAlignment(Qt.AlignCenter)


class AccountIcon(QLabel):
    def __init__(self, account_icon_path, row_maxheight, *args, **kwargs):
        super().__init__()

        # UI
        self.setObjectName("icon")
        pixmap = QPixmap(account_icon_path).scaledToHeight(row_maxheight)
        self.setPixmap(pixmap)
        self.setMaximumHeight(row_maxheight)
        self.setAlignment(Qt.AlignCenter)

        # Data
        self.row_maxheight = row_maxheight
        self.account_icon_path = account_icon_path

        # Functionality
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

    def refreshIcon(self):
        pixmap = QPixmap(self.account_icon_path).scaledToHeight(
            self.row_maxheight)
        self.setPixmap(pixmap)

    def showMenu(self, event):
        menu = QMenu()
        change_icon_action = menu.addAction("Change Icon")

        action = menu.exec_(QCursor.pos())

        if action == change_icon_action:
            self.showChangeIconDialog(self.row_maxheight)

    def showChangeIconDialog(self, row_maxheight):
        self.dialog = ChangeIconDialog(row_maxheight, self.account_icon_path)
        self.dialog.changed.iconchanged.connect(
            self.refreshIcon)  # Custom Signal

        self.dialog.show()


class ChangeIconDialog(QDialog):

    def __init__(self, row_maxheight, account_icon_path):
        super().__init__()

        # Data
        self.row_maxheight = row_maxheight
        self.account_icon_path = account_icon_path
        self.errorlabel, self.imgpath = None, None
        self.changed = Communicate()

        # UI
        self.setWindowTitle("Change Account  Icon")
        self.setFixedSize(250, 180)
        self.setAcceptDrops(True)

        self.dialog_layout = QVBoxLayout()
        self.dialog_label = QLabel("Drag new icon here")
        self.dialog_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.dialog_label.setStyleSheet(
            "border: 2px grey; border-style: dashed; font-style: italic")
        self.dialog_label.setAlignment(Qt.AlignCenter)

        # Button to write icon changes
        self.change_pushbutton = QPushButton("Change")
        self.change_pushbutton.clicked.connect(self.changeIcon)

        self.dialog_layout.addWidget(self.dialog_label)
        self.dialog_layout.addWidget(self.change_pushbutton)
        self.setLayout(self.dialog_layout)

    def dragEnterEvent(self, event):
        # Only accept if dragged file is a local file
        if event.mimeData().hasUrls():
            if len(event.mimeData().urls()) == 1:
                event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = (event.mimeData().urls())[0].path()

        self.changeLabelToIcon(url)

    def changeIcon(self):
        if self.imgpath != None:
            os.remove(self.account_icon_path)
            shutil.copyfile(self.imgpath, self.account_icon_path)
            self.change_pushbutton.setText("Changed!")
            # Emits signal to outside so that icon can be refreshed
            self.changed.iconchanged.emit()
            self.close()

        else:
            if self.errorlabel != None:
                self.errorlabel.setParent(None)
            self.errorlabel = QLabel("No image selected")
            self.errorlabel.setAlignment(Qt.AlignCenter)
            self.dialog_layout.addWidget(self.errorlabel)

    def mousePressEvent(self, event):
        self.filedialog = QFileDialog()
        self.filedialog.show()
        self.filedialog.fileSelected.connect(
            lambda url: self.changeLabelToIcon(url))

    def changeLabelToIcon(self, url):

        if url.split('.')[-1] in ['png', 'jpg', 'svg', 'jpeg']:
            # If the file is an image, we display it
            with open(url):
                pixmap = QPixmap(url).scaledToHeight(self.row_maxheight)
                self.imgpath = url
                self.dialog_label.setPixmap(pixmap)

                if self.errorlabel != None:
                    self.errorlabel.setParent(None)
                self.errorlabel = None
        else:
            self.errorlabel = QLabel("Has to be an image")
            self.errorlabel.setAlignment(Qt.AlignCenter)
            self.dialog_layout.addWidget(self.errorlabel)


class Communicate(QObject):
    """Custom Signal"""
    iconchanged = pyqtSignal()
