from pandas.io.json._normalize import nested_to_record
from datetime import datetime, timezone
from ndicts.ndicts import NestedDict
from operator import mul
import pandas as pd
import numpy as np


NOW = datetime.now().date()


def fill_list(lst, n, s):
    temp = [0]*(n-s)
    lst.extend(temp)
    return lst


def flatten_list(lst):
    return [item for sublist in lst for item in sublist]


def flatten_dict(d):
    return nested_to_record(d, sep='_')



def remove_key_dupes(lst, k):
    memo = set()
    res = []
    for d in lst:
        if d[k] not in memo:
            res.append(d)
            memo.add(d[k])
    return res


def unpack_dict(lst, parent, keys):
    for d in lst:
        for k in keys:
            d[k] = d[parent][k]
    return lst


def unpack_dict_list(lst, key, keys):
    x = len(keys)
    for d in lst:
        values = d[key]
        if isinstance(values, list):
            y = len(values)
            if x != y:
                values = values[:x]
            for k, v in zip(keys, values):
                d[k] = v
        else:
            for k in keys:
                d[k] = None
    return lst


def merge_dict(lst1, lst2, key, keys):
    for d1 in lst1:
        for d2 in lst2:
            if d1[key] == d2[key]:
                for k in keys:
                    if isinstance(d2[k], str):
                        d1[k] = d2[k].lower()
                    else:
                        d1[k] = d2[k]
    return lst1


def remove_dict_keys(lst, keys):
    return [{k: d[k] for k in d if k not in keys} for d in lst]


def rename_dict_key(lst, k_old, k_new):
    for d in lst:
        d[k_new] = d.pop(k_old)
    return lst


def lowercase_dict_values(lst, keys):
    for d in lst:
        for k, v in d.items():
            if k in keys and isinstance(d[k], str):
                d[k] = d[k].lower()
    return lst


def add_time_from_now(lst):
    for d in lst:
        d['timespan'] = abs((NOW - d['date']).days)
    return lst


def filter_dict(lst, key, value):
    return [d for d in lst if d[key].lower() == value]


def dict_reverse_cumsum(lst, col, sum_col):
    df = pd.DataFrame(lst)
    cols = df.columns
    data = pd.DataFrame(columns=cols)
    accounts = df['account_id'].unique().tolist()
    for account_id in accounts:
        temp = df[df['account_id'] == account_id]
        row = pd.DataFrame(temp[-1:].values, columns=cols)
        row.at[0, col] = row.at[0, sum_col]
        temp = pd.concat([temp, row], axis=0, ignore_index=True)
        temp.reset_index(drop=True, inplace=True)
        temp[sum_col] = temp.loc[::-1, col].cumsum()[::-1].shift(-1)
        temp = temp[:-1]
        temp[col] = temp[col]*-1
        data = pd.concat([data, temp], axis=0, ignore_index=True)
    return data.to_dict('records')


def aggregate_dict_by_month(data, agg_dict):
    df = pd.DataFrame(data).set_index('date')
    df.index = pd.to_datetime(df.index)
    df = df.groupby([df.index.year.values, df.index.month.values]).agg(agg_dict)
    return df


def util_ratio(metadata, data):
    metadata['credit_card']['util_ratio'] = {}
    metadata['credit_card']['util_ratio']['general'] = {}
    metadata['credit_card']['util_ratio']['period'] = {}
    period = [30, 60, 90, 180, 360, 720, 1800]
    months = [-1, -2, -3, -6, -12, -24, -60]
    data['util_ratio'] = data['amount'] / data['limit']
    for p, m in zip(period, months):
        metadata['credit_card']['util_ratio']['period'][p] = data.iloc[m:].util_ratio.max()
    temp = data[data['util_ratio'] > 0]
    metadata['credit_card']['util_ratio']['general']['avg_monthly_value'] = temp['util_ratio'].mean()
    metadata['credit_card']['util_ratio']['general']['month_count'] = len(data['util_ratio'])
    return metadata


def general(metadata, lst, k1):
    ''' regardless how many different account within same account type '''
    k2 = 'general'
    df = None

    # accounts
    k3 = 'accounts'
    metadata[k1][k2][k3] = {}
    accounts = list(set([d['account_id'] for d in lst]))
    metadata[k1][k2][k3]['total_count'] = len(accounts)

    # balances
    k3 = 'balances'
    metadata[k1][k2][k3] = {}
    current, limit, high_balance = [], [], []

    for account_id in accounts:
        data = [d for d in lst if d['account_id'] == account_id]
        current.append(data[-1]['current'])
        limit.append(data[-1]['limit'])

        if k1 == 'credit_card':
            df = aggregate_dict_by_month(data, {'amount': 'sum', 'limit': 'max'})
            high_balance.append(df.amount.max())
        else:
            high_balance.append(max([d['current'] for d in data]))

        if k1 == 'checking':
            df1 = aggregate_dict_by_month(data, {'amount': 'sum'})
            metadata[k1][k2][k3]['monthly'] = {}
            metadata[k1][k2][k3]['monthly']['total_count'] = len(df1)
            metadata[k1][k2][k3]['monthly']['balance'] = df1['amount'].tolist()
            metadata[k1][k2][k3]['monthly']['overdraft_count'] = len(df1[df1['amount'] < 0].index)

    metadata[k1][k2][k3]['current'] = current
    metadata[k1][k2][k3]['limit'] = limit
    metadata[k1][k2][k3]['high_balance'] = high_balance

    # running balance
    data = pd.DataFrame(lst)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    temp = data.groupby([data['date'].dt.year, data['date'].dt.month], as_index=False).last()
    metadata[k1][k2][k3]['running_balance'] = temp['current'].tolist()

    # credit card util ratio
    if df is not None:
        metadata = util_ratio(metadata, df)

    # transactions
    k3 = 'transactions'
    metadata[k1][k2][k3] = {}
    metadata[k1][k2][k3]['total_count'] = len(lst)
    metadata[k1][k2][k3]['timespan'] = lst[0]['timespan']

    m = metadata[k1][k2][k3]['timespan'] / 30
    metadata[k1][k2][k3]['avg_monthly_count'] = metadata[k1][k2][k3]['total_count'] / m
    metadata[k1][k2][k3]['avg_monthly_value'] = sum(d['amount'] for d in lst) / m

    return metadata


def late_payment(metadata, lst):
    metadata['credit_card']['late_payment'] = {}
    metadata['credit_card']['late_payment']['general'] = {}
    metadata['credit_card']['late_payment']['period'] = {}
    period = [30, 60, 90, 180, 360, 720, 1800]
    data = [d for d in lst if d['sub_category'] == 'interest charged']
    if data:
        values = []
        for p in period:
            values.append(len([d for d in data if d['timespan'] <= p]))
        values.reverse()
        values.append(0)
        values = [values[i]-values[i+1] for i in range(len(values)-1)]
        values.reverse()

        metadata['credit_card']['late_payment']['period'] = dict(zip(period, values))
        metadata['credit_card']['late_payment']['general']['total_count'] = len(data)
        metadata['credit_card']['late_payment']['general']['month_count'] = len(
            aggregate_dict_by_month(data, {'amount': ['count']}))
    return metadata


def income(metadata, lst, key, value):
    k1 = 'checking'
    k2 = 'income'

    data = [d for d in lst if d[key] == value]
    k3 = value
    metadata[k1][k2][k3] = {}
    if data:
        df = aggregate_dict_by_month(data, {'amount': ['count', 'sum']})
        metadata[k1][k2][k3]['avg_monthly_count'] = df[('amount', 'count')].mean()
        metadata[k1][k2][k3]['avg_monthly_value'] = df[('amount', 'sum')].mean()
        metadata[k1][k2][k3]['last_event_timespan'] = abs((NOW - data[-1]['date']).days)
        metadata[k1][k2][k3]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]
    return metadata


def filter_frame_outliers(data, col):
    data = data[data[col] < 0]
    high = data[col].quantile(0.99)
    return data[data[col] < high]


def expenses(metadata, lst, key, value):
    k1 = 'checking'
    k2 = 'expenses'

    data = [d for d in lst if d[key] == value]
    k3 = value.split()[0]
    metadata[k1][k2][k3] = {}
    if data:
        df = aggregate_dict_by_month(data, {'amount': ['count', 'sum']})
        df1 = filter_frame_outliers(df, ('amount', 'sum'))
        metadata[k1][k2][k3]['avg_monthly_count'] = df[('amount', 'count')].mean()
        metadata[k1][k2][k3]['avg_monthly_value'] = df1[('amount', 'sum')].mean()
        metadata[k1][k2][k3]['last_event_timespan'] = abs((NOW - data[-1]['date']).days)
        metadata[k1][k2][k3]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]

        nd = NestedDict(metadata)
        keys = [k for k in nd.keys()]
        if (k1, 'income', 'payroll', 'avg_monthly_value') in keys:
            metadata[k1][k2][k3]['avg_income_pct'] = abs(
                metadata[k1][k2][k3]['avg_monthly_value'] / metadata[k1]['income']['payroll']['avg_monthly_value'])
    return metadata


def investments(metadata, lst, key, value):
    k1 = 'checking'
    k2 = 'investments'
    k3 = 'earnings'

    data = [d for d in lst if d[key] == value]
    if data:
        cash_in = [d for d in data if d['amount'] < 0]
        cash_out = [d for d in data if d['amount'] > 0]
        k3i = 'deposits'  # FROM checking INTO external investment account
        k3o = 'withdrawals'  # FROM external investment account INTO checking
        dm, dt, wm, wt = 0, 0, 0, 0
        if cash_in:
            df = aggregate_dict_by_month(cash_in, {'amount': ['count', 'sum']})
            metadata[k1][k2][k3i]['avg_monthly_count'] = df[('amount', 'count')].mean()
            metadata[k1][k2][k3i]['avg_monthly_value'] = df[('amount', 'sum')].mean()
            metadata[k1][k2][k3i]['total_value'] = df[('amount', 'sum')].sum()
            metadata[k1][k2][k3i]['last_event_timespan'] = abs((NOW - cash_in[-1]['date']).days)
            metadata[k1][k2][k3i]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]
            dm = metadata[k1][k2][k3i]['avg_monthly_value']
            dt = metadata[k1][k2][k3i]['total_value']
        if cash_out:
            df = aggregate_dict_by_month(cash_out, {'amount': ['count', 'sum']})
            metadata[k1][k2][k3o]['avg_monthly_count'] = df[('amount', 'count')].mean()
            metadata[k1][k2][k3o]['avg_monthly_value'] = df[('amount', 'sum')].mean()
            metadata[k1][k2][k3o]['total_value'] = df[('amount', 'sum')].sum()
            metadata[k1][k2][k3o]['last_event_timespan'] = abs((NOW - cash_out[-1]['date']).days)
            metadata[k1][k2][k3o]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]
            wm = metadata[k1][k2][k3o]['avg_monthly_value']
            wt = metadata[k1][k2][k3o]['total_value']

        metadata[k1][k2][k3]['avg_monthly_value'] = dm + wm
        metadata[k1][k2][k3]['total_value'] = dt + wt
    return metadata


def cash_flow(metadata, lst, key, value):
    k1 = 'savings'
    k2 = 'cash_flow'

    data = [d for d in lst if d[key] != value]
    if data:
        cash_in = [d for d in data if d['amount'] > 0]
        cash_out = [d for d in data if d['amount'] < 0]
        k3i = 'deposits'
        k3o = 'withdrawals'
        if cash_in:
            df = aggregate_dict_by_month(cash_in, {'amount': ['count', 'sum']})
            metadata[k1][k2][k3i]['avg_monthly_count'] = df[('amount', 'count')].mean()
            metadata[k1][k2][k3i]['avg_monthly_value'] = df[('amount', 'sum')].mean()
            metadata[k1][k2][k3i]['last_event_timespan'] = abs((NOW - cash_in[-1]['date']).days)
            metadata[k1][k2][k3i]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]
        if cash_out:
            df = aggregate_dict_by_month(cash_out, {'amount': ['count', 'sum']})
            metadata[k1][k2][k3o]['avg_monthly_count'] = df[('amount', 'count')].mean()
            metadata[k1][k2][k3o]['avg_monthly_value'] = df[('amount', 'sum')].mean()
            metadata[k1][k2][k3o]['last_event_timespan'] = abs((NOW - cash_out[-1]['date']).days)
            metadata[k1][k2][k3o]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]
    return metadata


def earnings(metadata, lst, key, value):
    k1 = 'savings'
    k2 = 'earnings'

    data = [d for d in lst if d[key] == value]
    if data:
        df = aggregate_dict_by_month(data, {'amount': ['count', 'sum']})
        metadata[k1][k2]['avg_monthly_count'] = df[('amount', 'count')].mean()
        metadata[k1][k2]['avg_monthly_value'] = df[('amount', 'sum')].mean()
        metadata[k1][k2]['last_event_timespan'] = abs((NOW - data[-1]['date']).days)
        metadata[k1][k2]['last_montly_event_value'] = df[('amount', 'sum')].values[-1]

        nd = NestedDict(metadata)
        keys = [k for k in nd.keys()]
        if (k1, 'cash_flow', 'deposits', 'avg_monthly_value') in keys:
            if (k1, 'cash_flow', 'withdrawals', 'avg_monthly_value') in keys:
                cash_flow = metadata[k1]['cash_flow']['deposits']['avg_monthly_value'] + \
                    metadata[k1]['cash_flow']['withdrawals']['avg_monthly_value']
            else:
                cash_flow = metadata[k1]['cash_flow']['deposits']['avg_monthly_value']
        else:
            cash_flow = metadata[k1]['cash_flow']['withdrawals']['avg_monthly_value']

        metadata[k1][k2]['avg_monthly_cash_flow'] = cash_flow
        metadata[k1][k2]['avg_monthly_return_pct'] = metadata[k1][k2]['avg_monthly_value'] / cash_flow
    return metadata


def cum_halves_list(start, size):
    lst = [start]
    v = start
    for n in range(size-2):
        v += (1-v)/2
        lst.append(v)
    lst.append(1)
    lst.reverse()
    return lst


def dot_product(l1, l2):
    return sum(map(mul, l1, l2))


def head_tail_list(lst):
    return lst[0], lst[-1]


def aggregate_currencies(ccy1, ccy2, fiats):
    ccy1 = {k: v[1] for (k, v) in ccy1.items()}
    ccy2 = {k: 1 for (k, v) in ccy2.items() if v == 0.01 or k in fiats}

    ccy1.update(ccy2)
    ccy1 = list(ccy1.keys())
    return ccy1


def immutable_array(arr):
    arr.flags.writeable = False
    return arr



def validate_txn_history(req_period, data):
    try:
        txn_history = data[0]['timespan']
        print(f'\033[36m  -> History:\t\t{txn_history}\033[0m')
        if txn_history >= req_period:
            return True
        else:
            return False
    except Exception:
        return False


def build_2d_matrix(size, scalars):
    '''
    build a simple 2D scoring matrix.
    Matrix axes growth rate is defined by a log in base 10 function
    '''
    matrix = np.zeros(size)
    scalars = [1 / n for n in scalars]

    for m in range(matrix.shape[0]):
        for n in range(matrix.shape[1]):
            matrix[m][n] = round(
                scalars[0] * np.log10(m + 1) + scalars[1] * np.log10(n + 1), 2
            )
    return matrix


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
