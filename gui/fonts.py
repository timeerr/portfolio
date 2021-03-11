#!/usr/bin/python3

from PyQt5.QtGui import QFont


class TitleFont(QFont):

    def __init__(self):
        super().__init__()

        self.setPointSize(45)
        self.setBold(True)


class SubtitleFont(QFont):

    def __init__(self):
        super().__init__()

        self.setPointSize(18)
        self.setBold(True)
        self.setItalic(True)


class BoldFont(QFont):

    def __init__(self):
        super().__init__()

        self.setBold(True)


class DateButtonFont(QFont):

    def __init__(self):
        super().__init__()

        self.setPointSize(8)


class UpdateButtonFont(QFont):

    def __init__(self):
        super().__init__()

        self.setBold(True)


class AccountBalanceHeaderFont(QFont):

    def __init__(self):
        super().__init__()

        self.setFamily("Roboto")
        self.setPointSize(11)
        self.setItalic(True)


class AccountBalanceTextFont(QFont):

    def __init__(self):
        super().__init__()

        self.setFamily("Noto Sans")
        self.setPointSize(40)


class TokenBalanceFont(QFont):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFamily("Roboto")
        self.setPointSize(20)
