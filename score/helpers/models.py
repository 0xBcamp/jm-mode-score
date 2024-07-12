from helpers.metrics_covalent import *
from helpers.helper import *


# -------------------------------------------------------------------------- #
#                               Covalent Model                               #
# -------------------------------------------------------------------------- #


def covalent_credibility(txn, balances, portfolio, feedback, weights, params):

    feedback = fetch_covalent(txn, balances, portfolio, feedback)
    kyc, feedback = credibility_kyc(txn, balances, feedback)
    inception, feedback = credibility_oldest_txn(txn, feedback, params)

    a = list(weights.values())[:2]
    b = [kyc, inception]

    score = dot_product(a, b)

    return score, feedback


def covalent_wealth(txn, balances, feedback, weights, params, erc_rank):

    capital_now, feedback = wealth_capital_now(balances, feedback, params)
    capital_now_adj, feedback = wealth_capital_now_adjusted(balances, feedback, erc_rank, params)
    volume_per_txn, feedback = wealth_volume_per_txn(txn, feedback, params)

    a = list(weights.values())[2:5]
    b = [capital_now, capital_now_adj, volume_per_txn]

    score = dot_product(a, b)

    return score, feedback