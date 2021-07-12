"""
Handles all the input and output operations that use the cbalances table from cportfolio.db
"""
#!/usr/bin/python3 import sqlite3from sqlite3 import Error from datetime import datetime

import sqlite3
import os

from portfolio.utils.prices import prices
from portfolio.utils import confighandler
from portfolio.db.dbutils import DBHandler, create_connection_c as create_connection


def add_account(account: str, token: str, amount: float, _type: str, kyc: str, description: str):
    """ Adds account to database """
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
            conn.commit()
            print("Added new account '{}' ('{}') on database".format(account, token))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print("Account ", account, " with token ",
                  token, "already exists")
        return None


def delete_account(account_name: str, token_name: str):
    """Deletes the account with name=account_name and token=token_name"""
    token_name = token_name.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM cbalances WHERE account= '{account_name}' AND token= '{token_name}'")
        conn.commit()


def edit_account(account_name: str, new_account_name: str = None, new_token_name: str = None):
    raise NotImplementedError


def get_entries_with_account(account: str):
    """Returns all entries from an account"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM cbalances WHERE account= '{account}'")
        return cursor.fetchall()


def get_tokens_from_account(account: str):
    """Returns all tokens from an account"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT token FROM cbalances WHERE account= '{account}'")
        return [i[0] for i in cursor.fetchall()]


def get_entries_with_token(token: str):
    """Returns all rows where a token is involved"""
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM cbalances WHERE token= '{token}'")
        return cursor.fetchall()


def get_total_token_balance(token: str):
    """Sums all token balances from all accounts"""
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT amount FROM cbalances WHERE token = '{token}'""")
        result = cursor.fetchall()
        return sum([r[0] for r in result])


def get_total_token_balance_fiat(token: str):
    """
    Sums all token balances from all accounts
    Expressed in fiat"""
    return prices.btc_to_fiat(get_total_token_balance(token))


def get_all_accounts():
    """Returns a list with all accounts on cbalances"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT account FROM cbalances")
        result = [d[0] for d in cursor.fetchall()]
        return list(set(result))  # No duplicates


def get_all_accounts_with_token():
    """Returns a list with all (account,token) tuples on cbalances"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT account,token FROM cbalances")
        return cursor.fetchall()


def get_all_tokens():
    """Returns a list with all tokens"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT token FROM cbalances")
        result = [d[0] for d in cursor.fetchall()]
        return list(set(result))  # No duplicates


def get_all_tokens_with_amount():
    """Returns tuples as (token, total token amount)"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT token, SUM(amount) as sum_amount FROM cbalances GROUP BY token""")
        return cursor.fetchall()


def get_all_accounts_with_amount():
    """ Returns tuples as (account, total amount in btc)"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        cursor.execute(
            """SELECT account,token,amount FROM cbalances """)
        result = cursor.fetchall()
        # Convert to BTC
        accounts = {d[0]: 0 for d in result}
        for r in result:
            acc, token, amount = r
            accounts[acc] += prices.to_btc(token, amount)
        return [(acc, accounts[acc]) for acc in accounts]


def get_all_accounts_with_amount_fiat():
    """ Returns tuples as (account, total amount in fiat)"""
    data = get_all_accounts_with_amount()
    return [(d[0], prices.btc_to_fiat(d[1])) for d in data]


def get_account_with_token(account: str, token: str):
    """Returns data from a specific account-token combination"""
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM cbalances WHERE token= '{token}' AND account='{account}'")
        result = cursor.fetchall()
        return result[0] if result != [] else None


def get_all_entries():
    """Returns all entries on cbalances"""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cbalances")
        return cursor.fetchall()


def update_balance(account: str, token: str, newbalance: float):
    """ Changes balance for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE cbalances SET amount = {newbalance} WHERE account = '{account}' AND token = '{token}' ")
        conn.commit()


def update_type(account: str, token: str, newtype: str):
    """ Changes type for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE cbalances SET type = '{newtype}' \
            WHERE account= '{account}' AND token = '{token}' ")
        conn.commit()


def update_kyc(account: str, token: str, newkyc: str):
    """ Changes kyc for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE cbalances SET kyc = '{newkyc}' WHERE account = '{account}' AND token = '{token}' ")
        conn.commit()


def update_description(account: str, token: str, newdescription: str):
    """ Changes description for a specific account with a specific token """
    token = token.lower()
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE cbalances SET description = '{newdescription}' WHERE account = '{account}' AND token = '{token}' ")
        conn.commit()


def _get(account: str, token: str, item: str):
    """
    Retuns a specific item from an entry with a certain account-token
    combination
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT {item.lower()} from cbalances WHERE account = '{account}' AND token = '{token.lower()}'")
        try:
            return cursor.fetchall()[0][0]
        except IndexError:
            raise IndexError(f"Could not find {item} of {account},{token}")


def get_type(account: str, token: str):
    """ Returns the type of the account with a certain token """
    return _get(account, token, 'type')


def get_kyc(account: str, token: str):
    return _get(account, token, 'kyc')


def get_description(account: str, token: str):
    """ Returns the description of the account with a certain token """
    return _get(account, token, 'description')


def get_balance(account: str, token: str):
    """ Returns the balance of the account with a certain token """
    return _get(account, token, 'amount')


def get_total_account_balance(account: str):
    """
    Returns the total balance from all tokens from a certain account
    expressed in btc
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT token,amount FROM cbalances WHERE account = '{account}'")
        result = cursor.fetchall()
        return sum([prices.to_btc(d[0], d[1]) for d in result])


def get_total_account_balance_fiat(account):
    """
    Returns the total balance from all tokens from a certain account
    expressed in fiat
    """
    return prices.btc_to_fiat(get_total_account_balance(account))


def get_total_balance_all_accounts():
    """
    Returns the sum of all the balances of all the accounts on this table
    expressed in btc
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT token,amount FROM cbalances")
        return sum(prices.to_btc(d[0], d[1]) for d in cursor.fetchall())


def get_total_balance_all_accounts_fiat():
    """
    Returns the sum of all the balances of all the accounts on this table
    """
    return prices.btc_to_fiat(get_total_balance_all_accounts())
