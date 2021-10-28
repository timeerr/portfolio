#!/usr/bin/python3

import os
import configparser

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QMargins, QObject, pyqtSignal

from portfolio.gui.ui_components.fonts import SuperTitleFont, DescriptionFont
from portfolio.utils import confighandler


class WelcomeWidget(QWidget):
    """
    First window that gets displayed.
    Here the user can add/remove portfolios, and select which one they want to access.
    Once one is selected, it closes.
    """
    portfolioselected = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        # -----High container------
        wrapper_lyt = QVBoxLayout()
        wrapper_lyt.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        wrapper_lyt.setSpacing(0)

        self.title = QLabel(self.tr("Welcome"))
        self.title.setMaximumHeight(200)
        self.title.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.title.setFont(SuperTitleFont())
        wrapper_lyt.addWidget(self.title, alignment=Qt.AlignBottom)

        self.subtitle = QLabel(
            self.tr("Select to open a portfolio, or create a new one"))
        self.subtitle.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.subtitle.setFont(DescriptionFont())
        wrapper_lyt.addWidget(self.subtitle, alignment=Qt.AlignBottom)

        self.layout.addLayout(wrapper_lyt)

        # -------Low container-------
        self.portfolios_container = QVBoxLayout()
        self.portfolios_container.setAlignment(Qt.AlignBottom)
        self.buttons = []
        self.setup_portfolios()
        self.layout.addLayout(self.portfolios_container)

        self.add_portfolio_bttn = QPushButton(self.tr("Add Portfolio"))
        self.add_portfolio_bttn.setStyleSheet("font: bold; font-size:15px")
        self.add_portfolio_bttn.setFixedSize(175, 30)
        self.add_portfolio_bttn.clicked.connect(self.openAddPortfolioDialog)
        self.layout.addWidget(self.add_portfolio_bttn,
                              alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

    def setup_portfolios(self):
        """ Displays all the portfolios that the user has added """
        # First, we get all the current portfolio directories
        portfolios = confighandler.get_portfolios()
        # Iterate and populate
        for name in portfolios:
            path = portfolios[name]
            self.addPortfolioLyt(name, path)

    def addPortfolioLyt(self, name: str, path: str):
        """ Displays new portfolio """
        db_version = confighandler.get_database_version(path)

        portfolio_lyt = QHBoxLayout()
        portfolio_lyt.setAlignment(Qt.AlignHCenter)

        open_portfolio_bttn = QPushButton(name)
        open_portfolio_bttn.setFixedWidth(100)
        open_portfolio_bttn.setStyleSheet("font: bold; font-size:20px")
        open_portfolio_bttn.setObjectName(path+";"+name)
        open_portfolio_bttn.setCheckable(True)
        open_portfolio_bttn.toggled.connect(self.goToPortfolio)
        self.buttons.append(open_portfolio_bttn)
        portfolio_lyt.addWidget(open_portfolio_bttn)

        portfolio_path_label = QLabel(path)
        font = QFont()
        font.setWeight(QFont.Light)
        portfolio_path_label.setFont(font)
        portfolio_path_label.setFixedWidth(500)
        portfolio_lyt.addWidget(portfolio_path_label)

        portfolio_version_label = QLabel(db_version)
        portfolio_version_label.setFixedWidth(50)
        portfolio_lyt.addWidget(portfolio_version_label)

        # If the database has a version that is superior to the one
        # on the app, hide open button
        if db_version == "Missing":
            open_portfolio_bttn.setStyleSheet(
                "font:bold; font-size:20px;background-color:grey")
            open_portfolio_bttn.setCheckable(False)
        elif db_version > confighandler.get_version():
            open_portfolio_bttn.hide()
            portfolio_lyt.addWidget(QLabel(self.tr("Update App First")))

        self.portfolios_container.addLayout(portfolio_lyt)

    def openAddPortfolioDialog(self):
        """ Opens a Dialog to add a new portfolio, on a new directory """
        addportfolio_dlg = AddPortfolioDialog(self)
        addportfolio_dlg.exec_()

    def goToPortfolio(self):
        """
        Changes the program location to the portfolio path, so that when
        the main app is opened, it takes the data from that directory
        """
        for bttn in self.buttons:
            if bttn.isChecked() is True:
                path = bttn.objectName().split(";")[0]
                name = bttn.objectName().split(";")[1]
                os.chdir(path)  # Change location to portfolio
        # Emit open portfolio signal
        self.portfolioselected.emit(name)


class AddPortfolioDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- UI ----
        self.setWindowTitle(self.tr("Add New Portfolio"))

        # ---- Content ----
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

    def setPortolioLocation(self, newlocation):
        self.portfoliolocation.setText(newlocation)

    def openLocationSelectionDialog(self):
        """ Displays a Dialog to select a directory for the new portfolio """
        location_select_dialog = QFileDialog()
        location_select_dialog.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        location_select_dialog.fileSelected.connect(self.setPortolioLocation)
        location_select_dialog.exec_()

    def addNewPortfolio(self):
        """ Creates new portfolio data and UI entry """
        name, location = self.portfolioname_edit.text(), self.portfoliolocation.text()
        confighandler.add_portfolio(name, location)  # Data
        self.parent().addPortfolioLyt(name, location)  # UI
        self.close()
