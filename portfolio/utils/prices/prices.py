#!/usr/bin/python3

import requests
import json
import os
from datetime import datetime

coingeckoids_path = os.path.join('prices', 'coingeckoids.json')
coinprices_path = os.path.join('prices', 'coinprices.json')
BTC_TO_FIAT_NAME = 'btctofiat.json'
btctofiat_path = os.path.join('prices', BTC_TO_FIAT_NAME)
customprices_path = os.path.join('prices', 'customprices.json')


def initialize_prices(path=None):
    prev_cwd = os.getcwd()  # To return later
    if path is None:
        path = prev_cwd
    os.chdir(path)
    if 'prices' not in os.listdir():
        os.mkdir('prices')
    os.chdir(prev_cwd)
    # TODO: Decorator to go to path and return to use here and in db initializations


def update_coin_list_file():
    """ Gets all tokens from CoinGecko's API, and stores symbols and names on a file """
    # Getting data
    get_all_coins_url = 'https://api.coingecko.com/api/v3/coins/list'
    allcoins = requests.get(get_all_coins_url).json()
    coinlist = {}
    for coin in allcoins:
        coinsymbol = coin['symbol']
        coinname = coin['id']
        if coin['symbol'] not in coinlist.keys():
            # token with the same symbol as a previous one
            coinlist[coinsymbol] = []
        coinlist[coinsymbol].append(coinname)

    # Storing updated data inside file
    with open(coingeckoids_path, 'w', encoding='utf-8') as f:
        json.dump(coinlist, f, ensure_ascii=False, indent=4)


def update_btc_to_fiat():
    """ Writes btc in several fiat terms """
    with open(btctofiat_path, 'w', encoding='utf-8') as f:
        btcfiat_rate = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur%2Cusd%2Cjpy%2Ccad%2Caud%2Cchf").json()
        json.dump(btcfiat_rate, f, ensure_ascii=False, indent=4)


def update_coingecko_prices():
    """ Reads coinprices and updates prices that use coingecko's api """
    with open(coinprices_path) as f:
        scheduled_tokens = []
        coinprices = json.load(f)
        for token in coinprices:
            if coinprices[token]['method'] == 'coingecko':
                # Schedule for update
                scheduled_tokens.append(coinprices[token]['id'])

        # Getting new prices from scheduled tokens
        base_url = "https://api.coingecko.com/api/v3/simple/price?ids="
        coins_parameter = ""
        end_url = "&vs_currencies=btc"

        for _id in scheduled_tokens:
            coins_parameter += _id + "%2C"
        url = base_url+coins_parameter+end_url

        data = requests.get(url).json()
        result = {}
        for coinid in data.keys():
            symbol = id_to_symbol(coinid)
            result[symbol] = data[coinid]['btc']

        # Updating prices
        for r in result.keys():
            coinprices[r]['price'] = result[r]

    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)

        f.close()


def update_custom_price(token, price_in_btc):
    """Writes a custom price for a certaing token on customprices.json file"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    try:
        previousid = coinprices[token]['id']
    except KeyError:
        # token didn't exist before
        # we set the id the same as token
        previousid = token

    coinprices[token]['method'] = 'custom'
    coinprices[token]['price'] = price_in_btc
    coinprices[token]['id'] = previousid
    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)


def to_btc(token, amount):
    """ Reads coinprices.json and returns the token expressed in btc terms """
    token = token.lower()
    with open(coinprices_path) as f:
        prices = json.load(f)
        return round(prices[token]['price'] * amount, 8)


def to_btc_api(tokenid, amount):
    """ Calls coingecko's api and returns the token expressed in btc terms """
    if tokenid == None:
        return None

    tokenid = tokenid.lower()

    # Getting new prices from scheduled tokens
    base_url = "https://api.coingecko.com/api/v3/simple/price?ids="
    coins_parameter = tokenid+"%2C"
    end_url = "&vs_currencies=btc"
    url = base_url+coins_parameter+end_url

    price_btc = requests.get(url).json()[tokenid]['btc']
    print(price_btc)
    return price_btc


def id_to_symbol(_id):
    """Returns corresponding symbol of id according to coinlist.json"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)
        for symbol in coinprices:
            if coinprices[symbol]['id'] == _id:
                return symbol
    return None


def symbol_to_id(tokensymbol):
    """Returns coingecko's id of a symbol"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)
        tokensymbol = tokensymbol.lower()
        try:
            return coinprices[tokensymbol.lower()]['id']
        except:
            raise KeyError(
                "Symbol {} not in coinprices.".format(tokensymbol))


def symbol_to_id_coingecko_list(symbol):
    """ Returns all ids that have that symbol associated """
    symbol = symbol.lower()
    with open(coingeckoids_path) as f:
        coingeckoids = json.load(f)

        try:
            return coingeckoids[symbol]
        except KeyError:
            print("Symbol {} not in coingeckolist.".format(symbol))
            return []


def btc_to_fiat(amount, currency="EUR"):
    """Converts btc amount to fiat using btcfiat.json file"""
    if 'prices' not in os.listdir() or BTC_TO_FIAT_NAME not in os.listdir('prices'):
        update_btc_to_fiat()
    with open(btctofiat_path) as f:
        f = json.load(f)
        return(round(amount * f['bitcoin'][currency.lower()], 2))


def btc_to_fiat_date(amount, date, currency="EUR"):
    """
    Returns a btc amount converted to the selected fiat
    currency on a certain date in the past

    date must be in timestamp format
    """
    date_string = datetime.fromtimestamp(date).strftime("%d-%m-%Y")
    request = requests.get(
        "https://api.coingecko.com/api/v3/coins/bitcoin/history?date={}".format(date_string)).json()

    try:
        btcfiat_rate = request['market_data']['current_price'][currency.lower()]
    except KeyError:
        print("Could't get the data from the response")

    return amount*btcfiat_rate


def add_token_price(token, _method, _id, price):
    """ Adds a new token on coinprices.json """
    token = token.lower()

    with open(coinprices_path) as f:
        coinprices = json.load(f)

    coinprices[token] = {}
    coinprices[token]['method'] = _method
    coinprices[token]['id'] = _id
    coinprices[token]['price'] = price
    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)


def token_in_prices(token):
    """Return if token is in prices already"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)

        for currentoken in coinprices.keys():
            if token == currentoken:
                return True
    return False


def change_token_method(token, newmethod):
    """ Changes data obtaining method for a specific token """
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    coinprices[token]['method'] = newmethod
    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)


def get_tokens_with_custom_prices():
    """Returns list with all tokens that have currently their price set as 'custom' and their current prices """
    result = []
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    for coin in coinprices.keys():
        if coinprices[coin]['method'] == 'custom':
            result.append((coin, coinprices[coin]['price']))

    return result


def get_tokens_with_coingecko_prices():
    """Returns list with all tokens that have currently their price set as 'coingecko' and their current prices """
    result = []
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    for coin in coinprices.keys():
        if coinprices[coin]['method'] == 'coingecko':
            result.append((coin, coinprices[coin]['price']))

    return result


def get_all_tokens():
    """
    Returns all tokens that have prices on coinprices.json
    """
    with open(coinprices_path) as f:
        coinprices = json.load(f)

        return list(coinprices.keys())


def get_all_tokens_with_prices():
    """Returns list with all tokens and their price"""
    result = []
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    for coin in coinprices.keys():
        result.append((coin, coinprices[coin]['price']))

    return result


def get_token_method(tokensymbol):
    """
    Returns the current data obtaining method
    for a certainf token
    """
    with open(coinprices_path) as f:
        coinprices = json.load(f)

        return coinprices[tokensymbol]['method']


def btcToFiat_history(startdate, enddate, currency):
    """
    Returns a dictionary with the price of btc/currency
    for each day on the selected period

    Parameters:
        - startdate: timestamp
        - enddate: timestamp
        - currency: (eur,usd,jpy)
    """
    result = {}

    # getting data
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency={currency.lower()}&from={startdate}&to={enddate}"

    req = requests.get(url).json()
    req = req['prices']

    for data in req:
        date = datetime.fromtimestamp(data[0]/1000)  # Only consider date
        date = datetime(date.year, date.month, date.day)
        date = int(date.timestamp())
        price = data[1]

        # If an entry from the same day has already been stored, we ignore the rest
        # If it is the first entry of the day, we save it
        if date not in result.keys():
            result[date] = price

    return result
