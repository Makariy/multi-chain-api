from typing import TypeAlias, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from decimal import Decimal

from exceptions import NotEnoughGas, NotEnoughTokenBalance
from providers import BaseProvider


class Networks(Enum):
    BSC: str = "BSC"
    ETHEREUM: str = "ETH"
    TRON: str = "TRON"


@dataclass
class Wallet:
    network: Networks
    address: str
    secret_key: str


@dataclass
class Token:
    network: Networks
    contract_address: str
    abi: Any
    name: str
    decimal_places: int  # No need in case of eth compatible


TXHash: TypeAlias = Any


class BaseNetwork(ABC):
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def _assert_wallet_has_enough_gas(self, wallet: Wallet, gas: int):
        current_balance = self.get_gas_balance(wallet)
        if current_balance + self.gas_error < gas:
            raise NotEnoughGas(f"Not enough gas to execute the transfer: "
                               f"{current_balance=} < {gas=}")

    def _assert_wallet_has_enough_tokens(self, wallet: Wallet, token: Token, amount: Decimal):
        current_balance = self.get_token_balance(wallet, token)
        if current_balance < amount:
            raise NotEnoughTokenBalance(f"Not enough token balance to execute the transfer: "
                                        f"{current_balance=} < {amount=}")

    @property
    @abstractmethod
    def name(self) -> Networks:
        pass

    @property
    def gas_error(self) -> int:
        return 0

    @abstractmethod
    def create_wallet(self) -> Wallet:
        pass

    @abstractmethod
    def get_gas_balance(self, wallet: Wallet) -> int:
        pass

    @abstractmethod
    def get_gas_price(self) -> int:
        pass

    @abstractmethod
    def get_gas_for_gas_transaction(
            self,
            address_from: str,
            address_to: str,
            amount: int
    ) -> int:
        pass

    @abstractmethod
    def get_gas_for_token_transaction(
            self,
            address_from: str,
            address_to: str,
            token: Token,
            amount: int
    ) -> int:
        pass

    @abstractmethod
    def get_token_balance(
            self,
            wallet: Wallet,
            token: Token
    ) -> Decimal:
        pass

    @abstractmethod
    def get_transaction_by_hash(self, tx_hash: TXHash):
        pass

    @abstractmethod
    def await_transaction(self, tx_hash: TXHash, timeout: float = 10 * 60):
        # Timeout in seconds
        pass

    @abstractmethod
    def send_gas(
            self,
            wallet: Wallet,
            address: str,
            amount: int
    ) -> TXHash:
        pass

    @abstractmethod
    def send_token(
            self,
            wallet: Wallet,
            token: Token,
            address: str,
            amount: Decimal,
    ) -> TXHash:
        pass

