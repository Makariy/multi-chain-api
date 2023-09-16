from dataclasses import dataclass


@dataclass
class ETHProviderExtra:
    rps_limit: int = 1
    sleep_time: float = 0.1
