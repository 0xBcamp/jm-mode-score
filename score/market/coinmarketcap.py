from icecream import ic
import requests


def coinmarketcap_currencies(api_key, limit):
    '''
    Description:
        returns a dict of top-ranked cryptos on coinmarketcap

    Parameters:
        api_key (str): bearer token to authenticate into coinmarketcap API
        limit (float): number of top cryptos you want to keep

    Returns:
        top_cryptos (dict): ticker-value pairs for top coinmarketcap cryptos
    '''
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }

        params = {
            'start': '1',
            'limit': str(limit),
            'convert': 'USD'
        }

        r = requests.get(url, headers=headers, params=params).json()

        top_currencies = dict(
            [(n['symbol'], (n['cmc_rank'], n['quote']['USD']['price'])) for n in r['data']])

    except Exception as e:
        top_currencies = str(e)

    return top_currencies


def coinmarektcap_top_erc(api_key, limit, erc_tokens):
    '''
    Description: 
        returns ERC tokens ranked highest on Coinmarketcap

    Parameters:
        api_key (str): bearer token to authenticate into coinmarketcap API
        limit (float): number of top cryptos you want to keep
        erc_tokens (lits): list of coins which are ERC20 tokens

    Returns:
        top_erc_tokens (dict): top ERC tokens based on Coinmarketcap rankings
    '''
    try:
        # retrieve top cryptos from coinmarketcap
        top_currencies = coinmarketcap_currencies(api_key, limit)
        # keep only ERC tokens
        top_erc_tokens = {k: v[0]
                          for (k, v) in top_currencies.items() if k in erc_tokens}
        top_erc_tokens['WETH'] = top_erc_tokens['ETH']*1.25

    except Exception as e:
        top_erc_tokens = str(e)

    finally:
        return top_erc_tokens


def coinmarketcap_rate(api_key, coin_in, coin_out):
    '''
    Description:
        returns a conversion rate for the coin pair coin_in-coin_out

    Parameters:
        api_key (str): bearer token to authenticate into coinmarketcap API
        coin_in (str): ticker symbol for your base coin
        coin_out (str): ticker symbol for the coin to convert into

    Returns:
        rate (float): rate you ought to multiply your base coin by, to obtain its coin_out equilavent
    '''
    try:
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }

        params = {
            'amount': 1,
            'symbol': coin_in,
            'convert': coin_out
        }

        # Define url for coinmarketcap API
        url = 'https://pro-api.coinmarketcap.com/v2/tools/price-conversion'

        # Run GET task to fetch best cryptos from coinmarketcap API
        r = requests.get(url, headers=headers, params=params).json()
        rate = r['data'][0]['quote'][coin_out]['price']

    except Exception as e:
        ic(str(e))
        rate = 0

    return rate
