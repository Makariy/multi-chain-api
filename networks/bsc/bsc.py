from base import Networks

from networks.ethereum.ethereum import EthereumNetwork


class BSCNetwork(EthereumNetwork):
    name = Networks.BSC
