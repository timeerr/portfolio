#!/usr/bin/python3

import os
import configparser

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QMargins, QObject, pyqtSignal

from gui.resources.fonts import TitleFont
from gui import confighandler

CONFIG_FILE_PATH = os.path.join(os.path.expanduser(
    '~'), '.config', 'portfolio', 'config.ini')


class WelcomeWidget(QWidget):
    """
    First window that gets displayed.
    Here the user can add/remove portfolios, and select which one they want to access.
    Once one is selected, it closes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()

        # -----High container------
        self.label = QLabel(self.tr("Welcome"))
        self.label.setMaximumHeight(200)
        self.label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.label.setFont(TitleFont())
        self.layout.addWidget(self.label, alignment=Qt.AlignBottom)

        # -------Low container-------
        self.portoflios_container = QVBoxLayout()
        self.portoflios_container.setAlignment(Qt.AlignBottom)
        self.buttons = []
        self.setupPortfolios()
        self.layout.addLayout(self.portoflios_container)

        self.add_portfolio_bttn = QPushButton(self.tr("Add New Portfolio"))
        self.add_portfolio_bttn.setFixedSize(175, 30)
        self.add_portfolio_bttn.clicked.connect(self.addNewPortfolio)
        self.layout.addWidget(self.add_portfolio_bttn,
                              alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        # Custom Signal
        self.portfolioselected = PortfolioSelected()

    def setupPortfolios(self):
        """
        Displays all the portfolios that the user has added 
        """

        # First, we get all the current portfolio directories
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)

        for portfolioname in config['PORTFOLIODATA PATHS']:
            portfoliopath = config['PORTFOLIODATA PATHS'][portfolioname]

            portfolio_lyt = QHBoxLayout()
            portfolio_lyt.setAlignment(Qt.AlignHCenter)

            portfolio_name = QLabel(portfolioname)
            font = QFont()
            font.setBold(True)
            font.setFamily('Noto Sans')
            portfolio_name.setFont(font)
            portfolio_name.setFixedWidth(120)
            portfolio_lyt.addWidget(portfolio_name)

            portfolio_path = QLabel(portfoliopath)
            portfolio_path.setFixedWidth(300)
            portfolio_lyt.addWidget(portfolio_path)

            go_to_portfolio_bttn = QPushButton(self.tr("Open"))
            go_to_portfolio_bttn.setFixedWidth(100)
            go_to_portfolio_bttn.setStyleSheet("font: bold; font-size:20px")
            go_to_portfolio_bttn.setObjectName(portfoliopath)
            go_to_portfolio_bttn.setCheckable(True)
            self.buttons.append(go_to_portfolio_bttn)

            go_to_portfolio_bttn.toggled.connect(self.goToPortfolio)
            portfolio_lyt.addWidget(go_to_portfolio_bttn)

            self.portoflios_container.addLayout(portfolio_lyt)

    def addPortfolioLyt(self, name, location):
        """
        Displays new portfolio
        """
        portfolio_lyt = QHBoxLayout()
        portfolio_lyt.setAlignment(Qt.AlignHCenter)

        portfolio_name = QLabel(name)
        font = QFont()
        font.setBold(True)
        font.setFamily('Noto Sans')
        portfolio_name.setFont(font)
        portfolio_name.setFixedWidth(120)
        portfolio_lyt.addWidget(portfolio_name)

        portfolio_path = QLabel(location)
        portfolio_path.setFixedWidth(300)
        portfolio_lyt.addWidget(portfolio_path)

        go_to_portfolio_bttn = QPushButton(self.tr("Open"))
        go_to_portfolio_bttn.setFixedWidth(100)
        go_to_portfolio_bttn.setStyleSheet("font: bold; font-size:20px")
        go_to_portfolio_bttn.setObjectName(location)
        go_to_portfolio_bttn.setCheckable(True)
        self.buttons.append(go_to_portfolio_bttn)

        go_to_portfolio_bttn.toggled.connect(self.goToPortfolio)
        portfolio_lyt.addWidget(go_to_portfolio_bttn)

        self.portoflios_container.addLayout(portfolio_lyt)

    def addNewPortfolio(self):
        """
        Opens a Dialog to add a new portfolio, on a new directory
        """
        addportfolio_dlg = AddPortfolioDialog(self)
        addportfolio_dlg.exec_()

    def goToPortfolio(self):
        """
        Changes the program location to the portfolio path, so that when 
        the main app is opened, it takes the data from that directory
        """
        for bttn in self.buttons:
            print(bttn.isChecked())
            if bttn.isChecked() is True:
                path = bttn.objectName()
                os.chdir(path)
                print("changed to ", path)

        from gui.dbhandler import db_initialize
        from gui.cdbhandler import cdb_initialize

        self.portfolioselected.selected.emit()


class AddPortfolioDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()

        # Portfolio Name
        self.portfolioname_lyt = QHBoxLayout()
        self.portfolioname = QLabel("Name")
        self.portfolioname.setMinimumWidth(90)
        self.portfolioname.setAlignment(Qt.AlignLeft)
        self.portfolioname_edit = QLineEdit()
        self.portfolioname_lyt.addWidget(self.portfolioname)
        self.portfolioname_lyt.addWidget(self.portfolioname_edit)
        self.layout.addLayout(self.portfolioname_lyt)

        # Portfolio Location
        self.portfoliolocation_lyt = QHBoxLayout()
        self.portfoliolocation_label = QLabel("Location")
        self.portfoliolocation_label.setMinimumWidth(90)
        self.portfoliolocation_label.setAlignment(Qt.AlignLeft)
        self.portfoliolocation = QLabel("")
        self.portfoliolocation_select = QPushButton("Select")
        self.portfoliolocation_select.clicked.connect(
            self.openLocationSelectionDialog)
        self.portfoliolocation_lyt.addWidget(self.portfoliolocation_label)
        self.portfoliolocation_lyt.addWidget(self.portfoliolocation)
        self.portfoliolocation_lyt.addWidget(self.portfoliolocation_select)
        self.layout.addLayout(self.portfoliolocation_lyt)

        # Add button
        self.add_portfolio_bttn = QPushButton("Add New Portfolio")
        self.add_portfolio_bttn.clicked.connect(self.addNewPortfolio)
        self.layout.addWidget(self.add_portfolio_bttn)

        self.setLayout(self.layout)

        # Data
        self.current_newlocation = ''

    def setPortolioLocation(self, newlocation):
        self.portfoliolocation.setText(newlocation)

    def openLocationSelectionDialog(self):
        """
        Displays a Dialog to select a directory for the new portfolio
        """
        self.location_select_dialog = QFileDialog()
        self.location_select_dialog.setFileMode(
            QFileDialog.FileMode.DirectoryOnly)

        self.location_select_dialog.fileSelected.connect(
            self.setPortolioLocation)

        self.location_select_dialog.exec_()

    def addNewPortfolio(self):
        """
        Adds new portfolio info on config.ini file,
        and displays the new portfolio on the welcomewidget
        """
        name = self.portfolioname_edit.text()
        location = self.portfoliolocation.text()

        confighandler.add_portfolio(name, location)
        self.parent().addPortfolioLyt(name, location)

        self.close()


class PortfolioSelected(QObject):
    selected = pyqtSignal()
