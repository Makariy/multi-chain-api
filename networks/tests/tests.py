from . import *  # Import fixtures
from base import (
    BaseNetwork,
    Wallet,
    Token
)

from utils import move_all_gas_funds, move_all_token_funds


def test_create_wallet(network: BaseNetwork):
    wallet = network.create_wallet()
    assert wallet.address
    assert wallet.secret_key
    assert wallet.network == network.name


def test_get_gas_balance(network: BaseNetwork, wallet: Wallet):
    gas = network.get_gas_balance(wallet)
    assert gas > 0


def test_get_gas_price(network: BaseNetwork):
    gas_price = network.get_gas_price()
    assert gas_price > 0


def test_token_balance(network: BaseNetwork, token: Token, wallet: Wallet):
    balance = network.get_token_balance(wallet, token)
    assert balance > 0


def test_transfer_gas(network: BaseNetwork, wallet: Wallet, temp_wallet: Wallet):
    real_balance = network.get_gas_balance(wallet)
    amount = real_balance // 50  # In case it fails, not to lose all the balance

    gas = network.get_gas_for_gas_transaction(
        wallet.address,
        temp_wallet.address,
        amount
    ) * network.get_gas_price()

    tx_hash = network.send_gas(
        wallet=wallet,
        address=temp_wallet.address,
        amount=amount - gas
    )
    network.await_transaction(tx_hash)

    new_main_wallet_balance = network.get_gas_balance(wallet)
    new_temp_wallet_balance = network.get_gas_balance(temp_wallet)

    assert round(new_temp_wallet_balance / (amount - gas))  # There could be some precision errors
    assert round(new_main_wallet_balance / (real_balance - amount - gas))  # There could be some precision errors

    # Return the gas
    tx_hash = move_all_gas_funds(network, temp_wallet, wallet.address)
    network.await_transaction(tx_hash)


def test_transfer_token(network: BaseNetwork, wallet: Wallet, temp_wallet: Wallet, token: Token):
    assert network.get_token_balance(temp_wallet, token) == 0

    main_wallet_balance = network.get_token_balance(wallet, token)
    amount = main_wallet_balance / 50  # In case it fails, not to lose all the balance

    tx_hash = network.send_token(
        wallet=wallet,
        token=token,
        address=temp_wallet.address,
        amount=amount
    )
    network.await_transaction(tx_hash)

    new_main_wallet_balance = network.get_token_balance(wallet, token)
    new_temp_wallet_balance = network.get_token_balance(temp_wallet, token)

    assert round(amount / new_temp_wallet_balance) == 1  # There could be some precision errors
    assert round(new_main_wallet_balance / (main_wallet_balance - amount)) == 1  # There could be some precision errors

    # Return the tokens
    tx_hash = move_all_token_funds(network, temp_wallet, wallet, token)
    network.await_transaction(tx_hash)

