#!/usr/bin/python3

from PyQt5.QtWidgets import QPushButton, QDialog, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QFormLayout, QDoubleSpinBox, QComboBox, QFrame
from PyQt5.QtCore import pyqtSignal, QObject, QMargins, Qt
from PyQt5.QtGui import QFont

from gui.cdbhandler import cbalances
from gui.prices import prices


class TabCryptoToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add account action
        self.addaccount_action = QAction(self.tr("Add Account"), self)
        self.addaccount_action.setStatusTip(
            self.tr("Add cryptocurrency account"))
        self.addaccount_action.triggered.connect(self.addAccountActionClick)
        self.addAction(self.addaccount_action)

        self.addaccount_dialog = AddAccountDialog()

        # Update all accounts action
        self.update_all_accounts_action = QAction(
            self.tr("Update All Accounts"), self)
        self.update_all_accounts_action.setStatusTip(
            self.tr("Update all current cryptocurrency accounts with new balances"))
        self.update_all_accounts_action.triggered.connect(
            self.updateAccountsActionClick)
        self.addAction(self.update_all_accounts_action)

        # Update Custom Prices
        self.update_custom_prices_action = QAction(
            self.tr("Update Custom Prices"), self)
        self.update_custom_prices_action.setStatusTip(self.tr(
            "Update manually all tokens that don't get their price form external sources"))
        self.update_custom_prices_action.triggered.connect(
            self.updateCustomPricesActionClick)
        self.addAction(self.update_custom_prices_action)

    def addAccountActionClick(self):
        self.addaccount_dialog.setVisible(True)

    def updateAccountsActionClick(self):
        # Tries to display a Dialog where the user can change all accounts balances, and data
        try:
            self.update_all_accounts_dialog = UpdateAllAccountsDialog()
            self.update_all_accounts_dialog.setVisible(True)
        except IndexError:
            # No cryptocurrency accounts yet
            self.update_all_accounts_action.setStatusTip(
                self.tr("No accounts yet. Add and account first"))

    def updateCustomPricesActionClick(self):
        # Tries to display a Dialog where the user can change the price for tokens that get don't get their price from external sources
        self.update_custom_prices = UpdateCustomPricesDialog()
        self.update_custom_prices.show()


class AddAccountDialog(QDialog):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

        self.setWindowTitle(self.tr("Add Cryptocurrency Account"))
        self.layout = QVBoxLayout()
        self.formlayout = QFormLayout()

        # Account Name
        self.name = QLabel(self.tr("Account Name"))
        self.name_edit = QLineEdit()
        self.formlayout.setWidget(0, self.formlayout.LabelRole, self.name)
        self.formlayout.setWidget(0, self.formlayout.FieldRole, self.name_edit)

        # Token
        self.token = QLabel(self.tr("Token"))
        self.token_edit = QLineEdit()
        self.formlayout.setWidget(1, self.formlayout.LabelRole, self.token)
        self.formlayout.setWidget(
            1, self.formlayout.FieldRole, self.token_edit)

        # Starting balance
        self.startingbalance = QLabel(self.tr("Starting Balance"))
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
        self.type = QLabel(self.tr("Type"))
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
        self.descr = QLabel(self.tr("Description"))
        self.descr_edit = QLineEdit()
        self.formlayout.setWidget(5, self.formlayout.LabelRole, self.descr)
        self.formlayout.setWidget(
            5, self.formlayout.FieldRole, self.descr_edit)

        # Functionality
        self.add_acc_bttn = QPushButton(self.tr("Add Account"))
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
            self.tokenname + self.tr(" has to be added \nSelect Method to obtain new its price data"))
        self.layout.addWidget(self.description)

        # Method to obtain new token price data
        self.method = QComboBox()
        self.method.addItems(["Coingecko", self.tr("Custom Price")])
        self.method.currentTextChanged.connect(self.handleMethodChanged)
        self.layout.addWidget(self.method)

        self.currentprice = QLineEdit("")
        self.layout.addWidget(self.currentprice)
        self.currentprice.hide()

        # Save token
        self.save_token_bttn = QPushButton(self.tr("Add Token"))
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
            self.currentprice.setText(self.tr("Getting coingecko's price"))
            try:
                price = prices.toBTCAPI(self.tokenname, 1)
            except:
                price = self.tr("Couldn't get price in BTC")
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

        self.setWindowTitle(self.tr("Update All Accounts"))
        self.layout = QVBoxLayout()

        # All account names:
        self.accentries = [(i[0], i[1]) for i in cbalances.getAllEntries()]
        self.current_accentry = 0

        # Account
        self.account_lyt = QHBoxLayout()
        self.account_descr = QLabel(self.tr("Account"))
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
        self.token_descr = QLabel(self.tr("Token"))
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
        self.type_descr = QLabel(self.tr("Type"))
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
        self.descr_descr = QLabel(self.tr("Description"))
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
        self.prevbalance_descr = QLabel(self.tr("Previous Balance"))
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
        self.newbalance_descr = QLabel(self.tr("New Balance"))
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
        self.previous_bttn = QPushButton(self.tr("Previous"))
        self.previous_bttn.clicked.connect(lambda: self.changeEntry(-1))
        self.bttns_lyt.addWidget(self.previous_bttn)

        self.update_bttn = QPushButton(self.tr("Update"))
        self.update_bttn.clicked.connect(self.updateAccount)
        self.bttns_lyt.addWidget(self.update_bttn)

        self.next_btnn = QPushButton(self.tr("Next"))
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


class UpdateCustomPricesDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Update Custom Prices"))
        self.layout = QVBoxLayout()

        # All token with custom prices
        self.tokenswithcustomprices = prices.getTokensWithCustomPrices()

        # Headers
        self.headers_lyt = QHBoxLayout()

        self.tokenname_header = QLabel("Token")
        self.tokenname_header.setAlignment(Qt.AlignCenter)
        self.tokenname_header.setMaximumHeight(20)
        self.headers_lyt.addWidget(self.tokenname_header)

        self.tokenlastprice_header = QLabel("Last Price (BTC)")
        self.tokenlastprice_header.setAlignment(Qt.AlignCenter)
        self.tokenlastprice_header.setMaximumHeight(20)
        self.headers_lyt.addWidget(self.tokenlastprice_header)

        self.tokennewprice_header = QLabel("New Price (BTC)")
        self.tokennewprice_header.setAlignment(Qt.AlignCenter)
        self.tokennewprice_header.setMaximumHeight(20)
        self.headers_lyt.addWidget(self.tokennewprice_header)

        self.layout.addLayout(self.headers_lyt)

        # Content
        for token in self.tokenswithcustomprices:
            # Too keep track of al these rows later, we'll store each tokenname and tokennewprice on a list
            self.row_lyts_list = []

            # A row for each tokens
            tokenname = token[0]
            tokenlastprice = token[1]

            row_lyt = QHBoxLayout()
            tokenname_wgt = QLabel(tokenname.upper())
            tokenname_wgt.setFixedWidth(50)
            row_lyt.addWidget(tokenname_wgt)
            tokenlastprice_wdgt = QLineEdit(str(tokenlastprice))
            tokenlastprice_wdgt.setReadOnly(True)
            row_lyt.addWidget(tokenlastprice_wdgt)
            tokennewprice_wgt = QDoubleSpinBox()
            tokennewprice_wgt.setMinimum(0)
            tokennewprice_wgt.setDecimals(8)
            tokennewprice_wgt.setValue(tokenlastprice)
            row_lyt.addWidget(tokennewprice_wgt)

            self.row_lyts_list.append(
                (tokenname_wgt, tokennewprice_wgt))  # For later changes
            self.layout.addLayout(row_lyt)

        # Button for updating changes
        self.updatechanges_bttn = QPushButton("Update Prices")
        self.updatechanges_bttn.clicked.connect(self.updateChanges)
        self.layout.addWidget(self.updatechanges_bttn)

        self.setLayout(self.layout)

    def updateChanges(self):
        """Updates custom prices on the prices json file"""
        for token in self.row_lyts_list:
            tokenname = token[0].text().lower()
            tokennewprice = token[1].value()

            prices.updateCustomPrice(tokenname, tokennewprice)

        self.close()


class UpdateTabCryptoSignal(QObject):
    updated = pyqtSignal()
