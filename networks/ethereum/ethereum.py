from typing import Dict, Tuple, Union

from web3 import Web3
from web3 import HTTPProvider as W3HTTPProvider
from web3.contract import Contract
from web3.middleware import geth_poa_middleware

from eth_typing.evm import ChecksumAddress
from eth_account.datastructures import SignedTransaction

from providers import BaseProvider
from providers.http_provider import HTTPProvider

from decimal import Decimal

from base import (
    Networks,
    BaseNetwork,
    Wallet,
    Token,
    TXHash
)

from .middleware import rps_limit_middleware
from .provider_params import ETHProviderExtra

import logging


logger = logging.getLogger(__name__)


def convert_addresses_to_checksum(w3: Web3, *addresses) -> Union[ChecksumAddress, Tuple[ChecksumAddress, ...]]:
    if len(addresses) == 1:
        return w3.to_checksum_address(addresses[0])
    return tuple(w3.to_checksum_address(address) for address in addresses)


class EthereumNetwork(BaseNetwork):
    name = Networks.ETHEREUM
    ETH_TO_WEI = 10 ** 18
    gas_error = 100_000

    def __init__(self, provider: BaseProvider):
        super().__init__(provider)
        self._init_w3(provider)

    def _create_middleware(self, provider: HTTPProvider):
        rps_limit = 0.3
        sleep_time = 0.1
        if provider.extra and isinstance(provider.extra, ETHProviderExtra):
            rps_limit = provider.extra.rps_limit
            sleep_time = provider.extra.sleep_time

        return rps_limit_middleware(
            rps_limit=rps_limit,
            sleep_time=sleep_time
        )

    def _create_http_w3_provider(self, provider: HTTPProvider) -> Web3:
        w3_provider = W3HTTPProvider(
            endpoint_uri=provider.endpoint
        )
        w3 = Web3(w3_provider)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject middleware for Goerli
        w3.middleware_onion.add(
            self._create_middleware(provider)
        )
        return w3

    def _init_w3(self, provider: BaseProvider):
        if isinstance(provider, HTTPProvider):
            self._w3 = self._create_http_w3_provider(provider)
        else:
            raise NotImplementedError(f"Provider {provider} is not implemented for {self.name}")

    def _create_contract_from_token(self, token: Token) -> Contract:
        contract_address = convert_addresses_to_checksum(self._w3, token.contract_address)
        return self._w3.eth.contract(contract_address, abi=token.abi)

    def _create_transfer_contract(self, token: Token, address_checksum: str, token_wei: int):
        contract = self._create_contract_from_token(token)
        transfer = contract.functions.transfer(address_checksum, token_wei)
        return transfer

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

    def await_transaction(self, tx_hash: TXHash, timeout=1000, poll_latency=2):
        return self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout, poll_latency=poll_latency)

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
