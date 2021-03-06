#!/usr/bin/python3
"""
The Toolbar from Tabcrypto, with all of its actions and functionality.
"""
import logging

from PyQt5.QtWidgets import QPushButton, QDialog, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtWidgets import QLineEdit, QLabel, QFormLayout, QDoubleSpinBox, QComboBox, QFrame, QCheckBox, QGridLayout, QWidget, QListWidget
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QFont

from portfolio.db.cdbhandler import cbalances
from portfolio.utils.prices import prices


class TabCryptoToolBar(QToolBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add account action
        self.addaccount_action = QAction(self.tr("Add Account"), self)
        self.addaccount_action.setStatusTip(
            self.tr("Add cryptocurrency account"))
        self.addaccount_action.triggered.connect(self.addAccountActionClick)
        self.addAction(self.addaccount_action)

        # Remove account action
        self.removeaccount_action = QAction(self.tr("Remove Account"), self)
        self.removeaccount_action.setStatusTip(
            self.tr("Remove cryptocurrency account"))
        self.removeaccount_action.triggered.connect(
            self.removeAccountActionClick)
        self.addAction(self.removeaccount_action)

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

        # Update Coingecko Prices
        self.update_coingecko_prices_action = QAction(
            self.tr("Update Coingecko Prices"), self)
        self.update_coingecko_prices_action.setStatusTip(self.tr(
            "Update manually all tokens that get their price form external sources"))
        self.update_coingecko_prices_action.triggered.connect(
            self.updateCoingeckoPricesActionClick)
        self.addAction(self.update_coingecko_prices_action)

        # Pre-computed dialogs
        self.addaccount_dialog = AddAccountDialog(self)
        self.removeaccount_dialog = RemoveAccountDialog(self)

    def addAccountActionClick(self):
        self.addaccount_dialog.show()

    def removeAccountActionClick(self):
        self.removeaccount_dialog.exec_()

    def updateAccountsActionClick(self):
        """
        Tries to display a Dialog where the user can change all accounts balances, and data
        """
        try:
            update_all_accounts_dialog = UpdateAllAccountsDialog(self)
            update_all_accounts_dialog.setVisible(True)
        except IndexError:
            # No cryptocurrency accounts yet
            self.update_all_accounts_action.setStatusTip(
                self.tr("No accounts yet. Add and account first"))

    def updateCustomPricesActionClick(self):
        """
        Tries to display a Dialog where the user can change the price of
        tokens that don't get their price from external sources
        """
        update_custom_prices = UpdateCustomPricesDialog('custom', self)
        update_custom_prices.show()

    def updateCoingeckoPricesActionClick(self):
        """
        Tries to display a Dialog where the user can change the price of
        tokens that get their price from external sources
        """
        update_custom_prices = UpdateCustomPricesDialog('coingecko', self)
        update_custom_prices.show()


class AddAccountDialog(QDialog):
    """ Dialog to add a new account on the database """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        # First, we need to check if the account's token is new.
        # In that case, we need to ask the user on how to get info avout the token itself
        token = self.token_edit.text().lower()
        if prices.token_in_prices(token.lower()) is False:
            # We display a dialog
            new_token_dialog = NewTokenDialog(token, self)
            new_token_dialog.exec_()

        else:
            # The token already exists
            account = self.name_edit.text()

            if (account, token) in cbalances.get_all_accounts_with_token():
                # Account already exists
                mssg = QMessageBox()
                mssg.setText(
                    self.tr(f"Account {account} with token {token.upper()} already exists"))
                mssg.exec_()
                return

            # Create new account
            amount = self.startingbalance_edit.value()
            _type = self.type_edit.currentText()
            kyc = self.kyc_edit.currentText()
            description = self.descr_edit.text()
            cbalances.add_account(account, token, amount,
                                  _type, kyc, description)

            self.updatecryptosignal.updated.emit()
            self.close()


class RemoveAccountDialog(QDialog):
    """ Dialog to delete a new account from the database """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.tr("Remove Cryptocurrency Account"))
        self.layout = QVBoxLayout()
        self.setFixedWidth(300)

        # Account Selection
        self.acc_select = QComboBox()
        self.acc_select.addItems(cbalances.get_all_accounts())
        self.acc_select.currentTextChanged.connect(self.showTokens)

        # Token Selection
        self.token_select_wrapper = QWidget()
        self.token_select_lyt = QGridLayout()  # Filled on showTokens event

        # Remove Button
        self.remove_bttn = QPushButton(self.tr("Delete"))
        self.remove_bttn.clicked.connect(self.deleteAccounts)

        self.layout.insertWidget(0, self.acc_select)
        self.layout.insertWidget(2, self.remove_bttn)
        self.setLayout(self.layout)

        # Initialize with first account
        self.showTokens(self.acc_select.currentText())

    def showTokens(self, account):
        self.token_select_wrapper.deleteLater()
        self.token_checkboxes = []

        self.token_select_wrapper = QWidget()
        self.token_select_lyt = QGridLayout()

        tokens = cbalances.get_tokens_from_account(account)
        for i, token in enumerate(tokens):
            token_select = QCheckBox()
            token_select.setText(token.upper())
            row = i//4
            col = i % 4
            self.token_select_lyt.addWidget(token_select, row, col)
            self.token_checkboxes.append(token_select)

        self.token_select_wrapper.setLayout(self.token_select_lyt)
        self.layout.insertWidget(1, self.token_select_wrapper)

    def deleteAccounts(self):
        """
        Removes all checked accounts from de database
        """
        acc = self.acc_select.currentText()
        for token_select in self.token_checkboxes:
            if token_select.isChecked():
                cbalances.delete_account(
                    acc, token_select.text())

        mssg_box = QMessageBox(self)
        mssg_box.setText(f"Accounts removed")
        mssg_box.exec_()

        self.acc_select.clear()
        self.acc_select.addItems(cbalances.get_all_accounts())
        self.close()


class NewTokenDialog(QDialog):
    """
    When an account with an unknown token is added,
    the token has to be added to our prices first.
    """

    def __init__(self, tokenname, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Data
        self.tokenname = tokenname
        # UI
        self.layout = QVBoxLayout()

        # New Token Description
        self.description = QLabel(self.tr(
            f"{self.tokenname.upper()} token has to be added. \nSelect Method to obtain price data"))
        self.layout.addWidget(self.description)

        # Method to obtain new token price data
        self.method = QComboBox()
        self.method.addItems(["Coingecko", self.tr("Custom Price")])
        self.method.currentTextChanged.connect(self.handleMethodChanged)
        self.layout.addWidget(self.method)

        # Since there could be multiple tokens with the same symbol,
        # the user will have to select one of them from their id
        self.select_id = QComboBox()
        self.select_id.hide()
        self.layout.addWidget(self.select_id)
        # If the new token has a custom price, the user has to add an id manually
        self.manual_id = QLineEdit()
        self.manual_id.setPlaceholderText("Token full name")
        self.manual_id.hide()
        self.layout.addWidget(self.manual_id)

        # Displaying the current price for the new token
        self.currentprice = QLineEdit("")
        self.currentprice.setPlaceholderText("Token's price (in BTC)")
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
        """
        Writes new token info on prices folder
        """
        token, method = self.tokenname, self.method.currentText()
        try:
            if method == self.tr('Coingecko'):
                method = 'coingecko'
                _id = self.select_id.currentText()
                price = float(self.currentprice.text().split(" ")[0])
            elif method == self.tr('Custom Price'):
                method = 'custom'
                _id = self.manual_id.text()
                price = float(self.currentprice.text())
            prices.add_token_price(token, method, _id, price)
            self.close()

        except Exception:
            import traceback
            logging.warning(
                f"Couldn't add token price \nError: {traceback.format_exc()}")
            error_mssg = QMessageBox()
            error_mssg.setIcon(QMessageBox.Critical)
            error_mssg.setText(
                self.tr("Can't add account. Make sure price and id are properly formatted"))
            error_mssg.exec_()

    def handleMethodChanged(self, method):
        """ Depending on the method, we display different things """
        if method == 'Coingecko':
            self.manual_id.hide()  # Not needed
            # Checking if there are multiple tokens for a certain symbol
            possibleids = prices.symbol_to_id_coingecko_list(self.tokenname)
            if len(possibleids) == 0:
                self.select_id.addItem(
                    self.tr("No ids for that token name"))
            for tokenid in possibleids:
                self.select_id.addItem(tokenid)

            self.select_id.currentTextChanged.connect(
                self.handleIdSelected)
            self.select_id.show()

            self.currentprice.setReadOnly(True)
            self.currentprice.setText(
                self.tr("Select Id above to get coingecko's price"))

        elif method == self.tr('Custom Price'):
            # We add a field to put the current price
            self.select_id.clear()
            self.select_id.hide()
            self.manual_id.setText("")
            self.manual_id.show()
            self.currentprice.clear()
            self.currentprice.setReadOnly(False)

        self.handleIdSelected(self.select_id.currentText())
        self.currentprice.show()

    def handleIdSelected(self, _id):
        """
        When an id from the multiple options is selected,
        we can finally get the token's price and display it
        """
        try:
            price = prices.to_btc_api(_id, 1)
        except:
            price = self.tr("Couldn't get price in BTC")
        self.currentprice.setText(str(price) + " BTC")


class UpdateAllAccountsDialog(QDialog):
    """ Dialog to see each crypto account and edit it as wished """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Update All Accounts"))
        self.layout = QVBoxLayout()

        # All account names:
        self.accnames = cbalances.get_all_accounts()

        # Account
        self.account_lyt = QHBoxLayout()
        self.account_descr = QLabel(self.tr("Account"))
        self.account_descr.setFixedWidth(110)
        self.account_descr.setAlignment(Qt.AlignRight)
        self.accounts = QComboBox()
        self.accounts.setMaximumWidth(140)
        self.accounts.addItems(self.accnames)
        # Functionality: when account is changed, selectable tokens have to
        # change to the ones from that account
        self.accounts.currentTextChanged.connect(self.updateTokens)
        font = QFont()
        font.setItalic(True)
        self.accounts.setFont(font)
        self.account_lyt.addWidget(self.account_descr)
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.account_lyt.addWidget(line)
        self.account_lyt.addWidget(self.accounts)
        self.layout.addLayout(self.account_lyt)

        # Token
        self.token_lyt = QHBoxLayout()
        self.token_descr = QLabel(self.tr("Token"))
        self.token_descr.setFixedWidth(110)
        self.token_descr.setAlignment(Qt.AlignRight)
        self.tokens = QComboBox()
        self.tokens.setMaximumWidth(140)
        font = QFont()
        font.setItalic(True)
        self.tokens.setFont(font)
        self.token_lyt.addWidget(self.token_descr)
        # Functionality: when the token is changed,
        # all the account info (balance, type, etc.) changes too
        self.tokens.currentTextChanged.connect(
            lambda tokenname: self.updateWithAccInfo(self.accounts.currentText(), tokenname))
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.token_lyt.addWidget(line)
        self.token_lyt.addWidget(self.tokens)
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

        # Button to save changes
        self.savebttn = QPushButton(self.tr("Save Changes"))
        self.savebttn.clicked.connect(self.updateAccount)
        self.layout.addWidget(self.savebttn)

        # Initialize
        self.accounts.setCurrentIndex(1)

    def updateAccount(self):
        """Updates the account with a certain token with new data"""
        accname = self.accounts.currentText()
        tokenname = self.tokens.currentText()

        # Updating Type
        cbalances.update_type(accname, tokenname, self.type.currentText())
        # Updating KYC
        cbalances.update_kyc(accname, tokenname, self.kyc.currentText())
        # Updating balance
        cbalances.update_balance(accname, tokenname, self.newbalance.value())
        # Updating Description
        cbalances.update_description(accname, tokenname, self.descr.text())

        self.updateWithAccInfo(accname, tokenname)

        # Show message
        mssg = QMessageBox(self)
        mssg.setText(self.tr("Updated!"))
        mssg.exec_()

    def updateTokens(self, accountname):
        """
        Updates the token combobox to show the tokens from the new account
        that has been selected
        """
        self.tokens.clear()
        tokens_from_acc = [i.upper()
                           for i in cbalances.get_tokens_from_account(accountname)]
        self.tokens.addItems(tokens_from_acc)

    def updateWithAccInfo(self, accname, tokenname):
        if tokenname != "":
            accname = self.accounts.currentText()
            # Type
            self.type.setCurrentText(cbalances.get_type(accname, tokenname))
            # KYC
            self.kyc.setCurrentText(cbalances.get_kyc(accname, tokenname))
            # Description
            self.descr.setText(cbalances.get_description(accname, tokenname))
            # Previous Balance
            self.prevbalance.setText(
                str(cbalances.get_balance(accname, tokenname)))
            # Set New Balance same as previous at start
            self.newbalance.setValue(float(self.prevbalance.text()))

            # Reset diff label
            self.setDiff()

    def setDiff(self):
        """
        Displays the difference between the current balance of an account
        and the new one that the user is proposing.

        Just for informational purposes.
        """
        diff = str(round(self.newbalance.value() -
                         float(self.prevbalance.text()), 8))
        if float(diff) > 0:
            diff = "+"+diff
        self.diff.setText(diff)


class UpdateCustomPricesDialog(QDialog):
    """
    Since certain token obtain their prices from user input, and not externally,
    this dialog will let the user change those prices whenever they want.
    """

    def __init__(self, method, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(self.tr("Update Custom Prices"))

        self.layout = QVBoxLayout()

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

        # All token with custom prices
        method = method.lower()
        if method == 'custom':
            self.tokenswithprices = prices.get_tokens_with_custom_prices()
        if method == 'coingecko':
            self.tokenswithprices = prices.get_tokens_with_coingecko_prices()

        # Content
        self.row_lyts_list = []
        for token in self.tokenswithprices:
            # Too keep track of al these rows later,
            # we'll store each tokenname and tokennewprice on a list

            # A row for each token
            tokenname = token[0]
            tokenlastprice = token[1]
            row_lyt = UpdateCustomPricesDialogRow(tokenname, tokenlastprice)

            # For later changes
            self.row_lyts_list.append(row_lyt)
            self.layout.addLayout(row_lyt)

        # Button for updating changes
        self.updatechanges_bttn = QPushButton(self.tr("Update Prices"))
        self.updatechanges_bttn.clicked.connect(self.updateChanges)
        self.layout.addWidget(self.updatechanges_bttn)

        self.setLayout(self.layout)

    def updateChanges(self):
        """Updates custom prices on the prices json file"""
        for row_lyt in self.row_lyts_list:
            row_lyt.setCurrentPriceOnPrices()
        self.close()


class UpdateCustomPricesDialogRow(QHBoxLayout):
    """
    A row that contains a tokens symbol, previous price,
    new price and lets the user change the method for obtaining price data
    """

    def __init__(self, tokensymbol, tokenlastprice, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tokensymbol = tokensymbol
        self.setObjectName(tokensymbol)

        self.tokenname_wgt = QLabel(tokensymbol.upper())
        self.tokenname_wgt.setFixedWidth(50)
        self.addWidget(self.tokenname_wgt)

        self.tokenlastprice_wdgt = QLineEdit(str(tokenlastprice))
        self.tokenlastprice_wdgt.setReadOnly(True)
        self.addWidget(self.tokenlastprice_wdgt)

        self.tokennewprice_wgt = QDoubleSpinBox()
        self.tokennewprice_wgt.setMinimum(0)
        self.tokennewprice_wgt.setDecimals(8)
        self.tokennewprice_wgt.setValue(tokenlastprice)
        self.addWidget(self.tokennewprice_wgt)

        # If coingecko's method is selected and multiple tokens have the
        # same symbol, selecting the desired one will be necessary
        self.select_id_coingecko = QComboBox()
        self.select_id_coingecko.currentTextChanged.connect(
            self.setCoingeckoPrice)
        self.select_id_coingecko.hide()
        self.addWidget(self.select_id_coingecko)

        self.changemethod = QComboBox()
        self.changemethod.addItems(['Custom', 'Coingecko'])
        self.changemethod.currentTextChanged.connect(self.changeTokenMethod)
        current_method = prices.get_token_method(self.tokensymbol)
        self.changemethod.setCurrentText(
            current_method[0].upper()+current_method[1:])
        self.addWidget(self.changemethod)

    def changeTokenMethod(self, method):
        """
        Displays the row according to the new method
        """
        method = method.lower()

        if method == 'custom':
            self.tokennewprice_wgt.setValue(0)
            self.select_id_coingecko.clear()
            self.select_id_coingecko.hide()

        elif method == 'coingecko':
            # The user has to decide which token from coingecko
            # corresponds to the symbol
            ids_with_symbol = prices.symbol_to_id_coingecko_list(
                self.tokensymbol)
            if ids_with_symbol == []:
                # Symbol not in coingeckos list
                self.changemethod.setCurrentText('Custom')
                mssg_box = QMessageBox()
                mssg_box.setText(
                    "Symbol {} not in Coingecko's list. Update data or change to Custom".format(self.tokensymbol.upper()))
                mssg_box.exec()
            else:
                for _id in ids_with_symbol:
                    self.select_id_coingecko.addItem(_id)
                self.select_id_coingecko.show()
        else:
            return

    def setCoingeckoPrice(self, _id):
        if self.changemethod.currentText().lower() == 'coingecko':
            self.tokennewprice_wgt.setValue(prices.to_btc_api(_id, 1))

    def setCurrentPriceOnPrices(self):
        """
        Updates coinprices with the row info
        """
        tokensymbol = self.tokensymbol.lower()
        method = self.changemethod.currentText().lower()
        if method == 'custom':
            tokenid = tokensymbol
        else:
            tokenid = self.select_id_coingecko.currentText()
        price = self.tokennewprice_wgt.value()

        prices.add_token_price(tokensymbol, method, tokenid, price)


class UpdateTabCryptoSignal(QObject):
    """ Signal to indicate when the TabCrypto has to be refreshed/repainted"""
    updated = pyqtSignal()
