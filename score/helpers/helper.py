from pandas.io.json._normalize import nested_to_record
from datetime import datetime, timezone
from ndicts.ndicts import NestedDict
from operator import mul
import pandas as pd
import numpy as np


NOW = datetime.now().date()

def keep_dict(score, data):
    d = {}
    d['data'] = data

    d['request'] = {}
    d['request']['datetime'] = datetime.now(timezone.utc)

    d['response'] = {}
    d['response']['score'] = score

    d = {k: v for k, v in d.items() if not isinstance(v, list)}
    return d

# Helper function to safely get a value from a dictionary
def safe_get(dictionary, key, default=None):
    return dictionary.get(key, default)


def safe_calculation(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return 0, {f"{func.__name__}_error": str(e)}

def dot_product(l1, l2):
    return sum(map(mul, l1, l2))


def head_tail_list(lst):
    return lst[0], lst[-1]

def immutable_array(arr):
    arr.flags.writeable = False
    return arr

def build_normalized_matrix(size, scalar):
    '''
    build a normalized 2D scoring matrix.
    Matrix axes growth rate is defined by a natural logarithm function
    '''
    m = np.zeros(size)
    # evaluate the bottom right element in the matrix and use it to normalize the matrix
    extrema = round(scalar[0] * np.log(m.shape[0]) + scalar[1] * np.log(m.shape[1]), 2)

    for a in range(m.shape[0]):
        for b in range(m.shape[1]):
            m[a][b] = round(
                (scalar[0] * np.log(a + 1) + scalar[1] * np.log(b + 1)) / extrema, 2
            )
    return m

def covalent_params(params, score_range):

    count_to_four = immutable_array(np.array(params['metrics']['count_to_four']))
    volume_now = immutable_array(
        np.array(params['metrics']['volume_now']) * 1000
    )  # should be *1000
    volume_per_txn = immutable_array(
        np.array(params['metrics']['volume_per_txn']) * 100
    )  # should be *100
    duration = immutable_array(np.array(params['metrics']['duration']))
    count_operations = immutable_array(np.array(params['metrics']['count_operations']))
    cred_deb = immutable_array(
        np.array(params['metrics']['cred_deb']) * 1000
    )  # should be *1000
    frequency_txn = immutable_array(np.array(params['metrics']['frequency_txn']))
    avg_run_bal = immutable_array(
        np.array(params['metrics']['avg_run_bal']) * 100
    )  # should be *100
    due_date = immutable_array(np.array(params['metrics']['due_date']))

    mtx_traffic = immutable_array(
        build_normalized_matrix(
            tuple(params['matrices']['mtx_traffic']['shape']),
            tuple(params['matrices']['mtx_traffic']['scalars']),
        )
    )
    mtx_stamina = immutable_array(
        build_normalized_matrix(
            tuple(params['matrices']['mtx_stamina']['shape']),
            tuple(params['matrices']['mtx_stamina']['scalars']),
        )
    )

    head, tail = head_tail_list(score_range)
    fico = (np.array(score_range[:-1]) - head) / (tail - head)
    fico_medians = [
        round(fico[i] + (fico[i + 1] - fico[i]) / 2, 2) for i in range(len(fico) - 1)
    ]
    fico_medians.append(1)
    fico_medians = immutable_array(np.array(fico_medians))

    k = [
        'count_to_four',
        'volume_now',
        'volume_per_txn',
        'duration',
        'count_operations',
        'cred_deb',
        'frequency_txn',
        'avg_run_bal',
        'due_date',
        'fico_medians',
        'mtx_traffic',
        'mtx_stamina',
    ]

    v = [
        count_to_four,
        volume_now,
        volume_per_txn,
        duration,
        count_operations,
        cred_deb,
        frequency_txn,
        avg_run_bal,
        due_date,
        fico_medians,
        mtx_traffic,
        mtx_stamina,
    ]

    return dict(zip(k, v))


def validate_data(data, data_type):
    if not data or 'items' not in data or not isinstance(data['items'], list):
        raise ValueError(f"Invalid {data_type} data structure")
    
    for item in data['items']:
        if data_type == 'transaction':
            if 'value_quote' not in item or not isinstance(item['value_quote'], (int, float)):
                item['value_quote'] = 0  # Set a default value
            if 'block_signed_at' not in item or not isinstance(item['block_signed_at'], str):
                raise ValueError(f"Invalid block_signed_at in transaction: {item}")
        elif data_type == 'balance':
            if 'quote' not in item or not isinstance(item['quote'], (int, float)):
                item['quote'] = 0  # Set a default value


def get_staking_data(balances):
    staking_data = {
        'total_staked': 0,
        'staked_tokens': []
    }
    
    for item in balances.get('items', []):
        if item.get('type') == 'staked':  # You might need to adjust this condition based on how Covalent identifies staked tokens
            staking_data['total_staked'] += item['balance'] * item['quote_rate']
            staking_data['staked_tokens'].append({
                'contract_address': item['contract_address'],
                'symbol': item['contract_ticker_symbol'],
                'amount': item['balance'],
                'quote': item['quote']
            })
    
    return staking_data

def get_yield_farming_data(transactions):
    yield_farming_data = {
        'total_returns': 0,
        'yield_events': []
    }
    
    for tx in transactions.get('items', []):
        for log in tx.get('log_events', []):
            if log.get('decoded', {}).get('name') == 'staked':  # You might need to adjust this condition based on the specific yield farming protocols you're interested in
                amount = int(log['decoded']['params'][0]['value']) / 10**18  # Assuming 18 decimal places, adjust if necessary
                yield_farming_data['total_returns'] += amount
                yield_farming_data['yield_events'].append({
                    'tx_hash': tx['tx_hash'],
                    'block_height': tx['block_height'],
                    'amount': amount,
                    'token_address': log['sender_address']
                })
    
    return yield_farming_data