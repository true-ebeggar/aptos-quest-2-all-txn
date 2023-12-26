import json
import requests
import random

from aptos_sdk.account import Account
from aptos_sdk.client import RestClient

from logger import setup_gay_logger
from constant import zUSDC_coin, MOD_coin, MAX_SLIPPAGE_PERCENT


SLIPPAGE = (100 - MAX_SLIPPAGE_PERCENT) / 100
Z8 = 10**8
Z6 = 10**6
Rest_Client = RestClient("https://fullnode.mainnet.aptoslabs.com/v1")

def get_apt_price():
    try:
        response = requests.get('https://app.merkle.trade/api/v1/summary/prices')
        for pair in response.json()["pairs"]:
            if pair["id"] == "APT_USD":
                APT_usd_price = pair["price"]
                return APT_usd_price
    except Exception:
        return None

def submit_and_log_transaction(account, payload, logger):
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")

def append_digit_to_integer(original_integer, digit_to_add):
    new_integer_string = str(original_integer) + str(digit_to_add)
    new_integer = int(new_integer_string)
    return new_integer

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

    submit_and_log_transaction(account, payload, logger)

def check_registration(address, to_check: str):
    logger = setup_gay_logger(f'check_<{to_check}>_registration')
    try:
        coin_type = f"0x1::coin::CoinStore<{to_check}>"
        url = f"https://fullnode.mainnet.aptoslabs.com/v1/accounts/{address}/resources?limit=9999"
        response = requests.get(url)
        # print(json.dumps(response.json(), indent=4))
        return any(item.get('type', '') == coin_type for item in response.json())
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

def stake_MOD(account, amount_MOD: int):
    logger = setup_gay_logger('deposit_MOD')

    payload = {
        "type": "entry_function_payload",
        "function": "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool_scripts::deposit_mod",
        "type_arguments": [
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool::Crypto"
        ],
        "arguments": [
            str(amount_MOD)
        ],
    }

    submit_and_log_transaction(account, payload, logger)

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

    submit_and_log_transaction(account, payload, logger)

def swap_APT_to_zUSDC_via_liquidswap(account, amount: int):
    logger = setup_gay_logger('swap_APT_to_zUSDC_via_liquidswap')

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

    submit_and_log_transaction(account, payload, logger)
def open_merkle_order(account, amount_zUSDC: int):
    # Fake tx, no actual position will be open

    logger = setup_gay_logger('open_merkle_order')

    leverage = 130
    position_size = leverage * amount_zUSDC
    if position_size <= 300000000:
        return None

    apt = int(get_apt_price() * Z8)
    margin_requirement = 1 / leverage
    liquidation_price = int(apt * (1 - margin_requirement))
    stop_loss_price = int(apt * (1 - 0.10 / leverage))
    take_profit_price = int(apt * (1 + 0.20 / leverage))


    payload = {
        "function": "0x5ae6789dd2fec1a9ec9cccfb3acaf12e93d432f0a3a42c92fe1a9d490b7bbc06::managed_trading::place_order_with_referrer",
        "type_arguments": [
            "0x5ae6789dd2fec1a9ec9cccfb3acaf12e93d432f0a3a42c92fe1a9d490b7bbc06::pair_types::APT_USD",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            str(position_size),
            str(amount_zUSDC),
            str(append_digit_to_integer(liquidation_price, 10)),
            True,
            True,
            True,
            str(append_digit_to_integer(stop_loss_price, 59)),
            str(append_digit_to_integer(take_profit_price, 60)),
            False,
            "0x0"
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)
