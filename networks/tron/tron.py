from typing import Type
from decimal import Decimal
import time

from base import (
    BaseNetwork,
    Networks,
    Token,
    TXHash, Wallet
)

from tronpy import Tron, Contract
from tronpy.providers import HTTPProvider as TRONHTTPProvider
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionNotFound

from providers import BaseProvider
from providers.http_provider import HTTPProvider

from exceptions import ExternalError


def _convert_str_to_private_key(secret_key: str) -> PrivateKey:
    return PrivateKey(bytes.fromhex(secret_key))


class TronNetwork(BaseNetwork):
    name = Networks.TRON
    TRX_TO_SUN: int = 10 ** 6
    _GAS_LIMIT_FOR_SEND_GAS: int = 4 * 10 ** 5
    _GAS_LIMIT_FOR_SEND_TOKEN: int = 20 * 10 ** 6

    def __init__(self, provider: BaseProvider):
        super().__init__(provider)
        self._init_tron(provider)

    def _create_http_tron_provider(self, provider: HTTPProvider) -> Tron:
        tron_provider = TRONHTTPProvider(
            endpoint_uri=provider.endpoint,
            api_key=provider.api_key,
        )
        if provider.proxy:
            tron_provider.sess.proxies = provider.proxy.params

        return Tron(tron_provider)

    def _init_tron(self, provider: BaseProvider):
        if isinstance(provider, HTTPProvider):
            self._tron = self._create_http_tron_provider(provider)
        else:
            raise NotImplementedError(f"Provider {provider} is not implemented for {self.name}")

    def _get_contract_for_token(self, token: Token) -> Contract:
        return self._tron.get_contract(token.contract_address)

    def _assert_transaction_succeeded(self, tx_hash: TXHash):
        transaction = self.get_transaction_by_hash(tx_hash)
        statuses = transaction["ret"]
        if not statuses:
            raise ExternalError(f"No status was set for transaction {transaction}")

        status = transaction["ret"][-1]
        if not status.get("contractRet") in ["SUCCESS", "APPROVED"]:
            raise ExternalError(f"Transaction {transaction} has an unknown status")

    def create_wallet(self) -> Wallet:
        tron_wallet = self._tron.generate_address()
        wallet = Wallet(
            network=self.name,
            address=tron_wallet["base58check_address"],
            secret_key=tron_wallet["private_key"]
        )
        return wallet

    def get_gas_balance(self, wallet: Wallet) -> int:
        return int(self._tron.get_account_balance(wallet.address) * self.TRX_TO_SUN)

    def get_gas_price(self) -> int:
        return 1

    def get_gas_for_gas_transaction(self, address_from: str, address_to: str, amount: int) -> int:
        return self._GAS_LIMIT_FOR_SEND_GAS

    def get_gas_for_token_transaction(self, address_from: str, address_to: str, token: Token, amount: int) -> int:
        return self._GAS_LIMIT_FOR_SEND_TOKEN

    def get_token_balance(self, wallet: Wallet, token: Token) -> Decimal:
        contract = self._get_contract_for_token(token)
        return Decimal(contract.functions.balanceOf(wallet.address)) / Decimal(10 ** token.decimal_places)

    def get_transaction_by_hash(self, tx_hash: TXHash) -> dict:
        return self._tron.get_transaction(tx_hash)

    def await_transaction(self, tx_hash: TXHash, timeout: float = 20 * 60):
        start = time.time()
        while True:
            transaction = self.get_transaction_by_hash(tx_hash)
            try:
                return self._tron.get_transaction_info(transaction["txID"])
            except TransactionNotFound:
                if time.time() - start > timeout:
                    raise TransactionNotFound

                time.sleep(0.1)

    def send_gas(self, wallet: Wallet, address: str, amount: int) -> TXHash:
        gas_limit = self.get_gas_for_gas_transaction(wallet.address, address, amount)
        self._assert_wallet_has_enough_gas(wallet, amount + gas_limit)

        transaction = (
            self._tron.trx.transfer(wallet.address, address, amount)
            .fee_limit(gas_limit)
            .build()
            .sign(
                _convert_str_to_private_key(wallet.secret_key)
            )
        )
        tx_hash = transaction.broadcast().txid
        self._assert_transaction_succeeded(tx_hash)
        return tx_hash

    def send_token(
            self,
            wallet: Wallet,
            token: Token,
            address: str,
            amount: Decimal,
            gas_limit: int = None  # Optional
    ) -> TXHash:
        internal_amount = int(amount * 10 ** token.decimal_places)
        if not gas_limit:
            gas_limit = self.get_gas_for_token_transaction(
                wallet.address,
                address,
                token,
                internal_amount
            )

        self._assert_wallet_has_enough_gas(wallet, gas_limit)
        self._assert_wallet_has_enough_tokens(wallet, token, amount)

        contract = self._get_contract_for_token(token)
        transaction = (
            contract.functions.transfer(
                address,
                internal_amount
            )
            .with_owner(wallet.address)
            .fee_limit(gas_limit)
            .build().sign(_convert_str_to_private_key(wallet.secret_key))
        )
        tx_hash = transaction.broadcast().txid
        self._assert_transaction_succeeded(tx_hash)
        return tx_hash

