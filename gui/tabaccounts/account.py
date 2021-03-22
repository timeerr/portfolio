# /usr/bin/python3
"""
Object that contains data about a new account.
"""

import os
from gui.assetgen.accounticongen import get_png_account

RESOURCES_PATH = os.path.join(os.path.expanduser(
    '~'), '.local', 'share', 'portfolio')


class Account:

    def __init__(self, account_name, starting_amount=0):

        new_account_name = ""
        if "/" in account_name:
            for letter in account_name:
                if letter == "/":
                    new_account_name += "-"
                else:
                    new_account_name += letter
            self.account_name = new_account_name
            print(new_account_name)
        else:
            self.account_name = account_name
        self.amount = starting_amount

        if 'account-icons' not in os.listdir(RESOURCES_PATH):
            os.mkdir(os.path.join(RESOURCES_PATH, 'account-icons'))
        self.iconpath = os.path.join(
            RESOURCES_PATH, 'account-icons', self.account_name + '.png')

        if not os.path.isfile(self.iconpath):
            # Icon didn't exist before, so we generate a new one

            print(''.join(('Creating Icon for ',
                           self.account_name, " on: ", self.iconpath)))
            get_png_account(self.account_name, self.iconpath)

    def __repr__(self):
        return self.account_name + ' ' + str(self.amount)
