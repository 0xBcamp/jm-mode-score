import numpy as np
from datetime import datetime

NOW = datetime.now().date()

# -------------------------------------------------------------------------- #
#                               Helper Functions                             #
# -------------------------------------------------------------------------- #


def swiffer_duster(txn, feedback):
    '''
    Description:
        remove 'dust' transactions (i.e., transactions with less than $0.1 in spot fiat value get classified as dust) and
        keep only 'successful' transactions (i.e., transactions that got completed).

    Parameters:
        txn (dict): Covalent class A endpoint 'transactions_v2'
        feedback (dict): score feedback

    Returns:
        txn (dict): formatted txn data containing only successful and non-dusty transactions
    '''
    try:
        # keep only transactions that are successful and have a value > 0
        if txn['quote_currency'] == 'USD':
            txn['items'] = [t for t in txn['items']
                            if t['successful'] and t['value_quote'] > 0]

            if txn['items']:
                return txn
            else:
                raise Exception("txn data should be a dict, but is NoneType")
        else:
            raise Exception("quote_currency should be USD, but it isn't")

    except Exception as e:
        feedback['fetch'][swiffer_duster.__name__] = str(e)


def purge_portfolio(portfolio, feedback):
    '''
    Description:
        remove 'dusty' tokens from portfolio. That is, we consider only those tokens
        that had a closing day balance of >$50 for at least 3 days in the last month

    Parameters:
        portfolio (dict): Covalent class A endpoint 'portfolio_v2'
        feedback (dict): score feedback

    Returns:
        portfolio (dict): purged portfolio without dusty tokens
    '''
    try:
        # ensure the quote currency is USD. If it isn't, then raise an exception
        if portfolio['quote_currency'] != 'USD':
            raise Exception('quote_currency should be USD')
        else:
            counts = list()
            for a in portfolio['items']:
                count = 0
                for b in a['holdings']:
                    if b['close']['quote'] != None:
                        if b['close']['quote'] > 50:
                            count += 1
                        # exist the loop as soon as the count exceeds 3
                        if count > 2:
                            break
                counts.append(count)

            # remove dusty token from the records
            for i in reversed(range(len(counts))):
                if counts[i] < 3:
                    portfolio['items'].pop(i)

        return portfolio

    except Exception as e:
        feedback['fetch'][purge_portfolio.__name__] = str(e)


def top_erc_only(data, feedback, top_erc):
    '''
    Description:
        filter the Covalent API data by keeping only the assets in the ETH
        wallet address which are top ranked on Coinmarketcap as ERC20 tokens

    Parameters:
        data (dict): can be either the 'balances_v2' or the 'portfolio_v2' Covalent class A endpoint
        feedback (dict): score feedback
        top_erc (list): list of ERC tokens ranked highest on Coinmarketcap

    Returns:
        data (dict): containing only top ERC tokens. All other tokens will NOT
        count toward the credit score and are disregarded altogether
    '''
    try:
        skimmed = list()
        for b in data['items']:
            if b['contract_ticker_symbol'] in top_erc:
                skimmed.append(b)

        data['items'] = skimmed
        return data

    except Exception as e:
        feedback['fetch'][top_erc_only.__name__] = str(e)


def covalent_kyc(txn, balances, portfolio):
    '''
    Description:
        returns True if the oracle believes this is a legitimate user
        with some credible history. Returns False otherwise

    Parameters:
        txn (dict): Covalent class A endpoint 'transactions_v2'
        balances (dict): Covalent class A endpoint 'balances_v2'
        portfolio (dict): Covalent class A endpoint 'portfolio_v2'

    Returns:
        (boolean): True if user is legitimate and False otherwise
    '''
    try:
        oldest = datetime.strptime(
            txn['items'][-1]['block_signed_at'].split('T')[0], '%Y-%m-%d').date()
        how_long = (NOW - oldest).days

        # Assign max score as long as the user owns a
        # tot balance > $150, a credible transaction history,
        # a portfolio, and a wallet opened > 3 months ago
        if txn['items']\
            and portfolio['items']\
                and sum([b['quote'] for b in balances['items']]) > 150\
            and how_long >= 90:
            return True
        else:
            return False

    except Exception as e:
        return str(e)


def fetch_covalent(txn, balances, portfolio, feedback):
    '''
    Description:
        checks whether Covalent data was fetched correctly, without errors

    Parameters:
        balances (dict): Covalent class A endpoint 'balances_v2'
        txn (dict): Covalent class A endpoint 'transactions_v2'
        portfolio (dict): Covalent class A endpoint 'portfolio_v2'
        feedback (dict): score feedback

    Returns:
        feedback (dict): update 'fetch' key in feedback
    '''
    for x in [txn, balances, portfolio]:
        if 'JSONDecodeError' in x:
            feedback['fetch']['JSONDecodeError'] = True
        else:
            feedback['fetch']['JSONDecodeError'] = False
    return feedback


# -------------------------------------------------------------------------- #
#                            Metric #1 Credibility                           #
# -------------------------------------------------------------------------- #
def credibility_kyc(txn, balances, feedback):
    '''
    Description:
        checks whether an ETH wallet address has legitimate transaction history and active balances

    Parameters:
        txn (dict): Covalent class A endpoint 'transactions_v2'
        balances (dict): Covalent class A endpoint 'balances_v2'
        feedback (dict): score feedback

    Returns:
        score (float): 1 if KYC'ed and 0 otherwise
        feedback (dict): updated score feedback
    '''
    try:
        # Assign max score as long as the user owns a
        # non-zero balance and a credible transaction history
        if txn['items'] and sum([b['quote'] for b in balances['items']]) > 10:
            score = 1
            feedback['credibility']['verified'] = True
        else:
            score = 0
            feedback['credibility']['verified'] = False

    except Exception as e:
        score = 0
        feedback['credibility']['error'] = str(e)

    finally:
        return score, feedback


def credibility_oldest_txn(txn, feedback, params):
    '''
    Description:
        reads the date of the oldest recorded transaction, and rewards a score accondingly

    Parameters:
        txn (dict): Covalent class A endpoint 'transactions_v2'
        feedback (dict): score feedback
        fico_medians (array): score bins
        duration (array): account duration bins (days)

    Returns:
        score (float): points scored for longevity of ETH wallet address
        feedback (dict): updated score feedback
    '''
    try:
        oldest = datetime.strptime(
            txn['items'][-1]['block_signed_at'].split('T')[0], '%Y-%m-%d').date()
        how_long = (NOW - oldest).days

        score = params['fico_medians'][np.digitize(how_long, params['duration'], right=True)]
        feedback['credibility']['longevity_days'] = how_long

    except Exception as e:
        score = 0
        feedback['credibility']['error'] = str(e)

    finally:
        return score, feedback


# -------------------------------------------------------------------------- #
#                              Metric #2 Wealth                              #
# -------------------------------------------------------------------------- #
def wealth_capital_now(balances, feedback, params):
    '''
    Description:
        returns score based on total volume of token owned (USD) now
        across ALL tokens owned (regardless fo their Coinmarketcap ranking)

    Parameters:
        balances (dict): Covalent class A endpoint 'balances_v2'
        feedback (dict): score feedback
        fico_medians (array): score bins
        volume_now (array): bins for the total token volume owned now

    Returns:
        score (float): points for cumulative balance now
        feedback (dict): updated score feedback
    '''
    try:
        if balances['quote_currency'] == 'USD':
            total = sum([b['quote'] for b in balances['items']])
            if total == 0:
                score = 0
            else:
                score = params['fico_medians'][np.digitize(
                    total, params['volume_now'], right=True)]
            feedback['wealth']['cum_balance_now'] = round(total, 2)
        else:
            raise Exception('quote_currency should be USD')

    except Exception as e:
        score = 0
        feedback['wealth']['error'] = str(e)

    finally:
        return score, feedback


def wealth_capital_now_adjusted(balances, feedback, erc_rank, params):
    '''
    Description:
        adjusted tot balance of token owned (USD). Accounts for the Coinmarketcap ranking of the token owned

    Parameters:
        balances (dict): Covalent class A endpoint 'balances_v2'
        feedback (dict): score feedback
        erc_rank (dict): ERC tokens and their associated Coinmarketcap rank
        fico_medians (array): score bins
        volume_now (array): bins for the total token volume owned now

    Returns:
        score (float): points for cumulative balance now (adjusted)
        feedback (dict): updated score feedback
    '''
    try:
        # Keep only balances data of top rankes ERC tokens
        top_erc = list(erc_rank.keys())
        wealth_capital_now_adjusted.top = top_erc_only(balances, feedback, top_erc)

        total = sum([b['quote'] for b in wealth_capital_now_adjusted.top['items']])
        if total == 0:
            score = 0
            feedback['wealth']['cum_balance_now_adjusted'] = 0
        else:
            adjusted_balance = 0
            for b in wealth_capital_now_adjusted.top['items']:
                balance = b['quote']
                ticker = b['contract_ticker_symbol']
                # multiply the balance owned per token by a weight inversely
                # proportional to that token's ranking on Coinmarketcap
                penalty = np.e**(erc_rank[ticker]**(1/3.5))
                adjusted_balance += round(1 - penalty / 100, 2) * balance

                score = params['fico_medians'][np.digitize(
                    adjusted_balance, params['volume_now'], right=True)]
                feedback['wealth']['cum_balance_now_adjusted'] = round(
                    adjusted_balance, 2)

    except Exception as e:
        score = 0
        feedback['wealth']['error'] = str(e)

    finally:
        return score, feedback


def wealth_volume_per_txn(txn, feedback, params):
    '''
    Description:
       returns a score for the avg volume per transaction

    Parameters:
        txn (dict): Covalent class A endpoint 'transactions_v2'
        feedback (dict): score feedback
        fico_medians (array): score bins
        volume_per_txn (array): bins for the average volume traded on each transaction

    Returns:
        score (float): volume for each performed transactions
        feedback (dict): updated score feedback
    '''
    try:
        # remove 'dust' transactions from your dataset
        txn = swiffer_duster(txn, feedback)
        if txn['items']:
            volume = 0
            for t in txn['items']:
                volume += t['value_quote']
            volume_avg = volume/len(txn['items'])

            score = params['fico_medians'][np.digitize(
                volume_avg, params['volume_per_txn'], right=True)]
            feedback['wealth']['avg_volume_per_txn'] = round(volume_avg, 2)

        else:
            score = 0
            feedback['wealth']['avg_volume_per_txn'] = 0

    except Exception as e:
        score = 0
        feedback['wealth']['error'] = str(e)

    finally:
        return score, feedback
