#!/usr/bin/python3

"""
Tab that shows all of the main info about all cryptocurrency accounts, tokens,
history and more.
"""

import json
import os
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QSplitter, QDialog
from PyQt5.QtCore import Qt, QDateTime, QDate
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QSplineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QPixmap, QIcon

from portfolio.db.cdbhandler import cbalances, chistoricalbalances
from portfolio.gui.ui_components.fonts import TitleFont, TokenBalanceFont
from portfolio.utils.prices import prices
from portfolio.gui.tabcrypto.tabcrypto_toolbar import TabCryptoToolBar
from portfolio.utils import confighandler

CONFIG_FILE_PATH = confighandler.getConfigPath()
RESOURCES_PATH = confighandler.getUserDataPath()


class TabCrypto(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Crypto")

        # UI
        self.mainlayout = QVBoxLayout()
        self.upperlayout = QHBoxLayout()

        # Token Description
        self.description = DescriptionLayout(self)
        self.upperlayout.addWidget(self.description)

        # Token transactions
        self.tokenbalances = BalancesTable(self)
        self.upperlayout.addWidget(self.tokenbalances)

        # Historical Balances Table
        self.historicalbalances = HistoricalBalancesTable(self)
        self.upperlayout.addWidget(self.historicalbalances)

        # Data entries
        self.toolbar = TabCryptoToolBar(self)

        # Charts
        self.chart_lyt = QSplitter(self)
        self.chart_lyt.setHandleWidth(2)
        # Pie Charts
        self.accountpiechart = AccountPieChart(self)
        self.tokenpiechart = TokenPieChart(self)
        self.piecharts_lyt = QHBoxLayout()
        self.piecharts_lyt.addWidget(self.tokenpiechart)
        self.piecharts_lyt.addWidget(self.accountpiechart)
        self.piecharts_wgt = QWidget()
        self.piecharts_wgt.setLayout(self.piecharts_lyt)

        self.chart_lyt.addWidget(self.piecharts_wgt)

        # Line Charts
        self.balancehistorychart = BalanceHistoryChartView()
        self.chart_lyt.addWidget(self.balancehistorychart)

        # Functionality
        # When the select_mode button is clicked, we swith between modes
        self.description.select_mode.clicked.connect(
            lambda: self.updateSelectMode())
        # When a new selection is made, we update al info
        self.description.select_token_or_account.currentTextChanged.connect(
            self.selectionChanged)
        # When prices data is updated, we refresh everything
        self.description.updatedata.clicked.connect(
            lambda: self.selectionChanged(self.description.select_token_or_account.currentText()))

        # When an item of the tablewidget is double clicked, if it is an account or token
        # we switch to that
        self.tokenbalances.itemDoubleClicked.connect(
            self.updateWithDoubleClick)

        self.mainlayout.addWidget(self.toolbar)
        self.mainlayout.addLayout(self.upperlayout)
        self.mainlayout.addWidget(self.chart_lyt)
        self.setLayout(self.mainlayout)

        # ---- Initialization ----
        DATABASE_TOKENS = [i.upper() for i in cbalances.get_all_tokens()]
        # Checking if there is remote data avaliable
        prices.initialize_prices()
        if 'coingeckoids.json' not in os.listdir('prices'):
            prices.updateCoinListFile()
        if 'coinprices.json' not in os.listdir('prices'):
            with open(os.path.join('prices', 'coinprices.json'), 'w') as f:
                json.dump({}, f)
        if 'btctofiat.json' not in os.listdir('prices'):
            prices.updateBTCToFiat()

        # Checking that all the tokens from the database have prices
        coinprices_tokens = prices.getAllTokens()
        for token in DATABASE_TOKENS:
            token = token.lower()
            if token not in coinprices_tokens:
                prices.addTokenPrice(token, 'custom', token, 0)

        # Initialize with "All"
        self.selectionChanged("All")
        self.chart_lyt.setSizes([300, 100])

    def selectionChanged(self, selection):
        """
        Switching between account/token
        """
        if self.description.mode == 0:
            # All mode
            print("Selection changed to ", selection)
            self.tokenbalances.updateWithAll()
            self.historicalbalances.updateWithAll()
            self.description.allMode()
            self.accountpiechart.allMode()
            self.tokenpiechart.allMode()
            self.balancehistorychart.setupChartWithData('all')

        elif self.description.mode == 1:
            # Token mode
            print("Token changed to ", selection)
            self.tokenbalances.updateWithToken(selection)
            self.historicalbalances.updateWithToken(selection)
            self.accountpiechart.updateWithToken(selection)
            self.tokenpiechart.selectSlice(selection)
            self.description.tokenChanged(selection)
            self.balancehistorychart.setupChartWithData(
                'token', name=selection.lower())

        elif self.description.mode == 2:
            print("Account changed to ", selection)
            # Account mode
            self.tokenbalances.updateWithAccount(selection)
            self.historicalbalances.updateWithAccount(selection)
            self.tokenpiechart.updateWithAccount(selection)
            self.accountpiechart.selectSlice(selection)
            self.description.accountChanged(selection)
            self.balancehistorychart.setupChartWithData(
                'account', name=selection)

    def updateSelectMode(self, mode=None):
        """ Switches between three states: all, token, or account selection """
        if mode is None:
            # Switches to next mode
            self.description.mode += 1
            self.description.mode = self.description.mode % 3
        else:
            # Switches to desired mode
            if mode == "Account":
                self.description.mode = 2
            elif mode == "Token":
                self.description.mode = 1

        if self.description.mode == 0:
            # All mode
            self.description.select_mode.setText("All")
            self.description.select_token_or_account.clear()
            self.description.select_token_or_account.addItem("All")
        elif self.description.mode == 1:
            # Token mode
            self.description.select_mode.setText("Token")
            self.description.select_token_or_account.clear()
            DATABASE_TOKENS = [i.upper() for i in cbalances.get_all_tokens()]
            self.description.select_token_or_account.addItems(DATABASE_TOKENS)
            self.tokenpiechart.allMode()
        elif self.description.mode == 2:
            # Account mode
            self.description.select_mode.setText("Account")
            self.description.select_token_or_account.clear()
            DATABASE_ACCOUNTS = cbalances.get_all_accounts()
            self.description.select_token_or_account.addItems(
                DATABASE_ACCOUNTS)
            self.accountpiechart.allMode()

    def updateWithDoubleClick(self, item):
        """
        It looks for the double clicked item and if it is an account or token, it switches the whole layout to that
        """
        itemname = item.data(0)
        columname = (self.tokenbalances.horizontalHeaderItem(
            item.column()).text())

        if columname in (self.tr("Account"), self.tr("Token")):
            self.updateSelectMode(mode=columname)
            self.selectionChanged(itemname)
            self.description.select_token_or_account.setCurrentText(itemname)


class DescriptionLayout(QWidget):
    """
    Displays the main information about the token or account, i.e. ,
    the name, balance in multiple denominators.

    Also presents different buttons for the user to switch between accounts,etc.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.setFixedWidth(600)

        # Token Selection
        self.select_token_or_account_lyt = QHBoxLayout()
        self.select_token_or_account = QComboBox()
        self.select_token_or_account.addItem("All")
        #   Button to update coinlist info file
        self.updatedata = QPushButton(self.tr("Update Prices"))
        self.updatedata.setMaximumWidth(100)
        self.updatedata.clicked.connect(
            self.updateDataFiles)
        # Button to change selection mode between accounts or tokens
        self.select_mode = QPushButton("All")
        self.select_mode.setMaximumWidth(150)
        self.select_mode.setIcon(
            QIcon(QPixmap(os.path.join(RESOURCES_PATH, 'switch.svg'))))

        self.select_token_or_account_lyt.addWidget(
            self.select_token_or_account)
        self.select_token_or_account_lyt.addWidget(self.select_mode)
        self.select_token_or_account_lyt.addWidget(self.updatedata)

        # Token/Accout Name Label
        self.token_or_account_name = QLabel(self.tr("All Coins"))
        self.token_or_account_name.setAlignment(
            Qt.AlignBottom | Qt.AlignHCenter)
        self.token_or_account_name.setFont(TitleFont())
        self.token_or_account_name.setMaximumHeight(100)

        # Token balances layout
        self.token_or_account_balances_lyt = QHBoxLayout()
        # Token total balance
        self.token_or_account_balance = QLabel("")
        self.token_or_account_balance.setAlignment(Qt.AlignCenter)
        self.token_or_account_balance.setFont(TokenBalanceFont())
        # Token total balance (BTC)
        self.token_or_account_balance_btc = QLabel("")
        self.token_or_account_balance_btc.setAlignment(Qt.AlignCenter)
        self.token_or_account_balance_btc.setFont(TokenBalanceFont())
        # Token total balance (fiat)
        self.token_or_account_balance_fiat = QLabel("")
        self.token_or_account_balance_fiat.setAlignment(Qt.AlignCenter)
        self.token_or_account_balance_fiat.setFont(TokenBalanceFont())

        self.token_or_account_balances_lyt.addWidget(
            self.token_or_account_balance)
        self.token_or_account_balances_lyt.addWidget(
            self.token_or_account_balance_btc)
        self.token_or_account_balances_lyt.addWidget(
            self.token_or_account_balance_fiat)

        # Adding everything together
        self.layout.addLayout(self.select_token_or_account_lyt)
        self.layout.addWidget(self.token_or_account_name)
        self.layout.addLayout(self.token_or_account_balances_lyt)
        self.setLayout(self.layout)

        # We initialize with 'All'
        self.select_token_or_account.setCurrentText("All")
        self.mode = 0

        # Selecting fiat currency
        self.FIAT_CURRENCY = confighandler.get_fiat_currency().upper()

    def allMode(self):
        """
        If 'All' is selected, we show the full balance of all tokens in all accounts
        """

        self.token_or_account_name.setText(self.tr("All Coins"))
        totalbalancebtc, totalbalancefiat = 0, 0
        DATABASE_TOKENS = cbalances.get_all_tokens()
        for t in DATABASE_TOKENS:
            tokenbalance = cbalances.get_total_token_balance(t)
            tokenbalance_btc = prices.to_btc(t, tokenbalance)
            totalbalancebtc += tokenbalance_btc
            totalbalancefiat += prices.btc_to_fiat(
                tokenbalance_btc, currency=self.FIAT_CURRENCY)
        self.token_or_account_balance.hide()
        self.token_or_account_balance_btc.setText(
            str(round(totalbalancebtc, 8))+" BTC")
        self.token_or_account_balance_fiat.setText(
            str(round(totalbalancefiat, 2))+" " + self.FIAT_CURRENCY)

    def tokenChanged(self, tokensymbol):
        """
        If a Token is selected, we show the total amount of it on all accounts
        """
        # Getting token id from coingecko's list
        if tokensymbol == '':
            # No token selected
            return

        try:
            token_name = prices.symbolToId(tokensymbol)
        except KeyError:
            # Not in Coingecko's list
            print("Selected symbol {} is not in coingecko's stored list".format(
                tokensymbol))
            token_name = tokensymbol

        # Updating token info
        self.token_or_account_name.setText(
            token_name[0].upper()+token_name[1:])

        # Updating token balances
        tokenbalance = round(cbalances.get_total_token_balance(tokensymbol), 6)
        self.token_or_account_balance.setText(
            str(tokenbalance)+' '+tokensymbol)
        self.token_or_account_balance.show()
        tokenbalancebtc = round(prices.to_btc(tokensymbol, tokenbalance), 8)
        self.token_or_account_balance_btc.setText(str(tokenbalancebtc)+" BTC")
        if tokensymbol in ["BTC", "btc"]:
            self.token_or_account_balance_btc.setText("")
        tokenbalancefiat = prices.btc_to_fiat(tokenbalancebtc)
        self.token_or_account_balance_fiat.setText(
            str(tokenbalancefiat) + " {}".format(self.FIAT_CURRENCY.upper()))

    def accountChanged(self, accountname):
        """
        If an account is selected, we show the total amount of all of its tokens
        """

        # Updating account name
        self.token_or_account_name.setText(accountname)

        # Updating account balances
        acc_token_balances = cbalances.get_entries_with_account(accountname)
        total_in_btc = 0
        for atb in acc_token_balances:
            token = atb[1]
            amount = atb[2]
            amount_btc = prices.to_btc(token, amount)
            total_in_btc += amount_btc
        total_in_fiat = prices.btc_to_fiat(
            total_in_btc, currency=self.FIAT_CURRENCY)
        total_in_btc = round(total_in_btc, 8)
        total_in_fiat = int(round(total_in_fiat, 0))

        self.token_or_account_balance.hide()  # Not useful here
        self.token_or_account_balance_btc.setText(str(total_in_btc) + " BTC")
        self.token_or_account_balance_fiat.setText(
            str(total_in_fiat) + " " + self.FIAT_CURRENCY.upper())

    def updateDataFiles(self):
        """Calls coingecko's API and writes btcfiat.json, coinlist.json, coinprices.json"""
        self.parent().parent().parent().parent().parent(
        ).statusbar.showMessage(self.tr("Updating data..."))
        updatingdata_mssg = QDialog(self)
        updatingdata_lyt = QVBoxLayout()
        text = QLabel(self.tr("Updating data. Please wait..."))
        updatingdata_lyt.addWidget(text)
        updatingdata_mssg.setLayout(updatingdata_lyt)
        updatingdata_mssg.show()
        prices.updateCoingeckoPrices()
        prices.updateCoinListFile()
        prices.updateBTCToFiat()
        self.parent().parent().parent().parent().parent(
        ).statusbar.showMessage(self.tr("Data Updated!"))
        updatingdata_mssg.close()


class BalancesTable(QTableWidget):
    """
    A table showing a selection of accounts and tokens, that dynamically changes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setRowCount(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Not editable
        self.setStyleSheet("border: 0px")

        self.setSortingEnabled(True)

        self.setMaximumHeight(300)
        # self.setMaximumWidth(600)
        self.setMinimumWidth(600)
        self.verticalHeader().hide()

        # Selecting fiat currency
        self.FIAT_CURRENCY = confighandler.get_fiat_currency().upper()

    def updateWithToken(self, token):
        """Only shows database entries where token=token"""
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ['Account', 'Balance ({})'.format(token),
             'Balance(BTC)', 'Balance ({})'.format(self.FIAT_CURRENCY), 'Type', 'KYC', 'Description'])

        rows_to_insert = cbalances.get_entries_with_token(token)
        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Account
            self.setItem(numrow, 0, QTableWidgetItem(row[0]))
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[2])
            self.setItem(numrow, 1, item)
            # Balance (BTC)
            balance_in_btc = prices.toBTC(row[1], row[2])
            item = QTableWidgetItem()
            item.setData(0, balance_in_btc)
            self.setItem(numrow, 2, item)
            # Balance (Fiat)
            balance_in_fiat = prices.btcToFiat(
                balance_in_btc, currency=self.FIAT_CURRENCY)
            item = QTableWidgetItem()
            item.setData(0, balance_in_fiat)
            self.setItem(numrow, 3, item)
            # Type
            item = formatTypeItem(QTableWidgetItem(str(row[3])))
            self.setItem(numrow, 4, item)
            # KYC
            item = formatKYCItem(QTableWidgetItem(str(row[4])))
            self.setItem(numrow, 5, item)
            # Description
            self.setItem(numrow, 6, QTableWidgetItem(str(row[5])))

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def updateWithAccount(self, account):
        """Only shows database entries where account=account"""
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            ['Token', 'Balance', 'Balance(BTC)',
             'Balance({})'.format(self.FIAT_CURRENCY), 'Type', 'KYC', 'Description'])

        rows_to_insert = cbalances.get_entries_with_account(account)
        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Token
            self.setItem(numrow, 0, QTableWidgetItem(row[1].upper()))
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[2])
            self.setItem(numrow, 1, item)
            # Balance (BTC)
            balance_in_btc = prices.to_btc(row[1], row[2])
            item = QTableWidgetItem()
            item.setData(0, balance_in_btc)
            self.setItem(numrow, 2, item)
            # Balance (Fiat)
            balance_in_fiat = prices.btc_to_fiat(
                balance_in_btc, currency=self.FIAT_CURRENCY)
            item = QTableWidgetItem()
            item.setData(0, balance_in_fiat)
            self.setItem(numrow, 3, item)
            # Type
            item = formatTypeItem(QTableWidgetItem(str(row[3])))
            self.setItem(numrow, 4, item)
            # KYC
            item = formatKYCItem(QTableWidgetItem(str(row[4])))
            self.setItem(numrow, 5, item)
            # Description
            self.setItem(numrow, 6, QTableWidgetItem(str(row[5])))

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def updateWithAll(self):
        """
        Sets the table in  'All' mode,
        which shows all accounts and tokens
        """
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            ['Account', 'Token', 'Balance', 'Balance(BTC)',
             'Balance({})'.format(self.FIAT_CURRENCY), 'Type', 'KYC', 'Description'])
        rows_to_insert = cbalances.get_all_entries()

        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Account
            self.setItem(numrow, 0, QTableWidgetItem(row[0]))
            # Token
            self.setItem(numrow, 1, QTableWidgetItem(row[1].upper()))
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[2])
            self.setItem(numrow, 2, item)
            # Balance(BTC)
            balance_in_btc = prices.to_btc(row[1], row[2])
            item = QTableWidgetItem()
            item.setData(0, balance_in_btc)
            self.setItem(numrow, 3, item)
            # Balance (Fiat)
            balance_in_fiat = prices.btc_to_fiat(
                balance_in_btc, currency=self.FIAT_CURRENCY)
            item = QTableWidgetItem()
            item.setData(0, balance_in_fiat)
            self.setItem(numrow, 4, item)
            # Type
            item = formatTypeItem(QTableWidgetItem(str(row[3])))
            self.setItem(numrow, 5, item)
            # KYC
            item = formatKYCItem(QTableWidgetItem(str(row[4])))
            self.setItem(numrow, 6, item)
            # Description
            self.setItem(numrow, 7, QTableWidgetItem(str(row[5])))

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)


class HistoricalBalancesTable(QTableWidget):
    """
    Table showing recorded previous balances of accounts and tokens, that changes dynamically.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setRowCount(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setStyleSheet("border:0px")
        self.setSortingEnabled(True)

        self.setMaximumHeight(300)
        self.verticalHeader().hide()

    def updateWithToken(self, token):
        """Only shows entries where token=token"""
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            ['Date', 'Account', 'Balance', 'Balance(BTC)', f"Balance({confighandler.get_fiat_currency().upper()})"])

        rows_to_insert = chistoricalbalances.get_entries_with_token(token)
        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Date
            item = QTableWidgetItem()
            date = datetime.fromtimestamp(row[2]).strftime("%d-%m-%Y")
            item.setData(0, date)
            self.setItem(numrow, 0, item)
            # Account
            item = QTableWidgetItem()
            item.setData(0, row[1])
            self.setItem(numrow, 1, item)
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[4])
            self.setItem(numrow, 2, item)
            # Balance(BTC)
            item = QTableWidgetItem()
            item.setData(0, row[5])
            self.setItem(numrow, 3, item)
            # Balance(fiat)
            item = QTableWidgetItem()
            d = {'eur': 6, 'usd': 7, 'jpy': 8}
            item.setData(0, row[d[confighandler.get_fiat_currency().lower()]])
            self.setItem(numrow, 4, item)

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def updateWithAccount(self, account):
        """Only shows database entries where account=account"""
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            ['Date', 'Token', 'Balance', 'Balance(BTC)', f"Balance({confighandler.get_fiat_currency().upper()})"])

        rows_to_insert = chistoricalbalances.get_entries_with_account(account)
        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Date
            item = QTableWidgetItem()
            date = datetime.fromtimestamp(row[2])
            date = QDate(date.year, date.month, date.day)
            item.setData(0, date)
            self.setItem(numrow, 0, item)
            # Token
            item = QTableWidgetItem()
            item.setData(0, row[3].upper())
            self.setItem(numrow, 1, item)
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[4])
            self.setItem(numrow, 2, item)
            # Balance(BTC)
            item = QTableWidgetItem()
            item.setData(0, row[5])
            self.setItem(numrow, 3, item)
            # Balance(fiat)
            item = QTableWidgetItem()
            d = {'eur': 6, 'usd': 7, 'jpy': 8}
            item.setData(0, row[d[confighandler.get_fiat_currency().lower()]])
            self.setItem(numrow, 4, item)

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def updateWithAll(self):
        """
        Sets the table in 'All mode',
        which shows all entries
        """
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(
            ['Date', 'Account', 'Token', 'Balance', 'Balance(BTC)', f"Balance({confighandler.get_fiat_currency().upper()})"])

        rows_to_insert = chistoricalbalances.get_all_entries()
        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Date
            item = QTableWidgetItem()
            date = datetime.fromtimestamp(row[2])
            date = QDate(date.year, date.month, date.day)
            item.setData(0, date)
            self.setItem(numrow, 0, item)
            # Account
            item = QTableWidgetItem()
            item.setData(0, row[1])
            self.setItem(numrow, 1, item)
            # Token
            item = QTableWidgetItem()
            item.setData(0, row[3].upper())
            self.setItem(numrow, 2, item)
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[4])
            self.setItem(numrow, 3, item)
            # Balance(BTC)
            item = QTableWidgetItem()
            item.setData(0, row[5])
            self.setItem(numrow, 4, item)
            # Balance(fiat)
            item = QTableWidgetItem()
            d = {'eur': 6, 'usd': 7, 'jpy': 8}
            item.setData(0, row[d[confighandler.get_fiat_currency().lower()]])
            self.setItem(numrow, 5, item)

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)


def formatTypeItem(item):
    """Formats 'Type' item according to it's storage method"""
    if item.text() == 'Custodial':
        item.setForeground(QBrush(QColor("red")))
    elif item.text() == 'Cold':
        item.setForeground(QBrush(QColor('green')))
    elif item.text() == 'Hot':
        item.setForeground(QBrush(QColor('yellow')))

    return item


def formatKYCItem(item):
    """Formats 'KYC' item according to it's KYC state"""
    if 'No' in item.text():
        item.setForeground(QBrush(QColor('green')))
    elif 'Yes' in item.text():
        item.setForeground(QBrush(QColor('red')))

    return item


class AccountPieChart(QChartView):
    """
    Chart that displays certaing accounts with their
    respective balance on a Pie Chart.
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.series = QPieSeries()

        self.chart = QChart()
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor('#19232d')))

        self.chart.setTitle("")
        self.chart.setTitleBrush(QBrush(QColor('white')))

        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart.legend().setLabelColor(QColor('white'))

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: 0px")
        # self.setMinimumWidth(300)

    def updateWithToken(self, token):
        """ Updates series with all accounts that have a certain token """
        entries_with_token = cbalances.get_entries_with_token(token)

        self.series.clear()
        for entry in entries_with_token:
            account = entry[0]
            amount = entry[2]
            self.series.append(account, amount)
        self.showSliceLabels(token)

    def allMode(self):
        """Updates series with all accounts"""
        self.series.clear()
        data = cbalances.get_all_accounts_with_amount()

        for d in data:
            account = d[0]
            balance = d[1]
            self.series.append(account, balance)
        self.showSliceLabels("btc")
        self.hideLittleSlices()

    def showSliceLabels(self, token):
        """
        Formats the Slices so that they show the percentage
        """
        for slce in self.series.slices():
            slce.setLabel("{} {}% ({})".format(
                slce.label(), int(100*slce.percentage()), str(prices.to_btc(token, slce.value())) + " BTC"))
            slce.setLabelPosition(QPieSlice.LabelInsideNormal)
            # slce.setLabelPosition(QPieSlice.LabelOutside)
            slce.setLabelColor(QColor('white'))
            slce.setLabelVisible(True)

        self.hideLittleSlices()

    def selectSlice(self, account):
        """
        Explodes a certaing slice that corresponds to
        an account
        """
        for slce in self.series.slices():
            if account in slce.label():
                # Explode slice
                slce.setExploded(True)
                font = QFont()
                font.setBold(True)
                font.setUnderline(True)
                slce.setLabelFont(font)
                slce.setLabelPosition(QPieSlice.LabelOutside)
            else:
                slce.setExploded(False)
                slce.setLabelFont(QFont())
                # slce.setLabelPosition(QPieSlice.LabelInsideTangential)
                slce.setLabelPosition(QPieSlice.LabelInsideNormal)

        self.hideLittleSlices(selected=account)

    def hideLittleSlices(self, selected=''):
        """
        If a slice is not big enough for the label to be properly seen,
        the label gets hidden
        """
        for slce in self.series.slices():
            if slce.angleSpan() < 5 and slce.label().split(' ')[0] != selected:
                # Slice too little to show, and it's not selected
                slce.setLabelVisible(False)
            else:
                slce.setLabelVisible(True)


class TokenPieChart(QChartView):
    """
    Chart that displays certaing tokens with their
    respective balance on a Pie Chart.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.series = QPieSeries()

        self.chart = QChart()
        # self.chart.setTheme(QChart.ChartThemeBrownSand)
        self.chart.setTheme(QChart.ChartThemeQt)
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor('#19232d')))

        self.chart.setTitle("")
        self.chart.setTitleBrush(QBrush(QColor('white')))

        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet('border: 0px')
        # self.setMinimumWidth(300)

    def updateWithAccount(self, account):
        """Changes the series so that only tokens from a certain account are shown"""
        entries_with_account = cbalances.get_entries_with_account(account)

        self.series.clear()
        for entry in entries_with_account:
            token = entry[1].upper()
            amount = entry[2]
            amount_btc = prices.to_btc(token, amount)
            self.series.append(token, amount_btc)
        self.showSliceLabels()

    def allMode(self):
        """Changes the series to show all tokens"""
        self.series.clear()
        data = cbalances.get_all_tokens_with_amount()

        for d in data:
            token = d[0].upper()
            amount = d[1]
            total_in_btc = prices.to_btc(token, amount)
            self.series.append(token, total_in_btc)
        self.showSliceLabels()
        self.hideLittleSlices()

    def showSliceLabels(self):
        """
        Formats the Slices so that they show the percentage
        """
        for slce in self.series.slices():
            slce.setLabel("{} {}% ({})".format(
                slce.label(), int(100*slce.percentage()), str(round(slce.value(), 4)) + " BTC"))
            slce.setLabelPosition(QPieSlice.LabelInsideNormal)
            # slce.setLabelPosition(QPieSlice.LabelOutside)
            slce.setLabelVisible(True)

        self.hideLittleSlices()

    def selectSlice(self, account):
        """
        Explodes a certaing slice that corresponds to
        an account
        """
        for slce in self.series.slices():
            if slce.label().split(' ')[0] == account:
                # Explode slice
                slce.setExploded(True)
                font = QFont()
                font.setBold(True)
                font.setWeight(QFont.ExtraBold)
                font.setUnderline(True)
                slce.setLabelFont(font)
                slce.setLabelColor(QColor("white"))
                slce.setLabelPosition(QPieSlice.LabelOutside)
            else:
                slce.setExploded(False)
                slce.setLabelFont(QFont())
                # # slce.setLabelPosition(QPieSlice.LabelInsideTangential)
                font = QFont()
                slce.setLabelColor(QColor("#3f3f39"))
                slce.setLabelFont(font)
                slce.setLabelPosition(QPieSlice.LabelInsideNormal)

        self.hideLittleSlices(selected=account)

    def hideLittleSlices(self, selected=''):
        """
        If a slice is not big enough for the label to be properly seen,
        the label gets hidden
        """
        for slce in self.series.slices():
            if slce.angleSpan() < 5 and slce.label().split(' ')[0] != selected:
                # Slice too little to show, and it's not selected
                slce.setLabelVisible(False)
            else:
                slce.setLabelVisible(True)


class BalanceHistoryChartView(QChartView):
    """
    Chart that displays the balance between several dates
    from an account, token or whole portfolio
    """

    def __init__(self,  *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.chart = QChart()

    def setupChartWithData(self, selectiontype, name=None):
        """
        Chart gets updated displaying new data.
        The data gets extracted from cbalancehistory, according 
        to the selection

        Parameters:
            - selectiontype : in ('account','token','all')
            - name: str, corresponds to account/token on cbalancehistory

        """
        self.chart = QChart()

        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor('#19232d')))
#         self.chart.setTitle("")
#         self.chart.setTitleBrush(QBrush(QColor('white')))

        # Data
        # Get data
        if selectiontype == 'token':
            assert(name is not None)
            data = chistoricalbalances.get_balances_with_token_tuple(name)
        elif selectiontype == 'account':
            assert(name is not None)
            data = chistoricalbalances.get_balances_with_account_tuple(name)
        elif selectiontype == 'all':
            data = chistoricalbalances.get_balances_by_day_tuple()
        # Separate balance_btc from balance_fiat
        dates, balances_btc, balances_fiat = [], [], []
        for date in data:
            dates.append(int(date))
            balances_btc.append(data[date][0])
            balances_fiat.append(data[date][1])

        # Series
        self.btcseries = QSplineSeries()
        self.fiatseries = QSplineSeries()
        for date, balance_btc, balance_fiat in zip(dates, balances_btc, balances_fiat):
            date = datetime.fromtimestamp(date)
            date = datetime(date.year, date.month, date.day)
            dateQ = QDateTime(date).toMSecsSinceEpoch()
            self.btcseries.append(dateQ, balance_btc)
            self.fiatseries.append(dateQ, balance_fiat)

        # Append current point
        currentdate = QDateTime(datetime.today()).toMSecsSinceEpoch()
        if selectiontype == "all":
            # Append current balances
            self.btcseries.append(currentdate,
                                  cbalances.get_total_balance_all_accounts())
            self.fiatseries.append(currentdate,
                                   cbalances.get_total_balance_all_accounts_fiat())
        elif name != '':
            if selectiontype == "account":
                # Append current balances
                self.btcseries.append(
                    currentdate, cbalances.get_total_account_balance(name))
                self.fiatseries.append(
                    currentdate, cbalances.get_total_account_balance_fiat(name))
            elif selectiontype == "token":
                pass

        # Axis X (Dates)
        self.x_axis = QDateTimeAxis()
        self.x_axis.setTickCount(11)
        self.x_axis.setLabelsAngle(70)
        self.x_axis.setFormat("dd-MM-yy")
        self.x_axis.setTitleText(self.tr('Date'))

        # Axis Y (Balances)
        # BTC
        self.y_axis_btc = QValueAxis()
        if len(balances_btc) > 0:
            self.y_axis_btc.setMax(max(balances_btc)*1.1)
            self.y_axis_btc.setMin(min(balances_btc)*0.9)
        # Fiat
        self.y_axis_fiat = QValueAxis()
        if len(balances_fiat) > 0:
            self.y_axis_fiat.setMax(max(balances_fiat)*1.1)
            self.y_axis_fiat.setMin(min(balances_fiat)*0.9)

        self.chart.addAxis(self.y_axis_btc, Qt.AlignLeft)
        self.chart.addAxis(self.y_axis_fiat, Qt.AlignRight)
        self.chart.addAxis(self.x_axis, Qt.AlignBottom)

        # Add series to chart
        # BTC
        self.btcseries.setName("BTC")
        self.chart.addSeries(self.btcseries)
        self.btcseries.attachAxis(self.x_axis)
        self.btcseries.attachAxis(self.y_axis_btc)
        # Fiat
        self.fiatseries.setName(confighandler.get_fiat_currency().upper())
        self.chart.addSeries(self.fiatseries)
        self.fiatseries.attachAxis(self.x_axis)
        self.fiatseries.attachAxis(self.y_axis_fiat)

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("border: 0px")
