#!/usr/bin/python3

from PyQt5.QtGui import QFont


class BoldFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBold(True)


class LightFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWeight(25)


class SuperTitleFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPointSize(80)
        self.setBold(True)


class TitleFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPointSize(40)
        self.setBold(True)


class DescriptionFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPointSize(14)
        self.setWeight(QFont.Light)


class SubtitleFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPointSize(18)
        self.setBold(True)
        self.setItalic(True)


class DateButtonFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPointSize(8)


class UpdateButtonFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBold(True)


class AccountBalanceHeaderFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFamily("Roboto")
        self.setPointSize(11)
        self.setItalic(True)


class AccountBalanceTextFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFamily("Noto Sans")
        self.setPointSize(40)


class TokenBalanceFont(QFont):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFamily("Roboto")
        self.setPointSize(20)


class ChartTitleFont(QFont):
    def __init__(self, * args, fontsize=10, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFamily('Roboto')
        self.setPointSize(fontsize)
        self.setBold(True)


class PreferencesLabelFont(QFont):
    def __init__(self, * args, fontsize=10, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFamily('Roboto')
        self.setBold(True)
        self.setPointSize(34)


class PreferencesButtonFont(QFont):
    def __init__(self, * args, fontsize=10, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFamily('Roboto')
        self.setBold(True)
        self.setPointSize(24)
