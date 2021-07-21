#!/usr/bin/python3

import os
import configparser
import sqlite3
import logging
from datetime import datetime


from portfolio.utils.prices import prices
from portfolio.utils.appdirs import user_config_dir, user_data_dir

VERSION = "0.0.2"

PORTFOLIO_DATABASE_DIR_NAME = 'database'


def get_config_path():
    return user_config_dir('portfolio')


def get_user_data_path():
    return user_data_dir('portfolio')


CONFIG_PATH = get_config_path()
CONFIG_FILE_PATH = os.path.join(get_config_path(), 'config.ini')


def initial_setup():
    CONFIG_PATH = get_config_path()
    if 'portfolio' not in os.listdir(user_config_dir()):
        os.mkdir(CONFIG_PATH)
    if 'config.ini' not in os.listdir(CONFIG_PATH):
        create_config_file()
    migrate_version()


def create_config_file():
    with open(CONFIG_FILE_PATH, 'w') as cf:
        config = configparser.ConfigParser()

        config.add_section('LANGUAGE')
        config.set('LANGUAGE', 'language', 'None')

        config.add_section('PORTFOLIODATA PATHS')

        config.add_section('PREFERENCES')
        config.set('PREFERENCES', 'fiat_currency', 'None')

        config.add_section('INFO')
        config.set('INFO', 'version', VERSION)

        config.write(cf)


def get_version():
    """Reads configuration file to get the current version of the app"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    try:
        return config['INFO']['version']

    except (configparser.NoSectionError, KeyError):
        # Add new version section to configfile
        config.add_section('INFO')
        config.set('INFO', 'version', "None")

        with open(CONFIG_FILE_PATH, "w") as cf:
            config.write(cf)

        return "None"


def get_language():
    """Reads configuration file to parse the current selected language"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    return config['LANGUAGE']['language']


def get_fiat_currency():
    """Reads configuration file to parse the current selected language"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    return config['PREFERENCES']['fiat_currency']


def get_portfolios():
    """Reads the configuration file and returns all portfolio directories"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    return(config['PORTFOLIODATA PATHS'])


def set_version(version=VERSION):
    """ Sets the version on the config file """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    config.set('INFO', 'version', version)

    with open(CONFIG_FILE_PATH, 'w') as cf:
        config.write(cf)


def set_language(language):
    """ Sets the desired language on the config file """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    config.set('LANGUAGE', 'language', language)

    with open(CONFIG_FILE_PATH, 'w') as cf:
        config.write(cf)


def set_fiat_currency(fiat_currency):
    """ Sets the desired fiat currency on the config file """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    config.set('PREFERENCES', 'fiat_currency', fiat_currency)

    with open(CONFIG_FILE_PATH, 'w') as cf:
        config.write(cf)


def add_portfolio(name, location):
    # ---- Create data ----
    if PORTFOLIO_DATABASE_DIR_NAME not in os.listdir(location):
        os.mkdir(os.path.join(location, 'database'))
    # Create version file
    VERSION_FILE_PATH = os.path.join(location, 'database', 'version.txt')
    with open(VERSION_FILE_PATH, 'w') as vf:
        vf.write(get_version())
    # Create databases
    from portfolio.db.cdbhandler import cdb_initialize
    from portfolio.db.fdbhandler import db_initialize
    db_initialize.initialize(path=location)
    cdb_initialize.initialize(path=location)
    from portfolio.utils.prices import prices
    prices.initialize_prices(path=location)

    # ---- Add to config file ----
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    config.set('PORTFOLIODATA PATHS', name, location)
    with open(CONFIG_FILE_PATH, 'w') as cf:
        config.write(cf)


# ----------------------------------------------------
# ------------- Version Migration --------------------
# ----------------------------------------------------
def migrate_version():
    """
    Checks the current version, and executes
    all necessary migration scripts
    """
    # ----------- App Migration ----------
    if get_version() in ("None", "0.0.1"):
        pass
    # ----------- Database Migration ----------
    db_paths = get_portfolios().values()
    for path in db_paths:
        db_version = str(get_database_version(path))
        if db_version == "None":
            logging.info("Updating to version %s", VERSION)
            update_timestamps_from_db_to_ints(path)
        if db_version == "0.0.1":
            logging.info("Updating to version %s", VERSION)
            add_balance_fiat_to_cportfoliodb(path)
        if db_version < VERSION:
            add_version_to_databases()
        if db_version > VERSION:
            logging.info(
                path, " database's version is ahead of current app version. update app required")
    set_version()


def get_database_version(path_to_db):
    """
    Returns the version number of the database
    """
    with open(os.path.join(path_to_db, "database", "version.txt")) as f:
        return f.read().split()[0]


def add_version_to_databases():
    """
    Scans all portfolios added and adds a version file on the database folder
    of each one
    """
    paths = get_portfolios().values()

    for path in paths:
        with open(os.path.join(path, "database", "version.txt"), "w+") as f:
            print(f"Writing version file on {path}")
            f.write(VERSION)


# Database version migration scripts
def update_timestamps_from_db_to_ints(path):
    """
    Scans all .db files, and removes decimals from timestamps
    """

    # portfolio.db
    portfoliodb_path = os.path.join(path, "database", "portfolio.db")

    conn = sqlite3.connect(portfoliodb_path)
    cursor = conn.cursor()

    get_entries_query = "SELECT id,date FROM balancehistory"
    cursor.execute(get_entries_query)

    entries = cursor.fetchall()

    for entry in entries:
        _id = entry[0]
        new_timestamp = int(float(entry[1]))

        update_timestamp_query = f"UPDATE balancehistory SET date={new_timestamp} WHERE id={_id}"
        cursor.execute(update_timestamp_query)

        conn.commit()

    # cportfolio.db
    cportfoliodb_path = os.path.join(path, "database", "cportfolio.db")

    conn = sqlite3.connect(cportfoliodb_path)
    cursor = conn.cursor()

    get_entries_query = "SELECT id,date FROM cbalancehistory"
    cursor.execute(get_entries_query)

    entries = cursor.fetchall()

    for entry in entries:
        _id = entry[0]
        new_timestamp = int(float(entry[1]))

        update_timestamp_query = f"UPDATE cbalancehistory SET date={new_timestamp} WHERE id={_id}"
        cursor.execute(update_timestamp_query)

        conn.commit()


def add_balance_fiat_to_cportfoliodb(path):
    """
    Adds a column on cportfolio's cbalancehistory table
    by converting each balance_btc to its fiat value on each entry's date
    """
    logging.info("Updating databases")
    logging.info("Adding balance_fiat history to cbalancehistory on %s", path)
    # cportfolio.db
    cportfoliodb_path = os.path.join(path, "database", "cportfolio.db")
    conn = sqlite3.connect(cportfoliodb_path)

    with conn:
        cursor = conn.cursor()

        # get data
        get_balances_btc_query = "SELECT id, date,balance_btc FROM cbalancehistory"
        cursor.execute(get_balances_btc_query)

        entries = cursor.fetchall()

        # Now, we need to convert each balance_btc to its fiat value
        # on each entry's date
        dates = [i[1] for i in entries]
        dates = set(dates)

        mindate = min(dates)
        maxdate = max(dates)

        # Get btc/eur history from coingecko's api
        if len(dates) > 1:
            priceshistory_eur = prices.btcToFiat_history(
                mindate, maxdate, 'eur')
            priceshistory_usd = prices.btcToFiat_history(
                mindate, maxdate, 'usd')
            priceshistory_jpy = prices.btcToFiat_history(
                mindate, maxdate, 'jpy')
        elif len(dates) == 1:
            single_date = datetime.fromtimestamp(list(dates)[0])
            single_date = datetime(
                single_date.year, single_date.month, single_date.day).timestamp()
            priceshistory_eur = {
                single_date: prices.btcToFiat_Date(1, single_date, 'eur')}
            priceshistory_usd = {
                single_date: prices.btcToFiat_Date(1, list(dates)[0], 'usd')}
            priceshistory_jpy = {
                single_date: prices.btcToFiat_Date(1, list(dates)[0], 'jpy')}

        # Convert each balances_btc to balance_fiat
        balances_fiat = []
        for entry in entries:
            _id = entry[0]
            date = datetime.fromtimestamp(entry[1])
            date = datetime(date.year, date.month, date.day).timestamp()

            balance_btc = entry[2]

            balance_eur = int(balance_btc * priceshistory_eur[date])
            balance_usd = int(balance_btc * priceshistory_usd[date])
            balance_jpy = int(balance_btc * priceshistory_jpy[date])

            balances_fiat.append(
                (_id, balance_eur, balance_usd, balance_jpy))

        # Add columns to cbalancehistory table
        add_column_query = "ALTER TABLE cbalancehistory ADD COLUMN balance_{} integer"
        try:
            cursor.execute(add_column_query.format('eur'))
        except Exception as e:
            logging.error(e)
        try:
            cursor.execute(add_column_query.format('usd'))
        except Exception as e:
            logging.error(e)
        try:
            cursor.execute(add_column_query.format('jpy'))
        except Exception as e:
            logging.error(e)
        # If it fails, it already exists assumed (connection errors will be detected later)

        # Fill columns with history
        fill_balance_fiat_query = "UPDATE cbalancehistory SET balance_{} = {} WHERE id={}"
        for balance_fiat in balances_fiat:
            _id, balance_eur, balance_usd, balance_jpy, *_ = balance_fiat
            cursor.execute(fill_balance_fiat_query.format(
                'eur', balance_eur, _id))
            cursor.execute(fill_balance_fiat_query.format(
                'usd', balance_usd, _id))
            cursor.execute(fill_balance_fiat_query.format(
                'jpy', balance_jpy, _id))
        conn.commit()
