from config.helper import *
from helpers.helper import *
from market.coinmarketcap import *
from validator.covalent import *
from helpers.metrics_covalent import *

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from support.schemas import KYC_Item

from dotenv import load_dotenv
from os import getenv
load_dotenv()


router = APIRouter(
    tags=['KYC Verification']
)


@router.post('/kyc', status_code=status.HTTP_200_OK, summary='Verify KYC')
async def credit_score_kyc(request: Request, item: KYC_Item):
    '''
    Verifies chosen account (Covalent) through set of rules to determine whether KYC or not.

    Input:
    - **chosen_validator [string]**: chosen validator
    - **coinmarketcap_key [string | Optional]**: coinmarketcap key
    - **eth_address [string | Optional]**: eth address
    - **covalent_key [string | Optional]**: covalentkey

    Output:
    - **[object]**: kyc verification
    '''

    try:
        print(f'\033[35;1m Receiving request from: {request.client.host}\033[0m')

        # configs
        print(f'\033[36m Accessing settings ...\033[0m')
        configs = read_config_file(0)
        if isinstance(configs, str):
            raise Exception(configs)

        thresholds = configs['minimum_requirements'][item.chosen_validator]['thresholds']

        # kyc models
        if item.chosen_validator == 'covalent':
            # data fetching
            print(f'\033[36m Reading data ...\033[0m')
            transactions = covalent_get_transactions(
                '1', item.eth_address, item.covalent_key, False, 500, 0)

            if isinstance(transactions, dict) and 'found_error' in transactions and transactions['found_error']:
                error = transactions['error_message']
                raise Exception(f'Unable to fetch transactions data: {error}')

            balances = covalent_get_balances_or_portfolio(
                '1', item.eth_address, 'balances_v2', item.covalent_key)

            if isinstance(balances, dict) and 'found_error' in balances and balances['found_error']:
                error = balances['error_message']
                raise Exception(f'Unable to fetch balances data: {error}')

            portfolio = covalent_get_balances_or_portfolio(
                '1', item.eth_address, 'portfolio_v2', item.covalent_key)

            if isinstance(portfolio, dict) and 'found_error' in portfolio and portfolio['found_error']:
                error = portfolio['error_message']
                raise Exception(f'Unable to fetch portfolio data: {error}')

            # verify kyc
            print(f'\033[36m Verifying KYC ...\033[0m')
            kyc_verified = covalent_kyc(transactions, balances, portfolio)

        # return success
        print(f'\033[35;1m Account has successfully been KYC verified.\033[0m')
        return {
            'endpoint': '/kyc',
            'status': 'success',
            'validator': item.chosen_validator,
            'kyc_verified': kyc_verified
        }

    except Exception as e:
        print(f'\033[35;1m Unable to complete KYC verification.\033[0m')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'endpoint': '/kyc',
                'status': 'error',
                'message': str(e),
            }
        )
