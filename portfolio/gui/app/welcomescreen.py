#!/usr/bin/python3

import os
import configparser

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog
from PyQt5.QtWidgets import QCheckBox, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QMargins, QObject, pyqtSignal

from portfolio.gui.ui_components.widgets.buttons import OpenPortfolioButton, DeletePortfolioButton
from portfolio.gui.ui_components.fonts import SuperTitleFont, DescriptionFont, LightFont, BoldFont
from portfolio.utils import confighandler
from portfolio import logger


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
        self.layouts_tracker = {}
        self.portfolios_container = QVBoxLayout()
        self.portfolios_container.setAlignment(Qt.AlignBottom)
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
        portfolio_lyt = QHBoxLayout()
        portfolio_lyt.setAlignment(Qt.AlignHCenter)

        bttn = OpenPortfolioButton(name, path)
        bttn.toggled.connect(lambda: self.goToPortfolio(bttn))
        portfolio_lyt.addWidget(bttn)

        portfolio_path_label = QLabel(path)
        portfolio_path_label.setFont(LightFont())
        portfolio_path_label.setFixedWidth(500)
        portfolio_lyt.addWidget(portfolio_path_label)

        db_version = confighandler.get_database_version(path)
        portfolio_version_label = QLabel(db_version)
        portfolio_version_label.setFixedWidth(60)
        portfolio_lyt.addWidget(portfolio_version_label)

        del_bttn = DeletePortfolioButton(name, path)

        del_bttn.clicked.connect(
            lambda: self.openDeletePortfolioDialog(name))
        del_bttn.deleted.connect(lambda: self.deletePortfolioLyt(name))
        portfolio_lyt.addWidget(del_bttn)

        self.layouts_tracker[name] = (
            bttn, portfolio_path_label, portfolio_version_label, del_bttn)
        # If the database has a version that is superior to the one
        # on the app, hide open button
        if db_version == "Missing":
            bttn.set_unfunctional()
        elif db_version > confighandler.get_version():
            label = QLabel(self.tr("Update App First"))
            portfolio_lyt.addWidget(label)
            self.layouts_tracker[name].append(label)

        self.portfolios_container.addLayout(portfolio_lyt)

    def deletePortfolioLyt(self, name: str):
        logger.info(f"Deleting portfolio entry for {name}")
        confighandler.delete_portfolio_entry(name)
        for w in self.layouts_tracker[name]:
            w.deleteLater()
        # Delete entry

    def deletePortfolioData(self, path: str):
        logger.info(
            f"Deleting portfolio data for {path}")
        # Delete entry
        confighandler.delete_portfolio_data(path)

    def openAddPortfolioDialog(self):
        """ Opens a Dialog to add a new portfolio, on a new directory """
        AddPortfolioDialog(self).exec_()

    def openDeletePortfolioDialog(self, name):
        """ Opens a Dialog to delete a new portfolio """
        path = confighandler.get_portfolio_path(name)
        dlg = DeletePortfolioDialog(self)
        dlg.delete.connect(lambda: self.deletePortfolioLyt(name))
        dlg.delete_files.connect(lambda: self.deletePortfolioData(path))
        dlg.exec_()

    def goToPortfolio(self, bttn: OpenPortfolioButton):
        os.chdir(bttn.path)  # Change location to portfolio
        self.portfolioselected.emit(bttn.name)


class DeletePortfolioDialog(QDialog):
    delete = pyqtSignal()
    delete_files = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- UI ----
        self.setWindowTitle(self.tr("Add New Portfolio"))
        self.setMaximumSize(300, 100)

        # ---- Content ----
        self.layout = QVBoxLayout()

        # Message
        self.label = QLabel(
            self.tr("Are you sure you want to delete this portfolio?"))
        self.label.setFont(BoldFont())
        self.layout.addWidget(self.label)

        # Delete files checkbox
        self.delete_files_checkbox = QCheckBox(self.tr("Also delete files"))
        self.layout.addWidget(self.delete_files_checkbox)

        # Options
        self.options_lyt = QHBoxLayout()
        self.ok = QPushButton(self.tr("OK"))
        self.cancel = QPushButton(self.tr("Cancel"))
        self.options_lyt.addWidget(self.ok)
        self.options_lyt.addWidget(self.cancel)
        self.layout.addLayout(self.options_lyt)

        self.setLayout(self.layout)

        # Functionality
        self.cancel.clicked.connect(self.close)
        self.ok.clicked.connect(self.sendDeleteSignal)

    def sendDeleteSignal(self):
        self.delete.emit()
        if self.delete_files_checkbox.isChecked():
            self.delete_files.emit()
        self.close()


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

    def openLocationSelectionDialog(self):
        """ Displays a Dialog to select a directory for the new portfolio """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.DirectoryOnly)
        dlg.fileSelected.connect(self.portfoliolocation.setText)
        dlg.exec_()

    def addNewPortfolio(self):
        """ Creates new portfolio data and UI entry """
        name, location = self.portfolioname_edit.text(), self.portfoliolocation.text()
        confighandler.add_portfolio(name, location)  # Data
        self.parent().addPortfolioLyt(name, location)  # UI
        self.close()
