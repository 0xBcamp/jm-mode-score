from helpers.models import *
from helpers.helper import *

def covalent_score(score_range, feedback, model_weights, metric_weigths, params, erc_rank, txn, balances, portfolio):

    params = covalent_params(params, score_range)

    credibility, feedback = covalent_credibility(txn, balances, portfolio, feedback, metric_weigths, params)
    wealth, feedback = covalent_wealth(txn, balances, feedback, metric_weigths, params, erc_rank)
   
    a = list(model_weights.values())
    b = [credibility, wealth] #[credibility, wealth, traffic, stamina]

    head, tail = head_tail_list(score_range)
    score = head + (tail - head) * (dot_product(a, b))

    return score, feedback
