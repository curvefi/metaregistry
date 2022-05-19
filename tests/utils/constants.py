from dataclasses import dataclass
from typing import Tuple


@dataclass
class Pool:
    address: str
    coins: Tuple[str, str, str, str, str, str, str, str]
    n_coins: int
    underlying_coins: Tuple[str, str, str, str, str, str, str, str]
    decimals: Tuple[int, int, int, int, int, int, int, int]
    underlying_decimals: Tuple[int, int, int, int, int, int, int, int]
    lp_token: str
    gauges: Tuple[
        Tuple[str, str, str, str, str, str, str, str, str, str],
        Tuple[int, int, int, int, int, int, int, int, int, int],
    ]
    is_meta: bool
    name: str
    asset_type: int


ADMIN_FEE_RECEIVER = "0xeCb456EA5365865EbAb8a2661B0c503410e9B347"

STABLE_FACTORY = "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
STABLE_REGISTRY = "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5"
CRYPTO_FACTORY = "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99"
CRYPTO_REGISTRY = "0x8F942C20D02bEfc377D41445793068908E2250D0"

GAUGE_CONTROLLER = "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"
ADDRESS_PROVIDER = "0x0000000022D53366457F9d5E68Ec105046FC4383"

ADDRESS_ZERO = "0x0000000000000000000000000000000000000000"

ADDRESS_PROVIDER_STABLE_REGISTRY_INDEX = 0
ADDRESS_PROVIDER_STABLE_FACTORY_INDEX = 1
METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX = 0

sEUR = "0xD71eCFF9342A5Ced620049e616c5035F1dB98620"
agEUR = "0x1a7e4e63778B4f12a199C062f3eFdD288afCBce8"
