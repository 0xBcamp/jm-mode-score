from helpers.models import *
from helpers.helper import *


def covalent_score(score_range, feedback, model_weights, metric_weights, params, erc_rank, txn, balances, portfolio):
    try:
        validate_data(txn, 'transaction')
        validate_data(balances, 'balance')
        validate_data(portfolio, 'portfolio')
    except ValueError as e:
        feedback['validation_error'] = str(e)
        return score_range[0], feedback  # Return minimum score if validation fails

    params = covalent_params(params, score_range)

    credibility, cred_feedback = safe_calculation(covalent_credibility, txn, balances, portfolio, feedback, metric_weights, params)
    wealth, wealth_feedback = safe_calculation(covalent_wealth, txn, balances, feedback, metric_weights, params, erc_rank)
    traffic, traffic_feedback = safe_calculation(covalent_traffic, txn, portfolio, feedback, metric_weights, params, erc_rank)
    stamina, stamina_feedback = safe_calculation(covalent_stamina, txn, balances, portfolio, feedback, metric_weights, params, erc_rank)

    feedback.update(cred_feedback)
    feedback.update(wealth_feedback)
    feedback.update(traffic_feedback)
    feedback.update(stamina_feedback)

    a = list(model_weights.values())
    b = [credibility, wealth, traffic, stamina]

    head, tail = head_tail_list(score_range)
    score = head + (tail - head) * (dot_product(a, b))

    return score, feedback

"""
def covalent_score(score_range, feedback, model_weights, metric_weigths, params, erc_rank, txn, balances, portfolio):

    params = covalent_params(params, score_range)

    credibility, feedback = covalent_credibility(txn, balances, portfolio, feedback, metric_weigths, params)
    wealth, feedback = covalent_wealth(txn, balances, feedback, metric_weigths, params, erc_rank)
    traffic, feedback = covalent_traffic(txn, portfolio, feedback, metric_weigths, params, erc_rank)
    stamina, feedback = covalent_stamina(txn, balances, portfolio, feedback, metric_weigths, params, erc_rank)

    a = list(model_weights.values())
    b = [credibility, wealth, traffic, stamina]

    head, tail = head_tail_list(score_range)
    score = head + (tail - head) * (dot_product(a, b))

    return score, feedback
"""