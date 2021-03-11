#!/usr/bin/python3

from PyQt5.QtWidgets import QPushButton, QDialog, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QFormLayout, QDoubleSpinBox, QComboBox, QFrame
from PyQt5.QtCore import pyqtSignal, QObject, QMargins, Qt
from PyQt5.QtGui import QFont

from cdbhandler import cbalances
from prices import prices


class TabCryptoToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add account action
        self.addaccount_action = QAction("Add Account", self)
        self.addaccount_action.setStatusTip("Add cryptocurrency account")
        self.addaccount_action.triggered.connect(self.addAccountActionClick)
        self.addAction(self.addaccount_action)

        self.addaccount_dialog = AddAccountDialog()

        # Update all accounts action
        self.update_all_accounts_action = QAction("Update All Accounts")
        self.update_all_accounts_action.setStatusTip(
            "Update all current cryptocurrency accounts with new balances")
        self.update_all_accounts_action.triggered.connect(
            self.updateAccountsActionClick)
        self.addAction(self.update_all_accounts_action)

        self.update_all_accounts_dialog = UpdateAllAccountsDialog()

    def addAccountActionClick(self):
        self.addaccount_dialog.setVisible(True)

    def updateAccountsActionClick(self):
        self.update_all_accounts_dialog.setVisible(True)


class AddAccountDialog(QDialog):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

        self.setWindowTitle("Add Cryptocurrency Account")
        self.layout = QVBoxLayout()
        self.formlayout = QFormLayout()

        # Account Name
        self.name = QLabel("Account Name")
        self.name_edit = QLineEdit()
        self.formlayout.setWidget(0, self.formlayout.LabelRole, self.name)
        self.formlayout.setWidget(0, self.formlayout.FieldRole, self.name_edit)

        # Token
        self.token = QLabel("Token")
        self.token_edit = QLineEdit()
        self.formlayout.setWidget(1, self.formlayout.LabelRole, self.token)
        self.formlayout.setWidget(
            1, self.formlayout.FieldRole, self.token_edit)

        # Starting balance
        self.startingbalance = QLabel("Starting Balance")
        self.startingbalance_edit = QDoubleSpinBox()
        self.startingbalance_edit.setSuffix(self.token_edit.text())
        self.startingbalance_edit.setDecimals(8)
        self.startingbalance_edit.setSingleStep(0.00000001)
        self.startingbalance_edit.setMinimum(0)
        self.startingbalance_edit.setMaximum(99999999999)
        self.formlayout.setWidget(
            2, self.formlayout.LabelRole, self.startingbalance)
        self.formlayout.setWidget(
            2, self.formlayout.FieldRole, self.startingbalance_edit)

        # Type
        self.type = QLabel("Type")
        self.type_edit = QComboBox(self)
        self.type_edit.addItems(["Cold", "Hot", "Custodial"])
        self.formlayout.setWidget(3, self.formlayout.LabelRole, self.type)
        self.formlayout.setWidget(3, self.formlayout.FieldRole, self.type_edit)

        # KYC
        self.kyc = QLabel("KYC")
        self.kyc_edit = QComboBox()
        self.kyc_edit.addItems(["Yes", "No"])
        self.formlayout.setWidget(4, self.formlayout.LabelRole, self.kyc)
        self.formlayout.setWidget(4, self.formlayout.FieldRole, self.kyc_edit)

        # Description
        self.descr = QLabel("Description")
        self.descr_edit = QLineEdit()
        self.formlayout.setWidget(5, self.formlayout.LabelRole, self.descr)
        self.formlayout.setWidget(
            5, self.formlayout.FieldRole, self.descr_edit)

        # Functionality
        self.add_acc_bttn = QPushButton("Add Account")
        self.add_acc_bttn.clicked.connect(self.createAccount)

        self.layout.addLayout(self.formlayout)
        self.layout.addWidget(self.add_acc_bttn)
        self.setLayout(self.layout)

        # Custom Signals
        self.updatecryptosignal = UpdateTabCryptoSignal()

    def createAccount(self):
        """Creates account with form info, and adds it to database"""
        # First, we need to check if the account's token is new. In that case, we need to ask the user on how to get info avout the token itself
        token = self.token_edit.text().upper()
        if prices.tokenInPrices(token.lower()) == False:
            # We display a dialog
            self.new_token_dialog = NewTokenDialog(token)
            self.new_token_dialog.exec_()

        account = self.name_edit.text()
        amount = self.startingbalance_edit.value()
        _type = self.type_edit.currentText()
        kyc = self.kyc_edit.currentText()
        description = self.descr_edit.text()
        cbalances.addAccount(account, token, amount, _type, kyc, description)

        self.updatecryptosignal.updated.emit()
        self.close()


class NewTokenDialog(QDialog):
    def __init__(self, tokenname, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Data
        self.tokenname = tokenname
        # UI
        self.layout = QVBoxLayout()

        # New Token Description
        self.description = QLabel(
            self.tokenname + " has to be added \nSelect Method to obtain new its price data")
        self.layout.addWidget(self.description)

        # Method to obtain new token price data
        self.method = QComboBox()
        self.method.addItems(["Coingecko", "Custom Price"])
        self.method.currentTextChanged.connect(self.handleMethodChanged)
        self.layout.addWidget(self.method)

        self.currentprice = QLineEdit("")
        self.layout.addWidget(self.currentprice)
        self.currentprice.hide()

        # Save token
        self.save_token_bttn = QPushButton("Add Token")
        self.save_token_bttn.clicked.connect(self.addTokenPrice)
        self.layout.addWidget(self.save_token_bttn)

        self.setLayout(self.layout)

        # Initialization with Coingecko price
        self.handleMethodChanged('Coingecko')

    def addTokenPrice(self):
        # Writes new token info on prices folder
        token = self.tokenname

        method = self.method.currentText()
        if method == 'Coingecko':
            method = 'coingecko'
        elif method == 'Custom Price':
            method = 'custom'

        price = float(self.currentprice.text().split(" ")[0])

        prices.addTokenPrice(token, method, price)

        self.close()

    def handleMethodChanged(self, method):
        """ Depending on the method, we display different things """

        if method == 'Coingecko':
            # We add a simple label displaying the current price, to see if it's okay
            self.currentprice.setReadOnly(True)
            self.currentprice.setText("Getting coingecko's price")
            try:
                price = prices.toBTCAPI(self.tokenname, 1)
            except:
                price = "Couldn't get price in "
            self.currentprice.setText(str(price) + " BTC")

        elif method == 'Custom Price':
            # We add a field to put the current price
            self.currentprice.setText("")
            self.currentprice.setReadOnly(False)

        self.currentprice.show()


class UpdateAllAccountsDialog(QDialog):
    """ Dialog to see each crypto account and edit it as wished """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Update All Accounts")
        self.layout = QVBoxLayout()

        # All account names:
        self.accentries = [(i[0], i[1]) for i in cbalances.getAllEntries()]
        self.current_accentry = 0

        # Account
        self.account_lyt = QHBoxLayout()
        self.account_descr = QLabel("Account")
        self.account_descr.setFixedWidth(110)
        self.account_descr.setAlignment(Qt.AlignRight)
        self.account = QLabel()
        self.account.setMaximumWidth(140)
        font = QFont()
        font.setItalic(True)
        self.account.setFont(font)
        self.account.setText(self.accentries[0][0])
        self.account_lyt.addWidget(self.account_descr)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.account_lyt.addWidget(line)
        self.account_lyt.addWidget(self.account)
        self.layout.addLayout(self.account_lyt)

        # Token
        self.token_lyt = QHBoxLayout()
        self.token_descr = QLabel("Token")
        self.token_descr.setFixedWidth(110)
        self.token_descr.setAlignment(Qt.AlignRight)
        self.token = QLabel()
        self.token.setMaximumWidth(140)
        font = QFont()
        font.setItalic(True)
        self.token.setFont(font)
        self.token.setText(self.accentries[0][1])
        self.token_lyt.addWidget(self.token_descr)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.token_lyt.addWidget(line)
        self.token_lyt.addWidget(self.token)
        self.layout.addLayout(self.token_lyt)

        # Type
        self.type_lyt = QHBoxLayout()
        self.type_descr = QLabel("Type")
        self.type_descr.setFixedWidth(110)
        self.type_descr.setAlignment(Qt.AlignRight)
        self.type = QComboBox()
        self.type.setMaximumWidth(140)
        self.type.addItems(["Cold", "Hot", "Custodial"])
        self.type_lyt.addWidget(self.type_descr)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.type_lyt.addWidget(line)
        self.type_lyt.addWidget(self.type)
        self.layout.addLayout(self.type_lyt)

        # KYC
        self.kyc_lyt = QHBoxLayout()
        self.kyc_descr = QLabel("KYC")
        self.kyc_descr.setFixedWidth(110)
        self.kyc_descr.setAlignment(Qt.AlignRight)
        self.kyc = QComboBox()
        self.kyc.setMaximumWidth(140)
        self.kyc.addItems(["Yes", "No"])
        self.kyc_lyt.addWidget(self.kyc_descr)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.kyc_lyt.addWidget(line)
        self.kyc_lyt.addWidget(self.kyc)
        self.layout.addLayout(self.kyc_lyt)

        self.setLayout(self.layout)

        # Description
        self.descr_lyt = QHBoxLayout()
        self.descr_descr = QLabel("Description")
        self.descr_descr.setFixedWidth(110)
        self.descr_descr.setAlignment(Qt.AlignRight)
        self.descr = QLineEdit()
        self.descr.setMaximumWidth(140)
        self.descr_lyt.addWidget(self.descr_descr)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.descr_lyt.addWidget(line)
        self.descr_lyt.addWidget(self.descr)
        self.layout.addLayout(self.descr_lyt)

        # Previous Balance
        self.prevbalance_lyt = QHBoxLayout()
        self.prevbalance_descr = QLabel("Previous Balance")
        self.prevbalance_descr.setFixedWidth(110)
        self.prevbalance_descr.setAlignment(Qt.AlignRight)
        self.prevbalance = QLabel()
        self.prevbalance.setMaximumWidth(140)
        font = QFont()
        font.setItalic(True)
        self.prevbalance.setFont(font)
        self.prevbalance_lyt.addWidget(self.prevbalance_descr)
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.prevbalance_lyt.addWidget(line)
        self.prevbalance_lyt.addWidget(self.prevbalance)
        self.layout.addLayout(self.prevbalance_lyt)

        # New Balance
        self.newbalance_lyt = QHBoxLayout()
        self.newbalance_descr = QLabel("New Balance")
        self.newbalance_descr.setFixedWidth(110)
        self.newbalance_descr.setAlignment(Qt.AlignRight)
        self.newbalance = QDoubleSpinBox()
        self.newbalance.setSingleStep(0.00000001)
        self.newbalance.setDecimals(8)
        self.newbalance.setMinimum(0)
        self.newbalance.setMaximum(9999999999)
        self.newbalance.setMaximumWidth(140)
        self.newbalance.valueChanged.connect(self.setDiff)
        self.newbalance_lyt.addWidget(self.newbalance_descr)
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.newbalance_lyt.addWidget(line)
        self.newbalance_lyt.addWidget(self.newbalance)
        self.layout.addLayout(self.newbalance_lyt)

        # Diff
        self.diff_lyt = QHBoxLayout()
        self.diff = QLabel()
        self.diff.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(8)
        font.setItalic(True)
        self.diff.setFont(font)
        self.diff_lyt.addWidget(QLabel(""))  # For alignment purposes
        self.diff_lyt.addWidget(self.diff)
        self.layout.addLayout(self.diff_lyt)

        # Buttons
        self.bttns_lyt = QHBoxLayout()
        self.previous_bttn = QPushButton("Previous")
        self.previous_bttn.clicked.connect(lambda: self.changeEntry(-1))
        self.bttns_lyt.addWidget(self.previous_bttn)

        self.update_bttn = QPushButton("Update")
        self.update_bttn.clicked.connect(self.updateAccount)
        self.bttns_lyt.addWidget(self.update_bttn)

        self.next_btnn = QPushButton("Next")
        self.next_btnn.clicked.connect(lambda: self.changeEntry(1))
        self.bttns_lyt.addWidget(self.next_btnn)
        self.layout.addLayout(self.bttns_lyt)

        # Setting info according to account
        self.changeEntry(1)
        self.changeEntry(-1)

    def updateAccount(self):
        """Updates the account with a certain token with new data"""
        accname = self.accentries[self.current_accentry][0]
        tokenname = self.accentries[self.current_accentry][1]

        # Updating Type
        cbalances.updateType(accname, tokenname, self.type.currentText())
        # Updating KYC
        cbalances.updateKYC(accname, tokenname, self.kyc.currentText())
        # Updating balance
        cbalances.updateBalance(accname, tokenname, self.newbalance.value())
        # Updating Description
        cbalances.updateDescription(accname, tokenname, self.descr.text())

    def changeEntry(self, change):
        if change == 1:
            self.current_accentry += 1
            if self.current_accentry == len(self.accentries):
                # Reset to 0
                self.current_accentry = 0

        elif change == -1:
            self.current_accentry -= 1
            if self.current_accentry == -1:
                # Reset to last
                self.current_accentry = len(self.accentries)-1

        accname = self.accentries[self.current_accentry][0]
        tokenname = self.accentries[self.current_accentry][1]
        # Account
        self.account.setText(accname)
        # Token
        self.token.setText(tokenname)
        # Type
        self.type.setCurrentText(cbalances.getType(accname, tokenname))
        # KYC
        self.kyc.setCurrentText(cbalances.getKYC(accname, tokenname))
        # Description
        self.descr.setText(cbalances.getDescription(accname, tokenname))
        # Previous Balance
        self.prevbalance.setText(str(cbalances.getBalance(accname, tokenname)))
        # Set New Balance same as previous at start
        self.newbalance.setValue(float(self.prevbalance.text()))

        # Reset diff label
        self.setDiff()

    def setDiff(self):
        diff = str(round(self.newbalance.value() -
                         float(self.prevbalance.text()), 8))
        if float(diff) > 0:
            diff = "+"+diff
        self.diff.setText(diff)


class UpdateTabCryptoSignal(QObject):
    updated = pyqtSignal()
