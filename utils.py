from base import (
    BaseNetwork,
    Wallet,
    Token,
    TXHash
)
from exceptions import NotEnoughGas, NotEnoughTokenBalance


def move_all_gas_funds(
        network: BaseNetwork,
        wallet: Wallet,
        address: str
) -> TXHash:
    balance = network.get_gas_balance(wallet)
    gas_for_transaction = network.get_gas_for_gas_transaction(wallet.address, address, balance)
    amount = balance - gas_for_transaction * network.get_gas_price()
    if amount < 0:
        raise NotEnoughGas(f"Wallet {wallet.address} does not have enough gas to move funds")

    tx_hash = network.send_gas(wallet, address, amount)
    return tx_hash


def move_all_token_funds(
        network: BaseNetwork,
        from_wallet: Wallet,
        to_wallet: Wallet,
        token: Token
):
    from_wallet_balance = network.get_token_balance(from_wallet, token)
    if from_wallet_balance == 0:
        raise NotEnoughTokenBalance(f"Wallet {from_wallet.address} does not have any tokens to move")

    gas = network.get_gas_for_token_transaction(
        from_wallet.address, to_wallet.address, token, from_wallet_balance
    ) * network.get_gas_price()

    # Move some gas to from_wallet to transact
    tx_hash = network.send_gas(to_wallet, from_wallet.address, gas)
    network.await_transaction(tx_hash)

    tx_hash = network.send_token(from_wallet, token, to_wallet.address, from_wallet_balance)
    return tx_hash
