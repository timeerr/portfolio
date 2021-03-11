#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QComboBox, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView, QDialog, QDoubleSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap, QIcon

from cdbhandler import cbalances
from fonts import TitleFont, TokenBalanceFont
from prices import prices
from tabcrypto.tabcrypto_toolbar import TabCryptoToolBar

import requests
import json
import os

FIAT_CURRENCY = "EUR"
DATABASE_TOKENS = cbalances.getAllTokens()
DATABASE_ACCOUNTS = cbalances.getAllAccounts()


# Checking if there is remote data avaliable
if 'coingeckoids.json' not in os.listdir('prices'):
    prices.updateCoinListFile()
if 'coinprices.json' not in os.listdir('prices'):
    open('coinprices.json', 'w').close()
    for token in DATABASE_TOKENS:
        prices.addTokenPrice(token, 'coingecko', 0)
if 'btctofiat.json' not in os.listdir('prices'):
    prices.updateBTCToFiat()


class TabCrypto(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Crypto")

        # UI
        self.mainlayout = QVBoxLayout()
        self.upperlayout = QHBoxLayout()
        self.lowerlayout = QHBoxLayout()

        # Token Description
        self.description = DescriptionLayout(self)
        self.upperlayout.addWidget(self.description)

        # Token transactions
        self.tokenbalances = TokenBalancesLayout(self)
        self.upperlayout.addWidget(self.tokenbalances)

        # Data entries
        self.toolbar = TabCryptoToolBar(self)

        # Pie Charts
        self.accountpiechart = AccountPieChart(self)
        self.tokenpiechart = TokenPieChart(self)
        self.lowerlayout.addWidget(self.tokenpiechart)
        self.lowerlayout.addWidget(self.accountpiechart)

        # Functionality
        # When the select_mode button is clicked, we swith between modes
        self.description.select_mode.clicked.connect(self.updateSelectMode)
        # When a new selection is made, we update al info
        self.description.select_token_or_account.currentTextChanged.connect(
            self.selectionChanged)
        # When prices data is updated, we refresh everything
        self.description.updatedata.clicked.connect(
            lambda: self.selectionChanged(self.description.select_token_or_account.currentText()))

        self.mainlayout.addWidget(self.toolbar)
        self.mainlayout.addLayout(self.upperlayout)
        self.mainlayout.addLayout(self.lowerlayout)
        self.setLayout(self.mainlayout)

        # Initialize with "All"
        self.selectionChanged("All")

    def selectionChanged(self, selection):
        if self.description.mode == 0:
            # All mode
            print("Selection changed to ", selection)
            self.tokenbalances.updateWithAll()
            self.description.allMode()
            self.accountpiechart.allMode()
            self.tokenpiechart.allMode()

        elif self.description.mode == 1:
            # Token mode
            print("Token changed to ", selection)
            self.tokenbalances.updateWithToken(selection)
            self.accountpiechart.updateWithToken(selection)
            self.tokenpiechart.selectSlice(selection)
            self.description.tokenChanged(selection)

        elif self.description.mode == 2:
            print("Account changed to ", selection)
            # Account mode
            self.tokenbalances.updateWithAccount(selection)
            self.tokenpiechart.updateWithAccount(selection)
            self.accountpiechart.selectSlice(selection)
            self.description.accountChanged(selection)

    def updateSelectMode(self):
        """ Switches between three states: all, token, or account selection """
        self.description.mode += 1
        self.description.mode = self.description.mode % 3
        if self.description.mode == 0:
            # All mode
            self.description.select_mode.setText("All")
            self.description.select_token_or_account.clear()
            self.description.select_token_or_account.addItem("All")
        elif self.description.mode == 1:
            # Token mode
            self.description.select_mode.setText("Token")
            self.description.select_token_or_account.clear()
            DATABASE_TOKENS = cbalances.getAllTokens()
            self.description.select_token_or_account.addItems(DATABASE_TOKENS)
            self.tokenpiechart.allMode()
        elif self.description.mode == 2:
            # Account mode
            self.description.select_mode.setText("Account")
            self.description.select_token_or_account.clear()
            DATABASE_ACCOUNTS = cbalances.getAllAccounts()
            self.description.select_token_or_account.addItems(
                DATABASE_ACCOUNTS)
            self.accountpiechart.allMode()


class DescriptionLayout(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.setFixedWidth(600)

        # Token Selection
        self.select_token_or_account_lyt = QHBoxLayout()
        self.select_token_or_account = QComboBox()
        self.select_token_or_account.addItem("All")
        #   Button to update coinlist info file
        self.updatedata = QPushButton("Update Prices")
        self.updatedata.setMaximumWidth(100)
        self.updatedata.clicked.connect(
            self.updateDataFiles)
        # Button to change selection mode between accounts or tokens
        self.select_mode = QPushButton("All")
        self.select_mode.setMaximumWidth(150)
        self.select_mode.setIcon(
            QIcon(QPixmap(os.path.join('resources', 'switch.svg'))))

        self.select_token_or_account_lyt.addWidget(
            self.select_token_or_account)
        self.select_token_or_account_lyt.addWidget(self.select_mode)
        self.select_token_or_account_lyt.addWidget(self.updatedata)

        # Token/Accout Name Label
        self.token_or_account_name = QLabel("All Coins")
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

    def allMode(self):
        # If 'All' is selected, we show the full balance of all tokens in all accounts
        self.token_or_account_name.setText("All Coins")
        totalbalancebtc, totalbalancefiat = 0, 0
        DATABASE_TOKENS = cbalances.getAllTokens()
        for t in DATABASE_TOKENS:
            tokenbalance = cbalances.getTotalTokenBalance(t)
            tokenbalance_btc = prices.toBTC(t, tokenbalance)
            totalbalancebtc += tokenbalance_btc
            totalbalancefiat += prices.btcToFiat(
                tokenbalance_btc, currency=FIAT_CURRENCY)
        self.token_or_account_balance.hide()
        self.token_or_account_balance_btc.setText(
            str(round(totalbalancebtc, 8))+" BTC")
        self.token_or_account_balance_fiat.setText(
            str(round(totalbalancefiat, 2))+" " + FIAT_CURRENCY)

    def tokenChanged(self, tokensymbol):
        # If a Token is selected, we show the total amount of it on all accounts
        # Getting token id from coingecko's list
        if tokensymbol != '':
            try:
                token_name = prices.getId(tokensymbol)
            except:
                # Not in Coingecko's list
                token_name = tokensymbol
        else:
            return

        # Updating token info
        self.token_or_account_name.setText(
            token_name[0].upper()+token_name[1:])

        # Updating token balances
        tokenbalance = cbalances.getTotalTokenBalance(tokensymbol)
        self.token_or_account_balance.setText(
            str(tokenbalance)+' '+tokensymbol)
        self.token_or_account_balance.show()
        tokenbalancebtc = prices.toBTC(tokensymbol, tokenbalance)
        self.token_or_account_balance_btc.setText(str(tokenbalancebtc)+" BTC")
        if tokensymbol in ["BTC", "btc"]:
            self.token_or_account_balance_btc.setText("")
        tokenbalancefiat = prices.btcToFiat(tokenbalancebtc)
        self.token_or_account_balance_fiat.setText(
            str(tokenbalancefiat) + " {}".format(FIAT_CURRENCY.upper()))

    def accountChanged(self, accountname):
        # If an account is selected, we show the total amount of all of its tokens

        # Updating account name
        self.token_or_account_name.setText(accountname)

        # Updating account balances
        acc_token_balances = cbalances.getEntriesWithAccount(accountname)
        total_in_btc = 0
        for atb in acc_token_balances:
            token = atb[1]
            amount = atb[2]
            amount_btc = prices.toBTC(token, amount)
            total_in_btc += amount_btc
        total_in_fiat = prices.btcToFiat(
            total_in_btc, currency=FIAT_CURRENCY)

        self.token_or_account_balance.hide()  # Not useful here
        self.token_or_account_balance_btc.setText(str(total_in_btc) + " BTC")
        self.token_or_account_balance_fiat.setText(
            str(total_in_fiat) + " " + FIAT_CURRENCY.upper())

    def updateDataFiles(self):
        """Calls coingecko's API and writes btcfiat.json, coinlist.json, coinprices.json"""
        self.parent().parent().parent().parent().parent(
        ).statusbar.showMessage("Updating data...")
        DATABASE_TOKENS = cbalances.getAllTokens()
        prices.updateCoingeckoPrices()
        prices.updateCoinListFile()
        prices.updateBTCToFiat()
        self.parent().parent().parent().parent().parent(
        ).statusbar.showMessage("Data Updated!")


class TokenBalancesLayout(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setRowCount(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Not editable
        self.setStyleSheet("border: 0px")

        self.setHorizontalHeaderLabels(
            ['Account', 'Balance', 'Type', 'KYC', 'Description'])
        self.setSortingEnabled(True)

        self.setMaximumHeight(300)
        # self.setMaximumWidth(600)
        self.setMinimumWidth(600)
        self.verticalHeader().hide()

    def updateWithToken(self, token):
        """Only shows database entries where token=token"""
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            ['Account', 'Balance ({})'.format(token), 'Type', 'KYC', 'Description'])
        rows_to_insert = cbalances.getEntriesWithToken(token)

        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Account
            self.setItem(numrow, 0, QTableWidgetItem(row[0]))
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[2])
            self.setItem(numrow, 1, item)
            # Type
            item = self.formatTypeItem(QTableWidgetItem(str(row[3])))
            self.setItem(numrow, 2, item)
            # KYC
            item = self.formatKYCItem(QTableWidgetItem(str(row[4])))
            self.setItem(numrow, 3, item)
            # Description
            self.setItem(numrow, 4, QTableWidgetItem(str(row[5])))

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def updateWithAccount(self, account):
        """Only shows database entries where account=account"""
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            ['Token', 'Balance', 'Type', 'KYC', 'Description'])

        rows_to_insert = cbalances.getEntriesWithAccount(account)
        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Token
            self.setItem(numrow, 0, QTableWidgetItem(row[1]))
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[2])
            self.setItem(numrow, 1, item)
            # Type
            item = self.formatTypeItem(QTableWidgetItem(str(row[3])))
            self.setItem(numrow, 2, item)
            # KYC
            item = self.formatKYCItem(QTableWidgetItem(str(row[4])))
            self.setItem(numrow, 3, item)
            # Description
            self.setItem(numrow, 4, QTableWidgetItem(str(row[5])))

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def updateWithAll(self):
        self.setSortingEnabled(False)
        self.clear()
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            ['Account', 'Token', 'Balance', 'Balance(BTC)', 'Balance({})'.format(FIAT_CURRENCY), 'Type', 'KYC', 'Description'])
        rows_to_insert = cbalances.getAllEntries()

        self.setRowCount(len(rows_to_insert))
        for numrow, row in enumerate(rows_to_insert):
            # Account
            self.setItem(numrow, 0, QTableWidgetItem(row[0]))
            # Token
            self.setItem(numrow, 1, QTableWidgetItem(row[1]))
            # Balance
            item = QTableWidgetItem()
            item.setData(0, row[2])
            self.setItem(numrow, 2, item)
            # Balance(BTC)
            balance_in_btc = prices.toBTC(row[1], row[2])
            item = QTableWidgetItem()
            item.setData(0, balance_in_btc)
            self.setItem(numrow, 3, item)
            # Balance (Fiat)
            balance_in_fiat = prices.btcToFiat(
                balance_in_btc, currency=FIAT_CURRENCY)
            item = QTableWidgetItem()
            item.setData(0, balance_in_fiat)
            self.setItem(numrow, 4, item)
            # Type
            item = self.formatTypeItem(QTableWidgetItem(str(row[3])))
            self.setItem(numrow, 5, item)
            # KYC
            item = self.formatKYCItem(QTableWidgetItem(str(row[4])))
            self.setItem(numrow, 6, item)
            # Description
            self.setItem(numrow, 7, QTableWidgetItem(str(row[5])))

        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

    def formatTypeItem(self, item):
        """Formats 'Type' item according to it's storage method"""
        if item.text() == 'Custodial':
            item.setForeground(QBrush(QColor("red")))
        elif item.text() == 'Cold':
            item.setForeground(QBrush(QColor('green')))
        elif item.text() == 'Hot':
            item.setForeground(QBrush(QColor('yellow')))

        return item

    def formatKYCItem(self, item):
        """Formats 'KYC' item according to it's KYC state"""
        if 'No' in item.text():
            item.setForeground(QBrush(QColor('green')))
        elif 'Yes' in item.text():
            item.setForeground(QBrush(QColor('red')))

        return item


class AccountPieChart(QChartView):
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

    def updateWithToken(self, token):
        """ Updates series with all accounts that have a certain token """
        entries_with_token = cbalances.getEntriesWithToken(token)

        self.series.clear()
        for entry in entries_with_token:
            account = entry[0]
            amount = entry[2]
            self.series.append(account, amount)
        self.showSliceLabels()

    def allMode(self):
        """Updates series with all accounts"""
        self.series.clear()
        data = cbalances.getAllAccountsWithAmount()

        for d in data:
            account = d[0]
            balance = d[1]
            self.series.append(account, balance)
        self.showSliceLabels()

    def showSliceLabels(self):
        for slice in self.series.slices():
            slice.setLabel("{} {}% ({})".format(
                slice.label(), int(100*slice.percentage()), str(slice.value()) + " BTC"))
            slice.setLabelPosition(QPieSlice.LabelInsideNormal)
            # slice.setLabelPosition(QPieSlice.LabelOutside)
            slice.setLabelColor(QColor('white'))
            slice.setLabelVisible(True)

    def selectSlice(self, account):
        for slice in self.series.slices():
            if slice.label().split(' ')[0] == account:
                # Explode slice
                slice.setExploded(True)
                font = QFont()
                font.setBold(True)
                font.setUnderline(True)
                slice.setLabelFont(font)
                slice.setLabelPosition(QPieSlice.LabelOutside)
            else:
                slice.setExploded(False)
                slice.setLabelFont(QFont())
                # slice.setLabelPosition(QPieSlice.LabelInsideTangential)
                slice.setLabelPosition(QPieSlice.LabelInsideNormal)


class TokenPieChart(QChartView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.series = QPieSeries()

        self.chart = QChart()
        self.chart.setTheme(QChart.ChartThemeBrownSand)
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor('#19232d')))

        self.chart.setTitle("")
        self.chart.setTitleBrush(QBrush(QColor('white')))

        self.chart.legend().setAlignment(Qt.AlignBottom)
        # chart.legend().setLabelColor(QColor('white'))

        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet('border: 0px')
        self.setMinimumWidth(300)

    def updateWithAccount(self, account):
        """Changes the series so that only tokens from a certain account are shown"""
        entries_with_account = cbalances.getEntriesWithAccount(account)

        self.series.clear()
        for entry in entries_with_account:
            token = entry[1]
            amount = entry[2]
            amount_btc = prices.toBTC(token, amount)
            self.series.append(token, amount_btc)
        self.showSliceLabels()

    def allMode(self):
        """Changes the series to show all tokens"""
        self.series.clear()
        data = cbalances.getAllTokensWithAmount()

        for d in data:
            token = d[0]
            amount = d[1]
            total_in_btc = prices.toBTC(token, amount)
            self.series.append(token, total_in_btc)
        self.showSliceLabels()

    def showSliceLabels(self):
        for slice in self.series.slices():
            slice.setLabel("{} {}% ({})".format(
                slice.label(), int(100*slice.percentage()), str(slice.value()) + " BTC"))
            slice.setLabelPosition(QPieSlice.LabelInsideNormal)
            # slice.setLabelPosition(QPieSlice.LabelOutside)
            slice.setLabelColor(QColor('white'))
            slice.setLabelVisible(True)

    def selectSlice(self, account):
        for slice in self.series.slices():
            if slice.label().split(' ')[0] == account:
                # Explode slice
                slice.setExploded(True)
                font = QFont()
                font.setBold(True)
                font.setUnderline(True)
                slice.setLabelFont(font)
                slice.setLabelPosition(QPieSlice.LabelOutside)
            else:
                slice.setExploded(False)
                slice.setLabelFont(QFont())
                # slice.setLabelPosition(QPieSlice.LabelInsideTangential)
                slice.setLabelPosition(QPieSlice.LabelInsideNormal)
