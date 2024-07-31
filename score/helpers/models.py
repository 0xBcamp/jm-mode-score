from helpers.metrics_covalent import *
from helpers.helper import *


# -------------------------------------------------------------------------- #
#                               Covalent Model                               #
# -------------------------------------------------------------------------- #

def covalent_credibility(txn, balances, portfolio, feedback, weights, params):
    feedback = fetch_covalent(txn, balances, portfolio, feedback)
    
    kyc, kyc_feedback = safe_calculation(credibility_kyc, txn, balances, feedback)
    inception, inception_feedback = safe_calculation(credibility_oldest_txn, txn, feedback, params)

    feedback.update(kyc_feedback)
    feedback.update(inception_feedback)

    a = list(weights.values())[:2]
    b = [kyc, inception]

    score = dot_product(a, b)

    return score, feedback

def covalent_wealth(txn, balances, feedback, weights, params, erc_rank):
    capital_now, cn_feedback = safe_calculation(wealth_capital_now, balances, feedback, params)
    capital_now_adj, cna_feedback = safe_calculation(wealth_capital_now_adjusted, balances, feedback, erc_rank, params)
    volume_per_txn, vpt_feedback = safe_calculation(wealth_volume_per_txn, txn, feedback, params)
    # staking_balance, sb_feedback = safe_calculation(wealth_staking_balance, staking_data, feedback, params)
    # yield_returns, yr_feedback = safe_calculation(wealth_yield_farming_returns, yield_data, feedback, params)

    feedback.update(cn_feedback)
    feedback.update(cna_feedback)
    feedback.update(vpt_feedback)
    # feedback.update(sb_feedback)
    # feedback.update(yr_feedback)

    a = list(weights.values())
    b = [capital_now, capital_now_adj, volume_per_txn]

    score = dot_product(a, b)

    return score, feedback

def covalent_traffic(txn, portfolio, feedback, weights, params, erc_rank):
    credit, credit_feedback = safe_calculation(traffic_cred_deb, txn, feedback, 'credit', params)
    debit, debit_feedback = safe_calculation(traffic_cred_deb, txn, feedback, 'debit', params)
    dust, dust_feedback = safe_calculation(traffic_dustiness, txn, feedback, params)
    run_balance, rb_feedback = safe_calculation(traffic_running_balance, portfolio, feedback, params, erc_rank)
    frequency, freq_feedback = safe_calculation(traffic_frequency, txn, feedback, params)

    feedback.update(credit_feedback)
    feedback.update(debit_feedback)
    feedback.update(dust_feedback)
    feedback.update(rb_feedback)
    feedback.update(freq_feedback)

    a = list(weights.values())[5:10]
    b = [credit, debit, frequency, dust, run_balance]

    score = dot_product(a, b)

    return score, feedback

def covalent_stamina(txn, balances, portfolio, feedback, weights, params, erc_rank):
    methods, methods_feedback = safe_calculation(stamina_methods_count, txn, feedback, params)
    coins, coins_feedback = safe_calculation(stamina_coins_count, balances, feedback, params, erc_rank)
    dexterity, dex_feedback = safe_calculation(stamina_dexterity, portfolio, feedback, params)


    feedback.update(methods_feedback)
    feedback.update(coins_feedback)
    feedback.update(dex_feedback)

    a = list(weights.values())[10:]
    b = [coins, methods, dexterity]

    score = dot_product(a, b)

    return score, feedback
