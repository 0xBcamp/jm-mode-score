import requests
from icecream import ic

def format_err(e):
    '''
    format the error output when fetching Covalent data. 
    Covalent API returns JSON responses with the same shape for all endpoints
    '''
    error = {
        'found_error': e['error'],
        'error_message': e['error_message'],
        'error_code': e['error_code']
    }
    ic(error)
    return error

def covalent_get_balances_or_portfolio(chain_id, eth_address):
    '''
    get historical portfolio value over time or token balances for an address. 
    This function works for 2 endpoints: either 'balances_v2' or 'portfolio_v2' 
    '''
    try:
        endpoint = f'?id={eth_address}&chain_ids={chain_id}&is_all=false'
        url = 'https://pro-openapi.debank.com/v1/user/all_token_list' + endpoint
        headers = {
            'accept': 'application/json',
            'AccessKey': '2c6fc447ee79a5395d6d2971610c1007a3a0a581'
        }
        result2 = requests.get(url, headers=headers)
        print(result2)
        result = result2.json()
        
        if result.get('error'):
            r = format_err(result)
        else:
            r = result.get('data', {})
    except requests.exceptions.JSONDecodeError:
        r = 'JSONDecodeError: invalid Covalent API key'
    except requests.exceptions.RequestException as e:
        r = f'RequestException: {e}'
    finally:
        return r


def covalent_get_transactions(chain_id, eth_address, pagesize):
    '''
    Description:
        get all transactions for a given address. This endpoint does a deep-crawl 
        of the blockchain to retrieve all kinds of transactions/transfers that 
        references the address including indexed topics within the event logs

    Parameters:
        chain_id (int): blockchain id 
        eth_address (str): wallet address to fetch txn data from
        api_key (str): Covalent api key to for the https request
        no_logs (bool): choose whether to include log events in the return object
        pagesize (int): number of results per page
        pagenumber (int): the specific page to be returned

    Returns: 
        r (dict): the txn history for a wallet address
    '''
    try:
        endpoint = f'?id={eth_address}&chain_ids={chain_id}&page_count={pagesize}'
        url = 'https://pro-openapi.debank.com/v1/user/all_history_list' + endpoint
        headers = {
            'accept': 'application/json',
            'AccessKey': '2c6fc447ee79a5395d6d2971610c1007a3a0a581'
        }
        result = requests.get(url, headers=headers).json()

        if result.get('error'):
            r = format_err(result)
        else:
            r = result.get('data', {})
    except requests.exceptions.JSONDecodeError:
        r = 'JSONDecodeError: invalid Covalent API key'
    except requests.exceptions.RequestException as e:
        r = f'RequestException: {e}'
    finally:
        return r
    
result = covalent_get_balances_or_portfolio(0x1, 0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85)
result2 = covalent_get_transactions(0x1, 0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85, 5)

print("Result1", result)
print("result2", result2)