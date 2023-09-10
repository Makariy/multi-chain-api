import pytest
from networks.tron.tron import TronNetwork
from tronpy.providers import HTTPProvider

from base import Wallet, Networks, Token


@pytest.fixture
def network():
    return TronNetwork(
        provider=HTTPProvider(
            "https://nile.trongrid.io",
            api_key="53902d63-9be9-4720-aa36-46af9d36e489",
        ),
        network="nile"
    )


@pytest.fixture
def wallet():
    return Wallet(
        network=Networks.TRON,
        address="TUKAdHuM3LnQydyc6a1DvFirRmzsnT8rv6",
        secret_key="6072b6397483e7fc4e414252f8e89af1580c7d3c698e38c713991439b5ee81d0"
    )


@pytest.fixture
def temp_wallet():
    return Wallet(
        network=Networks.TRON,
        address="TUDCQfpCBo5sFUbN7N2Z4W7CpnXgdrw53D",
        secret_key="c3b3ec9b8b39518939b22996b682a21ca7e5a1fafb4a1b5fdcee4c5d71c84a2d"
    )


@pytest.fixture
def token():
    return Token(
        network=Networks.TRON,
        contract_address="TF17BgPaZYbz8oxbjhriubPDsA7ArKoLX3",
        abi={"entrys":[{"outputs":[{"type":"string"}],"constant":True,"name":"name","stateMutability":"View","type":"Function"},{"name":"stop","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"bool"}],"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"owner_","type":"address"}],"name":"setOwner","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"uint256"}],"constant":True,"name":"totalSupply","stateMutability":"View","type":"Function"},{"outputs":[{"type":"bool"}],"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"uint256"}],"constant":True,"name":"decimals","stateMutability":"View","type":"Function"},{"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"mint","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"wad","type":"uint256"}],"name":"burn","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"uint256"}],"constant":True,"inputs":[{"name":"src","type":"address"}],"name":"balanceOf","stateMutability":"View","type":"Function"},{"outputs":[{"type":"bool"}],"constant":True,"name":"stopped","stateMutability":"View","type":"Function"},{"outputs":[{"name":"result","type":"bool"}],"inputs":[{"name":"authority_","type":"address"}],"name":"setAuthority","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"address"}],"constant":True,"name":"owner","stateMutability":"View","type":"Function"},{"outputs":[{"type":"string"}],"constant":True,"name":"symbol","stateMutability":"View","type":"Function"},{"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"burn","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"wad","type":"uint256"}],"name":"mint","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"bool"}],"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"push","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"symbol_","type":"string"}],"name":"setSymbol","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"move","stateMutability":"Nonpayable","type":"Function"},{"name":"start","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"address"}],"constant":True,"name":"authority","stateMutability":"View","type":"Function"},{"inputs":[{"name":"name_","type":"string"}],"name":"setName","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"bool"}],"inputs":[{"name":"guy","type":"address"}],"name":"approve","stateMutability":"Nonpayable","type":"Function"},{"outputs":[{"type":"uint256"}],"constant":True,"inputs":[{"name":"src","type":"address"},{"name":"guy","type":"address"}],"name":"allowance","stateMutability":"View","type":"Function"},{"inputs":[{"name":"src","type":"address"},{"name":"wad","type":"uint256"}],"name":"pull","stateMutability":"Nonpayable","type":"Function"},{"inputs":[{"name":"symbol_","type":"string"}],"stateMutability":"Nonpayable","type":"Constructor"},{"inputs":[{"indexed":True,"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"Mint","type":"Event"},{"inputs":[{"indexed":True,"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"Burn","type":"Event"},{"inputs":[{"indexed":True,"name":"authority","type":"address"}],"name":"LogSetAuthority","type":"Event"},{"inputs":[{"indexed":True,"name":"owner","type":"address"}],"name":"LogSetOwner","type":"Event"},{"inputs":[{"indexed":True,"name":"sig","type":"bytes4"},{"indexed":True,"name":"guy","type":"address"},{"indexed":True,"name":"foo","type":"bytes32"},{"indexed":True,"name":"bar","type":"bytes32"},{"name":"sad","type":"uint256"},{"name":"fax","type":"bytes"}],"name":"LogNote","anonymous":True,"type":"Event"},{"inputs":[{"indexed":True,"name":"src","type":"address"},{"indexed":True,"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"Approval","type":"Event"},{"inputs":[{"indexed":True,"name":"src","type":"address"},{"indexed":True,"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"Transfer","type":"Event"}]},
        name="JST",
        decimal_places=18
    )

