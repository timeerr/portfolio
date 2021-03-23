#!/usr/bin/python3

import os
import configparser
from appdirs import user_config_dir, user_data_dir


def getConfigPath():
    return user_config_dir('portfolio')


def getUserDataPath():
    return user_data_dir('portfolio')


def initial_setup():
    if 'portfolio' not in os.listdir(os.path.join(os.path.expanduser('~'), '.config')):
        CONFIG_PATH = getConfigPath()
        os.mkdir(CONFIG_PATH)

    CONFIG_PATH = getConfigPath()
    CONFIG_FILE_PATH = os.path.join(getConfigPath(), 'config.ini')

    if 'config.ini' not in os.listdir(CONFIG_PATH):
        create_config_file(CONFIG_FILE_PATH)


def create_config_file(path):

    CONFIG_FILE_PATH = os.path.join(getConfigPath(), 'config.ini')
    with open(CONFIG_FILE_PATH, 'w') as cf:
        config = configparser.ConfigParser()

        config.add_section('LANGUAGE')
        config.set('LANGUAGE', 'language', 'None')

        config.add_section('PORTFOLIODATA PATHS')

        config.add_section('PREFERENCES')
        config.set('PREFERENCES', 'fiat_currency', 'None')

        config.write(cf)


CONFIG_PATH = getConfigPath()
CONFIG_FILE_PATH = os.path.join(getConfigPath(), 'config.ini')


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
