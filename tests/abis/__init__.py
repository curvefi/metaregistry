from brownie import Contract
import json
import os

from ..utils.constants import (
    STABLE_FACTORY,
    STABLE_REGISTRY,
    CRYPTO_REGISTRY,
    CRYPTO_FACTORY,
    GAUGE_CONTROLLER,
)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "CurvePool.json"), "r"
) as fp:
    CURVE_V1_ABI = json.load(fp)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "CurvePoolV2.json"), "r"
) as fp:
    CURVE_V2_ABI = json.load(fp)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "CryptoFactory.json"), "r"
) as fp:
    CRYPTO_FACTORY_ABI = json.load(fp)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "CryptoRegistry.json"),
    "r",
) as fp:
    CRYPTO_REGISTRY_ABI = json.load(fp)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "StableRegistry.json"),
    "r",
) as fp:
    STABLE_REGISTRY_ABI = json.load(fp)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "StableFactory.json"), "r"
) as fp:
    STABLE_FACTORY_ABI = json.load(fp)

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "GaugeController.json"),
    "r",
) as fp:
    GAUGE_CONTROLLER_ABI = json.load(fp)


def curve_pool(_pool: str) -> Contract:
    return Contract.from_abi(name="CurveV1", address=_pool, abi=CURVE_V1_ABI)


def curve_pool_v2(_pool: str) -> Contract:
    return Contract.from_abi(name="CurveV2", address=_pool, abi=CURVE_V2_ABI)


def crypto_factory() -> Contract:
    return Contract.from_abi(
        name="Curve Crypto Factory", address=CRYPTO_FACTORY, abi=CRYPTO_FACTORY_ABI
    )


def crypto_registry() -> Contract:
    return Contract.from_abi(
        name="Curve Crypto Registry", address=CRYPTO_REGISTRY, abi=CRYPTO_REGISTRY_ABI
    )


def stable_factory() -> Contract:
    return Contract.from_abi(
        name="Curve Stable Factory", address=STABLE_FACTORY, abi=STABLE_FACTORY_ABI
    )


def stable_registry() -> Contract:
    return Contract.from_abi(
        name="Curve Stable Registry", address=STABLE_REGISTRY, abi=STABLE_REGISTRY_ABI
    )


def gauge_controller() -> Contract:
    return Contract.from_abi(
        name="Curve Gauge Controller",
        address=GAUGE_CONTROLLER,
        abi=GAUGE_CONTROLLER_ABI,
    )
