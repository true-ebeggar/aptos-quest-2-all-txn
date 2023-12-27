import json
import requests
from logger import setup_gay_logger

def get_apt_price():
    try:
        response = requests.get('https://app.merkle.trade/api/v1/summary/prices')
        for pair in response.json()["pairs"]:
            if pair["id"] == "APT_USD":
                APT_usd_price = pair["price"]
                return APT_usd_price
    except Exception:
        return None

def append_digit_to_integer(original_integer, digit_to_add):
    new_integer_string = str(original_integer) + str(digit_to_add)
    new_integer = int(new_integer_string)
    return new_integer

def get_account_balance(client, account):
    logger = setup_gay_logger('get_account_balance')
    max_retries = 10
    retries = 0

    while retries < max_retries:
        try:
            return int(client.account_balance(account_address=account.address()))
        except Exception as e:
            if "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>" in str(e):
                logger.critical("Account does not exist")
                return None
            else:
                retries += 1
                print(e)
                logger.error(f"An unexpected error occurred. Retry {retries}/{max_retries}")

    logger.error("Maximum retries reached. Unable to get account balance.")
    return None


def check_registration(address, to_check: str):
    logger = setup_gay_logger(f'check_<{to_check}>_registration')
    try:
        coin_type = f"0x1::coin::CoinStore<{to_check}>"
        url = f"https://fullnode.mainnet.aptoslabs.com/v1/accounts/{address}/resources?limit=9999"
        response = requests.get(url)
        # print(json.dumps(response.json(), indent=4)) # Optional: Print the response for debugging
        return any(item.get('type', '') == coin_type for item in response.json())
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

def get_coin_value(address, coin_type_to_check: str):
    logger = setup_gay_logger(f'get_coin_value:<{coin_type_to_check}>')
    try:
        coin_store_type = f"0x1::coin::CoinStore<{coin_type_to_check}>"
        url = f"https://fullnode.mainnet.aptoslabs.com/v1/accounts/{address}/resources?limit=9999"
        response = requests.get(url)
        # print(json.dumps(response.json(), indent=4))  # Optional: Print the response for debugging

        for item in response.json():
            if item.get('type', '') == coin_store_type:
                coin_data = item.get('data', {}).get('coin', {})
                coin_value = coin_data.get('value')
                return coin_value

        return None  # Return None if the coin type is not found
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None
