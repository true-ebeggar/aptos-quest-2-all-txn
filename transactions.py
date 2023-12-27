from aptos_sdk.client import RestClient

from logger import setup_gay_logger
from constant import MAX_SLIPPAGE_PERCENT
from utils import get_apt_price, append_digit_to_integer

SLIPPAGE = (100 - MAX_SLIPPAGE_PERCENT) / 100
Z8 = 10**8
Z6 = 10**6
Rest_Client = RestClient("https://fullnode.mainnet.aptoslabs.com/v1")

def submit_and_log_transaction(account, payload, logger):
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")


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

def stake_APT(account, amount: int):
    logger = setup_gay_logger('stake_APT')

    if amount < 20000000:
        logger.error(f"Amount ({amount / Z8} ATP) less than required (0.2 APT)")
        return

    payload = {
        "function": "0x111ae3e5bc816a5e63c2da97d0aa3886519e0cd5e4b046659fa35796bd11542a::router::deposit_and_stake_entry",
        "type_arguments": [],
        "arguments": [
            str(amount),
            str(account.address())
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)

def register_gator_market_account(account):
    logger = setup_gay_logger('register_gator_market_account')

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::user::register_market_account",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            "7",
            "0"
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)

def deposit_zUSDC_to_gator(account, zUSDC_amount: int):
    logger = setup_gay_logger('deposit_zUSDC_to_gator')

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::user::deposit_from_coinstore",
        "type_arguments": [
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            "7",
            "0",
            str(zUSDC_amount)
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)

def swap_zUSDC_to_APT_via_gator(account):
    logger = setup_gay_logger('swap_zUSDC_to_APT_via_gator')

    payload = {
        "function": "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c::market::place_market_order_user_entry",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin",
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC"
        ],
        "arguments": [
            "7",
            "0x63e39817ec41fad2e8d0713cc906a5f792e4cd2cf704f8b5fab6b2961281fa11",
            False,
            "10000",
            3
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)

def swap_zUSDC_to_APT_via_pancakeswap(account, zUSDC_amount: int):
    logger = setup_gay_logger('swap_zUSDC_to_APT_via_pancakeswap')

    apt_price = get_apt_price()
    normalization = zUSDC_amount / Z6
    APT_ideal = normalization / apt_price
    APT_slip = APT_ideal * SLIPPAGE
    APT_slip_int = int(APT_slip * Z8)

    payload = {
        "function": "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfe19850fa::router::swap_exact_input",
        "type_arguments": [
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(zUSDC_amount),
            str(APT_slip_int)
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)

def swap_zUSDC_to_APT_via_sushisvap(account, zUSDC_amount: int):
    logger = setup_gay_logger('swap_zUSDC_to_APT_via_sushisvap')

    apt_price = get_apt_price()
    normalization = zUSDC_amount / Z6
    APT_ideal = normalization / apt_price
    APT_slip = APT_ideal * SLIPPAGE
    APT_slip_int = int(APT_slip * Z8)

    payload = {
        "function": "0x31a6675cbe84365bf2b0cbce617ece6c47023ef70826533bde5203d32171dc3c::router::swap_exact_input",
        "type_arguments": [
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(zUSDC_amount),
            str(APT_slip_int)
        ],
        "type": "entry_function_payload"
    }

    submit_and_log_transaction(account, payload, logger)
