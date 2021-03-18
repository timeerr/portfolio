#!/usr/bin/python3

import requests
import json
import os

coingeckoids_path = os.path.join('prices', 'coingeckoids.json')
coinprices_path = os.path.join('prices', 'coinprices.json')
btctofiat_path = os.path.join('prices', 'btctofiat.json')
customprices_path = os.path.join('prices', 'customprices.json')


def initialize_prices():
    if 'prices' not in os.listdir():
        os.mkdir('prices')


def updateCoinListFile():
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

        f.close()


def updateBTCToFiat():
    """ Writes btc in several fiat terms """
    with open(btctofiat_path, 'w', encoding='utf-8') as f:
        btcfiat = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur%2Cusd%2Cjpy%2Ccad%2Caud%2Cchf").json()
        json.dump(btcfiat, f, ensure_ascii=False, indent=4)

        f.close()


def updateCoingeckoPrices():
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
            symbol = idToSymbol(coinid)
            result[symbol] = data[coinid]['btc']

        # Updating prices
        for r in result.keys():
            coinprices[r]['price'] = result[r]

    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)

        f.close()


def updateCustomPrice(token, price_in_btc):
    """Writes a custom price for a certaing token on customprices.json file"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    coinprices[token]['method'] = 'custom'
    coinprices[token]['price'] = price_in_btc
    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)


def toBTC(token, amount):
    """ Reads coinprices.json and returns the token expressed in btc terms """
    token = token.lower()
    with open(coinprices_path) as f:
        prices = json.load(f)
        return round(prices[token]['price'] * amount, 8)


def toBTCAPI(tokenid, amount):
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


def idToSymbol(_id):
    """Returns corresponding symbol of id according to coinlist.json"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)
        for symbol in coinprices:
            if coinprices[symbol]['id'] == _id:
                return symbol
    return None


def symbolToId(tokensymbol):
    """Returns coingecko's id of a symbol"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)
        tokensymbol = tokensymbol.lower()
        try:
            return coinprices[tokensymbol.lower()]['id']
        except:
            raise KeyError(
                "Symbol {} not in coinprices.".format(tokensymbol))


def symbolToId_CoinGeckoList(symbol):
    """
    Returns all ids that have that symbol associated
    """
    symbol = symbol.lower()
    with open(coingeckoids_path) as f:
        coingeckoids = json.load(f)

        try:
            return coingeckoids[symbol]
        except KeyError:
            print("Symbol {} not in coingeckolist.".format(symbol))
            return []


def btcToFiat(amount, currency="EUR"):
    """Converts btc amount to fiat using btcfiat.json file"""
    with open(btctofiat_path) as f:
        f = json.load(f)
        return(round(amount * f['bitcoin'][currency.lower()], 2))


def addTokenPrice(token, _method, _id, price):
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


def tokenInPrices(token):
    """Return if token is in prices already"""
    with open(coinprices_path) as f:
        coinprices = json.load(f)

        for currentoken in coinprices.keys():
            if token == currentoken:
                return True
    return False


def changeTokenMethod(token, newmethod):
    """ Changes data obtaining method for a specific token """
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    coinprices[token]['method'] = newmethod
    with open(coinprices_path, 'w', encoding='utf-8') as f:
        json.dump(coinprices, f, ensure_ascii=False, indent=4)


def getTokensWithCustomPrices():
    """Returns list with all tokens that have currently their price set as 'custom' and their current prices """
    result = []
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    for coin in coinprices.keys():
        if coinprices[coin]['method'] == 'custom':
            result.append((coin, coinprices[coin]['price']))

    return result


def getTokensWithCoingeckoPrices():
    """Returns list with all tokens that have currently their price set as 'coingecko' and their current prices """
    result = []
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    for coin in coinprices.keys():
        if coinprices[coin]['method'] == 'coingecko':
            result.append((coin, coinprices[coin]['price']))

    return result


def getAllTokens():
    """
    Returns all tokens that have prices on coinprices.json
    """
    with open(coinprices_path) as f:
        coinprices = json.load(f)

        return list(coinprices.keys())


def getAllTokensWithPrices():
    """Returns list with all tokens and their price"""
    result = []
    with open(coinprices_path) as f:
        coinprices = json.load(f)

    for coin in coinprices.keys():
        result.append((coin, coinprices[coin]['price']))

    return result


def getTokenMethod(tokensymbol):
    """
    Returns the current data obtaining method
    for a certainf token
    """
    with open(coinprices_path) as f:
        coinprices = json.load(f)

        return coinprices[tokensymbol]['method']
