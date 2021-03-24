#!/usr/bin/python3
"""
Handles all the input and output operations that use the strategies table from portfolio.db
"""

import sqlite3
import os
from datetime import datetime
from gui.dbhandler import balances


PATH_TO_DB = os.path.join('database', 'portfolio.db')


def createConnection(path_to_db=PATH_TO_DB):
    conn = None

    conn = sqlite3.connect(path_to_db)

    return conn


def addStrategy(new_strategy, markettype):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        add_account_query = """INSERT INTO 'strategies'
            ('strategy','markettype','amount')
            VALUES (?,?,?);"""

        try:
            cursor.execute(add_account_query,
                           (new_strategy, markettype, 0))
            print("Added new account '{}' on database".format(new_strategy))

        except sqlite3.IntegrityError:
            print("Account ", new_strategy, "already exists on database")
            return "Already Exists"

        conn.commit()

        return cursor.lastrowid


def deleteStrategy(strategy_name):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        delete_strategy_query = """DELETE FROM strategies WHERE strategy= '{}' """.format(
            strategy_name)
        cursor.execute(delete_strategy_query)

        conn.commit()


def editStrategyName(strategy_name, new_strategy_name):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        edit_strategy_query = """UPDATE strategies SET strategy = '{}' WHERE strategy = '{}' """.format(
            new_strategy_name, strategy_name)
        cursor.execute(edit_strategy_query)

        conn.commit()


def editStrategyType(strategy_type, new_strategy_type):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        edit_strategy_query = """UPDATE strategies SET markettype = '{}' WHERE markettype = '{}' """.format(
            new_strategy_type, strategy_type)
        cursor.execute(edit_strategy_query)

        conn.commit()


def updateStrategies_withNewResult(strategy, amount):
    """Adds the new result to the specific strategy involved, updating its balance"""
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        currentbalance = getStrategyBalance(strategy)
        if isinstance(amount, str):
            if '.' in amount:
                amount = int(round(float(amount[:-2]), 0))
            else:
                amount = int(amount)

        update_strategy_with_new_result_query = "UPDATE strategies SET amount = {} WHERE strategy = '{}'".format(
            currentbalance+amount, strategy)
        print(update_strategy_with_new_result_query)

        cursor.execute(update_strategy_with_new_result_query)

        conn.commit()


def getStrategy(strategy):
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_strategy_query = "SELECT * FROM strategies WHERE strategy= '{}'".format(
            strategy)

        cursor.execute(get_strategy_query)

        result = cursor.fetchall()
        if result == []:
            return result
        return result[0]


def getStrategyBalance(strategy):
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_strategy_query = "SELECT amount FROM strategies WHERE strategy= '{}'".format(
            strategy)

        cursor.execute(get_strategy_query)

        result = cursor.fetchall()
        if result == []:
            return result
        return result[0][0]


def getStrategyMarketType(strategy):
    conn = createConnection()
    with conn:
        cursor = conn.cursor()

        get_strategy_markettype_query = "SELECT markettype FROM strategies WHERE strategy = '{}'".format(
            strategy
        )

        cursor.execute(get_strategy_markettype_query)

        result = cursor.fetchall()
        return result[0][0]


def getAllStrategies():
    conn = createConnection()

    with conn:
        cursor = conn.cursor()

        get_all_strategies_query = "SELECT * FROM strategies"

        cursor.execute(get_all_strategies_query)

        return cursor.fetchall()
