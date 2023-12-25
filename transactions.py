import json
import requests

from aptos_sdk.account import Account
from aptos_sdk.client import RestClient

from logger import setup_gay_logger
from constant import zUSDC_coin, MOD_coin, MAX_SLIPPAGE_PERCENT


SLIPPAGE = (100 - MAX_SLIPPAGE_PERCENT) / 100
Z8 = 10**8
Z6 = 10**6
Rest_Client = RestClient("https://fullnode.mainnet.aptoslabs.com/v1")

def get_apt_price():
    token_name = "aptos"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_name}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    token_price_usd = data[token_name]['usd']
    return token_price_usd

def get_account_balance(client, account):
    logger = setup_gay_logger('get_account_balance')
    try:
        return int(client.account_balance(account_address=account.address()))
    except Exception as e:
        if "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>" in str(e):
            logger.critical("Account does not exist")
            return None
        else:
            logger.error("An unexpected error occurred.")
            return None

def swap_zUSDC_to_MOD(account, amount_zUSDC: int):
    logger = setup_gay_logger('swap_zUSDC_to_MOD')

    normalization = amount_zUSDC / Z6
    MOD_slip = normalization * SLIPPAGE
    MOD_slip_int = int(MOD_slip * Z8)

    payload = {
        "type": "entry_function_payload",
        "function": "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool_scripts::swap_exact_in",
        "type_arguments": [
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD"
        ],
        "arguments": [
            str(amount_zUSDC),
            str(MOD_slip_int)
        ],
    }
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")

def check_registration(address, to_check: str):
    logger = setup_gay_logger('check_zUSDC_registration')
    try:
        coin_type = f"0x1::coin::CoinStore<{to_check}>"
        url = f"https://fullnode.mainnet.aptoslabs.com/v1/accounts/{address}/resources?limit=9999"
        response = requests.get(url)
        # print(json.dumps(response.json(), indent=4))
        return any(item.get('type', '') == coin_type for item in response.json())
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

def register_coin(account, to_register: str):
    logger = setup_gay_logger(f'register_coin:<{to_register}>')

    payload = {
        "type": "entry_function_payload",
        "function": "0x1::managed_coin::register",
        "type_arguments": [
             to_register
        ],
        "arguments": []
    }

    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")

def swap_APT_to_zUSDC(account, amount: int):
    logger = setup_gay_logger('swap_APT_to_zUSDC')

    apt_price = get_apt_price()
    normalization = amount / Z8
    zUSDC_ideal = apt_price * normalization
    zUSDC_slip = zUSDC_ideal * SLIPPAGE
    zUSDC_slip_int = int(zUSDC_slip * Z6)

    payload = {
        "type": "entry_function_payload",
        "function": "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12::scripts_v2::swap",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12::curves::Uncorrelated"
        ],
        "arguments": [
            str(amount),
            str(zUSDC_slip_int)
        ],
    }
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")