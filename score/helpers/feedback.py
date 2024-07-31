from market.coinmarketcap import *
import numpy as np
from icecream import ic
import json
import logging

# Some helper functions


def comma_separated_list(l):
    '''Takes a Pyhton list as input and returns a string of comma separated elements with AND at the end'''
    if len(l) == 1:
        msg = l[0]
    elif len(l) == 2:
        msg = l[0]+' and '+l[1]
    else:
        msg = ', '.join(l[:-1]) + ', and ' + l[-1]

    return msg


# -------------------------------------------------------------------------- #
#                                  Covalent                                  #
# -------------------------------------------------------------------------- #
def create_interpret_covalent():
    '''
   Description:
        Initializes a dict with a concise summary to communicate and interpret the NearOracle score.
        It includes the most important metrics used by the credit scoring algorithm (for Covalent).
    '''
    return {
        'score': {
            'score_exist': False,
            'points': None,
            'quality': None,
            'longevity_days': None,
            'cum_balance_now': None
        },
        'advice': {
            'credibility_error': False,
            'wealth_error': False,
            'traffic_error': False,
            'stamina_error': False
        }
    }


def interpret_score_covalent(score, feedback, score_range, quality_range):
    '''
    Description:
        returns a dict explaining the meaning of the numerical score

    Parameters:
        score (float): user's numerical score
        feedback (dict): score feedback, reporting stats on major Covalent metrics

    Returns:
        interpret (dict): dictionaries with the major contributing score metrics
    '''
    try:
        # Create 'interpret' dict to interpret the numerical score
        interpret = create_interpret_covalent()

        # Score
        if ('credibility' in feedback.keys() and
            feedback['credibility']['verified'] == False) or \
            ('fetch' in feedback.keys() and
             feedback['fetch']['JSONDecodeError'] == True):
            interpret['score']['points'] = 300
            interpret['score']['quality'] = 'very poor'

        else:
            interpret['score']['score_exist'] = True
            interpret['score']['points'] = int(score)
            interpret['score']['quality'] = quality_range[np.digitize(
                score, score_range, right=False)]

            if ('longevity_days' in list(feedback['credibility'].keys())) and \
                    (feedback['credibility']['longevity_days']):
                interpret['score']['longevity_days'] = feedback['credibility']['longevity_days']

            if 'cum_balance_now' in list(feedback['wealth'].keys()):
                interpret['score']['cum_balance_now'] = feedback['wealth']['cum_balance_now']

        # Advice
            if 'error' in list(feedback['credibility'].keys()):
                interpret['advice']['credibility_error'] = True

            if 'error' in list(feedback['wealth'].keys()):
                interpret['advice']['wealth_error'] = True

            if 'error' in list(feedback['traffic'].keys()):
                interpret['advice']['traffic_error'] = True

            if 'error' in list(feedback['stamina'].keys()):
                interpret['advice']['stamina_error'] = True

    except Exception as e:
        interpret = str(e)

    finally:
        return interpret


def qualitative_feedback_covalent(
        messages, score, feedback, score_range, quality_range, coinmarketcap_key):
    
    print(f'\033[36m in feedback covalent ...\033[0m')
    '''
    Description:
        A function to format and return a qualitative description
        of the numerical score obtained by the user

    Parameters:
        score (float): user's numerical score
        feedback (dict): score feedback, reporting stats on main Covalent metrics

    Returns:
        msg (str): qualitative message explaining the numerical score to the user.
        Return this message to the user in the front end of the Dapp
    '''

    # SCORE
    all_keys = [x for y in [list(feedback[k].keys())
                for k in feedback.keys()] for x in y]

    print(f'\033[36m all keys ...\033[0m')
    # Case #1: Failed to fetch data.
    # --> return fetch error when we did not
    # --> fetch any data and computed no score
    if 'fetch' in feedback.keys() and \
            feedback['fetch']['JSONDecodeError'] == True:
        msg = messages['fetcherror']
        print(f'\033[36m checking if error in msg ...\033[0m')
        return msg
    #print(f'\033[36m after Failed to fetch ...\033[0m')
    # Case #2: User not verified.
    # --> return fetch error when the user has
    # --> flow balance or no txn history
    elif 'credibility' in feedback.keys() and \
            feedback['credibility']['verified'] == False:
        msg = messages['failed']
        return msg

    #print(f'\033[36m After credibility ...\033[0m')
    # Case #3: a score exists.
    # --> return descriptive score feedback
    # Declare score variables
    else:
        quality = quality_range[np.digitize(score, score_range, right=False)]
        points = int(score)

        # Communicate the score
        #rate = coinmarketcap_rate(coinmarketcap_key, 'USD', 'MODE')
        msg = messages['success'].format(
            quality.upper(), points)


        # Covalent account duration
        if ('longevity_days' in all_keys):
            if ('cum_balance_now' in all_keys):
                lon = feedback['credibility']['longevity_days']
                bal = feedback['wealth']['cum_balance_now']
                msg = msg + f' Your Mode wallet address has been active for {lon} days '\
                    f'and your total balance across all cryptocurrencies is ${bal:,.0f} USD'
            else:
                bal = feedback['wealth']['cum_balance_now']
                msg = msg + \
                    f' Your Mode wallet address has been active for {bal} days'
        # Tot balance
        else:
            if ('cum_balance_now' in all_keys):
                bal = feedback['wealth']['cum_balance_now']
                msg = msg + \
                    f' Your total balance across all cryptocurrencies is ${bal} USD'

        # ADVICE
        # Case #1: there's error(s).
        # Either some functions broke or data is missing.
        if 'error' in all_keys:
            metrics_w_errors = [k for k in feedback.keys(
            ) if 'error' in list(feedback[k].keys())]
            err = comma_separated_list(metrics_w_errors)
            msg = msg + f'. An error occurred while computing the score metric called {err}. ' \
                f'As a result, your score was rounded down. Try to log into MetaMask again later'
        return msg + '.'

def generate_recommendations(feedback, score):
    try:
        recommendations = {
            "credibility": [],
            "wealth": [],
            "traffic": [],
            "stamina": []
        }
        
        # Credibility recommendations
        try:
            longevity_days = feedback.get('credibility', {}).get('longevity_days', 0)
            if longevity_days < 180:
                recommendations["credibility"].append({
                    "message": "Consider maintaining your wallet activity for a longer period to improve your credibility score.",
                    "current_value": longevity_days,
                    "target_value": 180
                })
        except KeyError as e:
            logging.warning(f"KeyError in credibility recommendation: {str(e)}")
        
        # Wealth recommendations
        try:
            cum_balance_now = feedback.get('wealth', {}).get('cum_balance_now', 0)
            if cum_balance_now < 1000:
                recommendations["wealth"].append({
                    "message": "Increasing your overall balance across cryptocurrencies could improve your wealth score.",
                    "current_value": cum_balance_now,
                    "target_value": 1000
                })
        except KeyError as e:
            logging.warning(f"KeyError in wealth recommendation: {str(e)}")
        
        # Traffic recommendations
        try:
            txn_frequency = float(feedback.get('traffic', {}).get('txn_frequency', '0').split()[0])
            if txn_frequency < 1:
                recommendations["traffic"].append({
                    "message": "Increasing the frequency of your transactions may improve your traffic score.",
                    "current_value": txn_frequency,
                    "target_value": 1
                })
        except (KeyError, ValueError) as e:
            logging.warning(f"Error in traffic recommendation: {str(e)}")
        
        # Stamina recommendations
        try:
            coins_count = feedback.get('stamina', {}).get('coins_count', 0)
            if coins_count < 3:
                recommendations["stamina"].append({
                    "message": "Holding a wider variety of cryptocurrencies could enhance your stamina score.",
                    "current_value": coins_count,
                    "target_value": 3
                })
        except KeyError as e:
            logging.warning(f"KeyError in stamina recommendation: {str(e)}")
        
        # Convert to JSON string
        # recommendations_json = json.dumps(recommendations, indent=2)
        
        return recommendations
    
    except Exception as e:
        logging.error(f"Unexpected error in generate_recommendations: {str(e)}")
        return json.dumps({"error": "An unexpected error occurred while generating recommendations."}) 

