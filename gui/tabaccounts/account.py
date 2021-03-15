# /usr/bin/python3
import os
from gui.assetgen.accounticongen import get_png_account


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

        self.iconpath = os.path.join(
            'resources', 'account-icons', self.account_name + '.png')

        if not os.path.isfile(self.iconpath):
            # Icon didn't exist before, so we generate a new one

            print(''.join(('Creating Icon for ',
                           self.account_name, " on: ", self.iconpath)))
            get_png_account(self.account_name, self.iconpath)

    def __repr__(self):
        return (self.account_name + ' ' + str(self.amount))
