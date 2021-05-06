"""
Handles all the input and output operations that use the cbalances table from cportfolio.db
"""
#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime

import sqlite3
import os

from gui.prices import prices
from gui import confighandler


PATH_TO_DB = os.path.join('database', 'cportfolio.db')


def create_connection(path_to_db=PATH_TO_DB):
    """Connects to the database on a certain path, returning the connection"""
    conn = None

    try:
        conn = sqlite3.connect(path_to_db)
    except sqlite3.OperationalError as e:
        print(e, path_to_db)

    return conn


def addAccount(account, token, amount, _type, kyc, description):
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        add_account_query = """INSERT INTO 'cbalances'
            ('account','token','amount','type','kyc','description')
            VALUES (?,?,?,?,?,?);"""

        try:
            cursor.execute(add_account_query,
                           (account, token, amount, _type, kyc, description))
            print("Added new account '{}' ('{}') on database".format(account, token))

        except sqlite3.IntegrityError:
            print("Account ", account, " with token ",
                  token, "already exists")
            return "Already Exists"

        conn.commit()

        return cursor.lastrowid


def deleteAccount(account_name, token_name):
    token_name = token_name.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        delete_account_query = """DELETE FROM cbalances WHERE account= '{}' AND token= '{}'""".format(
            account_name, token_name)
        cursor.execute(delete_account_query)

        conn.commit()


def editAccount(account_name, new_account_name=None, new_token_name=None):
    conn = create_connection()

    if new_token_name is not None:
        new_token_name = new_token_name.lower()

    with conn:
        cursor = conn.cursor()

        if new_account_name is not None:
            edit_account_query = """UPDATE cbalances SET account = '{}' WHERE account = '{}' """.format(
                new_account_name, account_name)
            cursor.execute(edit_account_query)

        if new_token_name is not None:
            edit_token_query = """UPDATE cbalances SET token = '{}' WHERE token = '{}' """.format(
                new_token_name, account_name)
            cursor.execute(edit_token_query)

        conn.commit()


def getEntriesWithAccount(account):
    """Returns all entries from an account"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_account_query = "SELECT * FROM cbalances WHERE account= '{}'".format(
            account)

        cursor.execute(get_account_query)

        result = cursor.fetchall()
        return result


def getTokensFromAccount(account):
    """Returns all tokens from an account"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_account_query = "SELECT token FROM cbalances WHERE account= '{}'".format(
            account)

        cursor.execute(get_account_query)

        result = [i[0] for i in cursor.fetchall()]
        return result


def getEntriesWithToken(token):
    """Returns all rows where a token is involved"""
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_token_query = "SELECT * FROM cbalances WHERE token= '{}'".format(
            token)

        cursor.execute(get_token_query)

        result = cursor.fetchall()
        return result


def getTotalTokenBalance(token):
    """Sums all token balances from all accounts"""
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_token_balances_query = """SELECT amount FROM cbalances WHERE token = '{}'""".format(
            token)

        cursor.execute(get_all_token_balances_query)
        result = cursor.fetchall()

        totaltokenbalance = 0
        for r in result:
            totaltokenbalance += r[0]

        return totaltokenbalance


def getAllAccounts():
    """Returns a listwith all accounts on cbalances"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_accounts_query = "SELECT account FROM cbalances"

        cursor.execute(get_all_accounts_query)

        result = cursor.fetchall()
        result_no_duplicates = []

        for r in result:
            r = r[0]
            if r not in result_no_duplicates:
                result_no_duplicates.append(r)

        return result_no_duplicates


def getAllAccountsWithToken():
    """Returns a list with all (account,token) tuples on cbalances"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_accounts_query = "SELECT account,token FROM cbalances"

        cursor.execute(get_all_accounts_query)

        return cursor.fetchall()


def getAllTokens():
    """Returns a list with all tokens"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_tokens_query = "SELECT token FROM cbalances"
        cursor.execute(get_all_tokens_query)

        result = cursor.fetchall()
        result_no_duplicates = []

        for r in result:
            r = r[0]
            if r not in result_no_duplicates:
                result_no_duplicates.append(r)

        return result_no_duplicates


def getAllTokensWithAmount():
    """Returns a dict with each full token balance from each token"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_tokens_and_amounts_query = "SELECT token, amount FROM cbalances"
        cursor.execute(get_all_tokens_and_amounts_query)

        result = cursor.fetchall()
        result_dict = {}
        final_result = []
        for r in result:
            token = r[0]
            amount = r[1]
            if token in result_dict.keys():
                result_dict[token] += amount
            else:
                result_dict[token] = amount

        for r in result_dict:
            final_result.append((r, result_dict[r]))

        return final_result


def getAllAccountsWithAmount():
    """ Returns a dict with each full account balance """
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_accounts_and_amounts_query = "SELECT account, token,amount FROM cbalances"
        cursor.execute(get_all_accounts_and_amounts_query)

        result = cursor.fetchall()
        result_dict = {}
        final_result = []
        for r in result:
            account = r[0]
            token = r[1]
            amount = r[2]
            amount_btc = float(prices.toBTC(token, amount))
            if account in result_dict.keys():
                # We add the amount to the account
                result_dict[account] += amount_btc
            else:
                result_dict[account] = amount_btc

        for r in result_dict:
            final_result.append((r, result_dict[r]))

        return final_result


def getAllAccountsWithAmount_fiat():
    """ Returns a dict with each full account balance """
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_accounts_and_amounts_query = "SELECT account, token,amount FROM cbalances"
        cursor.execute(get_all_accounts_and_amounts_query)

        result = cursor.fetchall()
        result_dict = {}
        final_result = []
        for r in result:
            account = r[0]
            token = r[1]
            amount = r[2]
            amount_btc = float(prices.toBTC(token, amount))
            amount_fiat = prices.btcToFiat(
                amount_btc, confighandler.get_fiat_currency())
            if account in result_dict.keys():
                # We add the amount to the account
                result_dict[account] += amount_fiat
            else:
                result_dict[account] = amount_fiat

        for r in result_dict:
            final_result.append((r, result_dict[r]))

        return final_result


def getAccountWithToken(account, token):
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_account_with_token_query = "SELECT * FROM cbalances WHERE token= '{}' AND account='{}'".format(
            token, account)

        cursor.execute(get_account_with_token_query)

        result = cursor.fetchall()
        if result == []:
            return None
        return result[0]


def getAllEntries():
    """Returns all entries on cbalances"""
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_all_accounts_query = "SELECT * FROM cbalances"

        cursor.execute(get_all_accounts_query)

        return cursor.fetchall()


def updateBalance(account, token, newbalance):
    """ Changes balance for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        update_balance_query = "UPDATE cbalances SET amount = {} WHERE account = '{}' AND token = '{}' ".format(newbalance,
                                                                                                                account, token)
        cursor.execute(update_balance_query)

        conn.commit()


def updateType(account, token, newtype):
    """ Changes type for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        update_type_query = "UPDATE cbalances SET type = '{}' WHERE account = '{}' AND token = '{}' ".format(newtype,
                                                                                                             account, token)
        cursor.execute(update_type_query)

        conn.commit()


def updateKYC(account, token, newkyc):
    """ Changes kyc for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        update_kyc_query = "UPDATE cbalances SET kyc = '{}' WHERE account = '{}' AND token = '{}' ".format(newkyc,
                                                                                                           account, token)
        cursor.execute(update_kyc_query)

        conn.commit()


def updateDescription(account, token, newdescription):
    """ Changes description for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        update_description_query = "UPDATE cbalances SET description = '{}' WHERE account = '{}' AND token = '{}' ".format(newdescription,
                                                                                                                           account, token)
        cursor.execute(update_description_query)

        conn.commit()


def getType(account, token):
    """ Returns the type of the account with a certain token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_type_query = "SELECT type from cbalances WHERE account = '{}' AND token = '{}'".format(
            account, token)

        cursor.execute(get_type_query)

        try:
            return cursor.fetchall()[0][0]
        except IndexError:
            raise IndexError(f"Could not find type of {account},{token}")


def getKYC(account, token):
    """ Returns the kyc of the account with a certain token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_kyc_query = "SELECT kyc from cbalances WHERE account = '{}' AND token = '{}'".format(
            account, token)

        cursor.execute(get_kyc_query)

        return cursor.fetchall()[0][0]


def getDescription(account, token):
    """ Returns the description of the account with a certain token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_description_query = "SELECT description from cbalances WHERE account = '{}' AND token = '{}'".format(
            account, token)

        cursor.execute(get_description_query)

        return cursor.fetchall()[0][0]


def getBalance(account, token):
    """ Returns the balance of the account with a certain token """
    token = token.lower()
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_balance_query = "SELECT amount from cbalances WHERE account = '{}' AND token = '{}'".format(
            account, token)

        cursor.execute(get_balance_query)

        return cursor.fetchall()[0][0]


def getTotalBalanceAllAccounts():
    """
    Returns the sum of all the balances of all the accounts on this table
    """
    conn = create_connection()

    with conn:
        cursor = conn.cursor()

        get_total_balances_all_accs_query = "SELECT token,amount FROM cbalances"

        cursor.execute(get_total_balances_all_accs_query)
        result_list = cursor.fetchall()
        cumsum = 0
        for token, amount in result_list:
            cumsum += prices.toBTC(token, amount)

        return cumsum


def getTotalBalanceAllAccounts_fiat():
    """
    Returns the sum of all the balances of all the accounts on this table
    """
    return prices.btcToFiat(getTotalBalanceAllAccounts(), confighandler.get_fiat_currency())
