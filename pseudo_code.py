
def get_score( user_id ):
    credibility = calculate_credibility( user_id )
    wealth = calculate_wealth( user_id )
    traffic = calculate_traffic( user_id )
    stamina = calculate_stamina( user_id )
    mode_score = credibility + wealth + traffic + stamina
    return mode_score

def calculate_credibilty( user_id ):
    today_timestamp = datetime.now()
    oldest_transaction = api_first_transaction(user_id)
    time_difference = today_timestamp - oldest_transaction
    credibility_score = time_difference / 1000 
    return credibility_score

def calculate_wealth( user_id ):
    capital_now = api_eth_now(user_id)
    capital_now_adjusted = eth_now_adjusted(user_id)
    volume_per_transaction = calculate_avg_vole(user_id)
    wealth_score = capital_now + capital_now_adjusted + volume_per_transaction / 3000
    return wealth_score

def calculate_traffic( user_id ):
    total_debit_tx = api_debit_tx(user_id)
    total_credit_tx = api_credit_tx(user_id)
    clean_transaction = count_tx_greater_than_1eth(user_id)
    running_balance = api_eth_avg_vol(user_id)
    frequency = api_count_total_tx(user_id)
    traffic_score = (10 * total_debit_tx + 10 * total_credit_tx + 30 * clean_transaction + 5 * running_balance + 10 * frequency )/1000
    return traffic_score

def calculate_stamina( user_id ):
    stake_score = api_total_stake_vol(user_id) / api_total_stake_tx(user_id)
    swap_score = api_total_swap_vol(user_id) / api_total_swap_tx(user_id)
    method_count = stake_score + swap_score
    coins_count = api_total_coins(user_id)
    # Did the user lose money or gain money?
    dexterity = lifetime_balance_difference(user_id)
    stamina_score = method_count + coins_count + dexterity /3
    return stamina_score

user = 0x1337
user_score = get_score(user)
print(user_score)