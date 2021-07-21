# /usr/bin/python3
"""
Main layout of TabAccount.
Here all accounts are displayed, with their respective info.
"""

import os
import shutil

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtWidgets import QGridLayout, QLabel, QMenu, QDialog, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

from portfolio.gui.ui_components.fonts import AccountBalanceTextFont, AccountBalanceHeaderFont
from portfolio.db.fdbhandler import balances, costbasis


class AccountsLayout(QScrollArea):
    """
    This ScrollArea has one Widget with one Layout that stores
    rows with each account info
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- Content ----
        self.widget = QWidget()
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setColumnMinimumWidth(1, 350)
        self.layout.setColumnMinimumWidth(2, 350)

        # Headers
        # Name
        name_header = HeaderLabel(self.tr("Name"))
        self.layout.addWidget(name_header, 0, 1)
        # Balance
        balance_header = HeaderLabel(self.tr("Balance (EUR)"))
        self.layout.addWidget(balance_header, 0, 2)
        # Cost Basis
        costbasis_header = HeaderLabel(self.tr("Cost Basis"))
        self.layout.addWidget(costbasis_header, 0, 3)

        # Account Rows
        accounts = balances.get_all_account_names()
        for row_number, accname in enumerate(accounts):
            # First row is aleady taken (headers)
            self.addAccountRow(accname, row_number+1)

        # ---- UI ----
        self.layout.setVerticalSpacing(40)

        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

    def addAccountRow(self, acc_name, row_number):
        MAXHEIGHT = 90

        # Account Name
        accname = QLabel(acc_name)
        accname.setAlignment(Qt.AlignCenter)
        accname.setFont(AccountBalanceTextFont())
        accname.setObjectName("accname")
        accname.setMaximumHeight(MAXHEIGHT)

        # Account Balance
        accbalance = QLabel()
        accbalance.setAlignment(Qt.AlignCenter)
        accbalance.setObjectName(str(accname))
        # So that we can find this balance label later by the account name
        # Getting the balance of the account from the db
        balance = balances.get_account_balance(acc_name)
        accbalance.setText(str(balance) + " EUR")
        accbalance.setFont(AccountBalanceTextFont())

        # Cost Basis
        acccostbasis = QLabel()
        acccostbasis.setAlignment(Qt.AlignCenter)
        acccostbasis.setText(str(costbasis.get_cost_basis(acc_name)))
        acccostbasis.setFont(AccountBalanceTextFont())

        self.layout.addWidget(accname, row_number, 1)
        self.layout.addWidget(accbalance, row_number, 2)
        self.layout.addWidget(acccostbasis, row_number, 3)


class HeaderLabel(QLabel):
    """A header indicating what a column is about"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(AccountBalanceHeaderFont())
        self.setMaximumHeight(15)
        self.setAlignment(Qt.AlignCenter)


class AccountIcon(QLabel):
    """Displays an account's current associated icon"""

    def __init__(self, account_icon_path, row_maxheight, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        change_icon_action = menu.addAction(self.tr("Change Icon"))

        action = menu.exec_(QCursor.pos())
        if action == change_icon_action:
            self.showChangeIconDialog(self.row_maxheight)

    def showChangeIconDialog(self, row_maxheight):
        dialog = ChangeIconDialog(
            row_maxheight, self.account_icon_path, self)
        dialog.changed.iconchanged.connect(
            self.refreshIcon)  # Custom Signal

        dialog.show()


class ChangeIconDialog(QDialog):
    iconchanged = pyqtSignal()

    def __init__(self, row_maxheight, account_icon_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Data
        self.row_maxheight = row_maxheight
        self.account_icon_path = account_icon_path
        self.errorlabel, self.imgpath = None, None
        self.changed = Communicate()

        # UI
        self.setWindowTitle(self.tr("Change Account  Icon"))
        self.setFixedSize(250, 180)
        self.setAcceptDrops(True)

        self.dialog_layout = QVBoxLayout()
        self.dialog_label = QLabel(self.tr("Drag new icon here"))
        self.dialog_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.dialog_label.setStyleSheet(
            "border: 2px grey; border-style: dashed; font-style: italic")
        self.dialog_label.setAlignment(Qt.AlignCenter)

        # Button to write icon changes
        self.change_pushbutton = QPushButton(self.tr("Change"))
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
        """File has been droped. We'll try to change the icon"""
        url = (event.mimeData().urls())[0].path()
        self.changeLabelToIcon(url)

    def changeIcon(self):
        if self.imgpath is not None:
            os.remove(self.account_icon_path)
            shutil.copyfile(self.imgpath, self.account_icon_path)
            self.change_pushbutton.setText(self.tr("Changed!"))
            # Emits signal to outside so that icon can be refreshed
            self.iconchanged.emit()
            self.close()

        else:
            if self.errorlabel is not None:
                self.errorlabel.setParent(None)
            self.errorlabel = QLabel(self.tr("No image selected"))
            self.errorlabel.setAlignment(Qt.AlignCenter)
            self.dialog_layout.addWidget(self.errorlabel)

    def mousePressEvent(self, event):
        """Display a dialog to select the new icon"""
        filedialog = QFileDialog(self)
        filedialog.show()
        filedialog.fileSelected.connect(
            self.changeLabelToIcon)

    def changeLabelToIcon(self, url):
        """
        Changes the dialog layout to the image that has been selected.
        If it is not an image, it changes the dialog layout to an error message.
        """

        if url.split('.')[-1] in ['png', 'jpg', 'svg', 'jpeg']:
            # If the file is an image, we display it
            with open(url):
                pixmap = QPixmap(url).scaledToHeight(self.row_maxheight)
                self.imgpath = url
                self.dialog_label.setPixmap(pixmap)

                if self.errorlabel is not None:
                    self.errorlabel.setParent(None)
                self.errorlabel = None
        else:
            self.errorlabel = QLabel(self.tr("Has to be an image"))
            self.errorlabel.setAlignment(Qt.AlignCenter)
            self.dialog_layout.addWidget(self.errorlabel)
