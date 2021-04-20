#!/usr/bin/python3

import os
import configparser
import sqlite3
from appdirs import user_config_dir, user_data_dir

VERSION = "0.0.1"


def getConfigPath():
    return user_config_dir('portfolio')


def getUserDataPath():
    return user_data_dir('portfolio')


def initial_setup():

    CONFIG_PATH = getConfigPath()
    if 'portfolio' not in os.listdir(user_config_dir()):
        os.mkdir(CONFIG_PATH)

    if 'config.ini' not in os.listdir(CONFIG_PATH):
        create_config_file()

    migrate_version()


def create_config_file():

    CONFIG_FILE_PATH = os.path.join(getConfigPath(), 'config.ini')
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


CONFIG_PATH = getConfigPath()
CONFIG_FILE_PATH = os.path.join(getConfigPath(), 'config.ini')


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


def set_version():
    """ Sets the version on the config file """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    config.set('INFO', 'version', VERSION)

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
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    config.set('PORTFOLIODATA PATHS', name, location)

    with open(CONFIG_FILE_PATH, 'w') as cf:
        config.write(cf)


# Migration

def migrate_version():
    """
    Checks the current version, and executes any migration needed tasks, if necessary
    """

    # Migration from no version to version 0.0.1
    if get_version() == "None":
        update_timestamps_from_db_to_ints()
        set_version()

    else:
        return

    add_version_to_databases()


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


def update_timestamps_from_db_to_ints():
    """
    Scans all .db files, and removes decimals from timestamps
    """

    # get paths to all databases
    paths = get_portfolios().values()

    for path in paths:
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
