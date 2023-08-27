from typing import Dict, Tuple, Union
from web3 import HTTPProvider, Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware

from eth_typing.evm import ChecksumAddress
from eth_account.datastructures import SignedTransaction


from decimal import Decimal

from base import (
    Networks,
    BaseNetwork,
    Wallet,
    Token,
    TXHash
)
from exceptions import NotEnoughGas, NotEnoughTokenBalance

import logging


logger = logging.getLogger(__name__)


def convert_addresses_to_checksum(w3: Web3, *addresses) -> Union[ChecksumAddress, Tuple[ChecksumAddress, ...]]:
    if len(addresses) == 1:
        return w3.to_checksum_address(addresses[0])
    return tuple(w3.to_checksum_address(address) for address in addresses)


class BSCNetwork(BaseNetwork):
    name = Networks.BSC
    _ETH_TO_WEI = 10 ** 18

    def __init__(self, *args, **kwargs):
        # endpoint="https://bsc-dataseed1.binance.org/"  Mainnet
        # endpoint="https://data-seed-prebsc-1-s1.binance.org:8545" Testnet
        super().__init__(*args, **kwargs)
        self._w3 = self._init_w3()

    def _init_w3(self) -> Web3:
        w3 = Web3(HTTPProvider(self.endpoint))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject middleware for Goerli
        return w3

    def _create_contract_from_token(self, token: Token) -> Contract:
        contract_address = convert_addresses_to_checksum(self._w3, token.contract_address)
        return self._w3.eth.contract(contract_address, abi=token.abi)

    def _create_transfer_contract(self, token: Token, address_checksum: str, token_wei: int):
        contract = self._create_contract_from_token(token)
        transfer = contract.functions.transfer(address_checksum, token_wei)
        return transfer

    def _assert_wallet_has_enough_gas(self, wallet: Wallet, gas: int):
        current_balance = self.get_gas_balance(wallet)
        if current_balance < gas:
            raise NotEnoughGas(f"Not enough gas to execute the transfer: "
                               f"{current_balance=} < {gas=}")

    def _assert_wallet_has_enough_tokens(self, wallet: Wallet, token: Token, amount: Decimal):
        current_balance = self.get_token_balance(wallet, token)
        if current_balance < amount:
            raise NotEnoughTokenBalance(f"Not enough token balance to execute the transfer: "
                                        f"{current_balance=} < {amount=}")

    def _sign_transaction(self, wallet: Wallet, transaction_data: Dict) -> SignedTransaction:
        return self._w3.eth.account.sign_transaction(
            transaction_data,
            wallet.secret_key
        )

    def create_wallet(self) -> Wallet:
        w3_wallet = self._w3.eth.account.create()
        return Wallet(
            secret_key=w3_wallet.key,
            address=w3_wallet.address,
            network=self.name
        )

    def get_nonce(self, address_checksum: ChecksumAddress) -> int:
        return self._w3.eth.get_transaction_count(address_checksum)

    def get_gas_price(self) -> int:
        return self._w3.eth.gas_price

    def get_gas_for_gas_transaction(self, address_from: str, address_to: str, amount: int) -> int:
        return self._w3.eth.estimate_gas({
            "from": address_from,
            "to": address_to,
            "amount": amount
        })

    def get_gas_for_token_transaction(
            self,
            address_from: str,
            address_to: str,
            token: Token,
            amount: Decimal
    ) -> int:
        token_wei = int(amount * (10 ** token.decimal_places))
        transfer = self._create_transfer_contract(token, address_to, token_wei)
        return transfer.estimate_gas({"from": address_from})

    def get_gas_balance(self, wallet: Wallet) -> int:
        address_checksum = convert_addresses_to_checksum(self._w3, wallet.address)
        return self._w3.eth.get_balance(address_checksum)

    def get_token_balance(
            self,
            wallet: Wallet,
            token: Token,
    ) -> Decimal:
        contract = self._create_contract_from_token(token)
        balance = contract.functions.balanceOf(wallet.address).call()
        decimal_places = contract.functions.decimals().call()
        return Decimal(balance) / Decimal(10 ** decimal_places)

    def await_transaction(self, tx_hash: TXHash):
        return self._w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_transaction_by_hash(self, tx_hash: TXHash):
        transaction = self._w3.eth.get_transaction(tx_hash)
        return transaction

    def send_gas(
            self,
            wallet: Wallet,
            address: str,
            amount: int
    ) -> TXHash:
        wallet_address_checksum, address_checksum = convert_addresses_to_checksum(
            self._w3,
            wallet.address, address
        )

        gas = self.get_gas_for_gas_transaction(wallet_address_checksum, address_checksum, amount)
        gas_price = self.get_gas_price()

        self._assert_wallet_has_enough_gas(wallet, gas * gas_price + amount)

        transaction_data = {
            "from": wallet_address_checksum,
            "to": address_checksum,
            "value": amount,
            "gas": gas,
            "gasPrice": gas_price,
            "nonce": self.get_nonce(wallet_address_checksum)
        }
        signed_transaction = self._sign_transaction(wallet, transaction_data)
        return self._w3.eth.send_raw_transaction(signed_transaction["rawTransaction"])

    def send_token(
            self,
            wallet: Wallet,
            token: Token,
            address: str,
            amount: Decimal,
    ) -> TXHash:
        self._assert_wallet_has_enough_tokens(wallet, token, amount)

        wallet_address_checksum, address_checksum = convert_addresses_to_checksum(
            self._w3,
            wallet.address, address
        )

        token_wei = int(amount * (10 ** token.decimal_places))
        gas = self.get_gas_for_token_transaction(wallet_address_checksum, address_checksum, token, amount)
        gas_price = self.get_gas_price()
        self._assert_wallet_has_enough_gas(wallet, gas * gas_price)

        transfer = self._create_transfer_contract(token, address_checksum, token_wei)
        transaction_data = transfer.build_transaction({
            "nonce": self.get_nonce(wallet_address_checksum),
            "gas": gas,
            "gasPrice": gas_price
        })
        signed_transaction_data = self._sign_transaction(wallet, transaction_data)

        return self._w3.eth.send_raw_transaction(signed_transaction_data["rawTransaction"])
