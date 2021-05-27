#!/usr/bin/python3

from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QMargins, QDate

from portfolio.gui.ui_components.fonts import TitleFont, SubtitleFont, DateButtonFont, UpdateButtonFont
from portfolio.gui.tabtransactions.tabtransactions_formquery import TransactionsQueryForm
from portfolio.gui.tabtransactions.tabtransactions_addtransactionsform import AddTransactionsForm


class LeftLayout(QVBoxLayout):
    """
    Layout containing forms to interact with the table on the right
    layout of tabtransactions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Title
        title = QLabel(self.tr("Transactions"))
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(50)
        title.setFont(TitleFont())
        self.addWidget(title)

        # Subtitle
        subtitle = QLabel(self.tr("Parameters"))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setMaximumHeight(50)
        subtitle.setFont(SubtitleFont())
        self.addWidget(subtitle)

        # Form
        self.form = TransactionsQueryForm()
        self.addLayout(self.form)

        # Date shortcut buttons
        self.date_shorcut_buttons_layout = QHBoxLayout()

        self.current_week_button = QPushButton(self.tr("Current Week"))
        self.current_week_button.clicked.connect(self.set_currentweek)
        self.date_shorcut_buttons_layout.addWidget(self.current_week_button)

        self.mtd_button = QPushButton(self.tr("Current Month"))
        self.mtd_button.clicked.connect(self.set_mtd)
        self.date_shorcut_buttons_layout.addWidget(self.mtd_button)

        self.ytd_button = QPushButton(self.tr("Current Year"))
        self.ytd_button.clicked.connect(self.set_ytd)
        self.date_shorcut_buttons_layout.addWidget(self.ytd_button)

        self.all_button = QPushButton(self.tr("All"))
        self.all_button.clicked.connect(self.set_all)
        self.date_shorcut_buttons_layout.addWidget(self.all_button)

        self.addLayout(self.date_shorcut_buttons_layout)

        # Button
        self.update_query_pushbutton = QPushButton(self.tr("Update"))
        self.update_query_pushbutton.setFont(DateButtonFont())
        self.update_query_pushbutton.setFont(UpdateButtonFont())
        self.update_query_pushbutton.setMinimumHeight(30)
        self.update_query_pushbutton.setMaximumWidth(75)
        # Wrap the pushbutton inside a layout, that gets inserted into our
        # main leftlayout, so that we can center it properly
        self.update_query_pushbutton_layout = QVBoxLayout()
        self.update_query_pushbutton_layout.addWidget(
            self.update_query_pushbutton, Qt.AlignVCenter)
        self.update_query_pushbutton_layout.setAlignment(
            Qt.AlignHCenter | Qt.AlignTop)  # Centering it
        self.update_query_pushbutton_layout.setContentsMargins(
            QMargins(10, 10, 10, 10))  # A little bit of margin
        self.addLayout(self.update_query_pushbutton_layout)

        # Add results form
        self.add_transactions_form = AddTransactionsForm()
        self.add_transactions_form.setAlignment(Qt.AlignTop)

        self.addLayout(self.add_transactions_form)

    def set_currentweek(self):
        dayofweek = QDate.currentDate().dayOfWeek()

        # We will have to substract this number of days to the current date,
        # and set that date on the startdate slot
        days_to_prev_monday = -(dayofweek+6)

        self.form.start_date_edit.setDate(
            QDate(QDate.currentDate().addDays(days_to_prev_monday)))
        self.update_query_pushbutton.click()

    def set_mtd(self):
        """Month to Date"""
        days_to_first_day_of_month = -(QDate.currentDate().day()-1)

        self.form.start_date_edit.setDate(
            QDate.currentDate().addDays(days_to_first_day_of_month))
        self.update_query_pushbutton.click()

    def set_ytd(self):
        """Year to Date"""
        self.form.start_date_edit.setDate(
            QDate(QDate.currentDate().year(), 1, 1))
        self.update_query_pushbutton.click()

    def set_all(self):
        self.form.start_date_edit.setDate(QDate(1900, 1, 1))
        self.form.end_date_edit.setDate(QDate.currentDate())
        self.update_query_pushbutton.click()
