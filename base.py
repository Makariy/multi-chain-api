from typing import List, Dict, TypeAlias, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from decimal import Decimal


class Networks(Enum):
    BSC: str = "BSC"
    ETHEREUM: str = "ETH"


@dataclass
class Wallet:
    network: Networks
    address: str
    secret_key: str


@dataclass
class Token:
    network: Networks
    contract_address: str
    abi: List[Dict]
    name: str
    decimal_places: int  # No need in case of eth compatible


TXHash: TypeAlias = Any


class BaseNetwork(ABC):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @property
    @abstractmethod
    def name(self) -> Networks:
        pass

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
            amount: Decimal
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
    def await_transaction(self, tx_hash: TXHash):
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

