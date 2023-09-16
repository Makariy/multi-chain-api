from typing import Optional, Any
from dataclasses import dataclass
from .base import BaseProvider


@dataclass
class HTTPProxy:
    params: Any


@dataclass
class HTTPProvider(BaseProvider):
    endpoint: str
    api_key: Optional[str] = None
    proxy: Optional[HTTPProxy] = None
    extra: Optional[Any] = None

