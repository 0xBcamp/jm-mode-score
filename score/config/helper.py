from os import path
import json


def read_config_file():
    '''
    Returns all data stored in the config.json file as a dict
    '''
    try:
        config_file = path.join(path.dirname(__file__), 'config.json')

        with open(config_file) as f:
            data = json.load(f)['data']
            data = [d for d in data][0]

        return data

    except OSError:
        return 'Unable to find config.json'

    except Exception:
        return 'Loan amount requested is over the limit.'


def read_models_and_metrics(d):
    '''
    Returns 2 distinct dict objects:
        - all metrics and their associated weights
        - all functions (within each metric) and their associated weights
    '''
    keys = [*d]
    values = list(d.values())

    model_values = [d['weight'] for d in values]
    models = dict(zip(keys, model_values))

    metric_values = [d['metrics'] for d in values]
    metrics = {k: v for d in metric_values for k, v in d.items()}

    return models, metrics


def read_model_penalties(d):
    '''
    Returns a dict with model metrics and their associated penalty values
    '''
    keys = [*d]
    values = list(d.values())

    model_values = [d['penalty_weight'] for d in values]
    models = dict(zip(keys, model_values))

    return models


def create_feedback(models):
    '''
    Returns a dict of empty dict for each metric
    '''
    return {k: {} for k, v in models.items()}
