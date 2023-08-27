from . import *  # Import fixtures
from networks.bsc.bsc import (
    BSCNetwork,
    Wallet,
    Token
)

from utils import move_all_gas_funds, move_all_token_funds


def test_bsc_create_wallet(bsc_network: BSCNetwork):
    wallet = bsc_network.create_wallet()
    assert wallet.address
    assert wallet.secret_key
    assert wallet.network == bsc_network.name


def test_bsc_get_gas_balance(bsc_network: BSCNetwork, wallet: Wallet):
    gas = bsc_network.get_gas_balance(wallet)
    assert gas > 0


def test_bsc_get_gas_price(bsc_network: BSCNetwork):
    gas_price = bsc_network.get_gas_price()
    assert gas_price > 0


def test_bsc_usdt_balance(bsc_network: BSCNetwork, usdt_token: Token, wallet: Wallet):
    balance = bsc_network.get_token_balance(wallet, usdt_token)
    assert balance > 0


def test_bsc_transfer_gas(bsc_network: BSCNetwork, wallet: Wallet, temp_wallet: Wallet):
    real_balance = bsc_network.get_gas_balance(wallet)
    amount = real_balance // 50  # In case it fails, not to lose all the balance

    gas = bsc_network.get_gas_for_gas_transaction(
        wallet.address,
        temp_wallet.address,
        amount
    ) * bsc_network.get_gas_price()

    tx_hash = bsc_network.send_gas(
        wallet=wallet,
        address=temp_wallet.address,
        amount=amount - gas
    )
    bsc_network.await_transaction(tx_hash)

    new_main_wallet_balance = bsc_network.get_gas_balance(wallet)
    new_temp_wallet_balance = bsc_network.get_gas_balance(temp_wallet)

    assert round(new_temp_wallet_balance / (amount - gas))  # There could be some precision errors
    assert round(new_main_wallet_balance / (real_balance - amount - gas))  # There could be some precision errors

    # Return the gas
    tx_hash = move_all_gas_funds(bsc_network, temp_wallet, wallet.address)
    bsc_network.await_transaction(tx_hash)


def test_bsc_transfer_token(bsc_network: BSCNetwork, wallet: Wallet, temp_wallet: Wallet, usdt_token: Token):
    assert bsc_network.get_token_balance(temp_wallet, usdt_token) == 0

    main_wallet_balance = bsc_network.get_token_balance(wallet, usdt_token)
    amount = main_wallet_balance / 50  # In case it fails, not to lose all the balance

    tx_hash = bsc_network.send_token(
        wallet=wallet,
        token=usdt_token,
        address=temp_wallet.address,
        amount=amount
    )
    bsc_network.await_transaction(tx_hash)

    new_main_wallet_balance = bsc_network.get_token_balance(wallet, usdt_token)
    new_temp_wallet_balance = bsc_network.get_token_balance(temp_wallet, usdt_token)

    assert round(amount / new_temp_wallet_balance) == 1  # There could be some precision errors
    assert round(new_main_wallet_balance / main_wallet_balance - amount) == 1  # There could be some precision errors

    # Return the tokens
    tx_hash = move_all_token_funds(bsc_network, temp_wallet, wallet, usdt_token)
    bsc_network.await_transaction(tx_hash)

