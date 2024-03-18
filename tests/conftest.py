import logging
from functools import cache
from os import environ
from urllib.parse import urlparse

import boa
import pytest

from tests.utils import get_contract_pools

pytest_plugins = [
    "tests.fixtures.accounts",
    "tests.fixtures.constants",
    "tests.fixtures.deployments",
    "tests.fixtures.functions",
]


@cache
def _get_stable_registry_pools():
    logging.info("Retrieving stable registry pools")
    return get_contract_pools(
        "StableRegistry", "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5"
    )


@cache
def _get_stable_factory_pools():
    logging.info("Retrieving stable factory pools")
    factory_pools_mainnet = get_contract_pools(
        "StableFactory", "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
    )
    factory_ng_pools_mainnet = get_contract_pools(
        "StableFactoryNG", "0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf"
    )
    return factory_pools_mainnet + factory_ng_pools_mainnet


@cache
def _get_crypto_registry_pools():
    logging.info("Retrieving crypto registry pools")
    return get_contract_pools(
        "CryptoRegistry", "0x8F942C20D02bEfc377D41445793068908E2250D0"
    )


@cache
def _get_crypto_factory_pools():
    logging.info("Retrieving crypto factory pools")
    return get_contract_pools(
        "CryptoFactory", "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99"
    )


@cache
def _get_all_pools():
    return (
        _get_stable_registry_pools()
        + _get_stable_factory_pools()
        + _get_crypto_registry_pools()
        + _get_crypto_factory_pools()
    )


def pytest_sessionstart():
    """Set up pools into global variables at session start"""
    logging.info(
        f"Connecting to fork at {urlparse(environ['RPC_ETHEREUM']).netloc}"
    )
    boa.env.fork(url=environ["RPC_ETHEREUM"])
    # TODO: boa.env.enable_fast_mode()


def pytest_generate_tests(metafunc):
    if "stable_registry_pool" in metafunc.fixturenames:
        metafunc.parametrize(
            "stable_registry_pool", _get_stable_registry_pools()
        )

    if "stable_factory_pool" in metafunc.fixturenames:
        metafunc.parametrize(
            "stable_factory_pool", _get_stable_factory_pools()
        )

    if "crypto_registry_pool" in metafunc.fixturenames:
        metafunc.parametrize(
            "crypto_registry_pool", _get_crypto_registry_pools()
        )

    if "crypto_factory_pool" in metafunc.fixturenames:
        metafunc.parametrize(
            "crypto_factory_pool", _get_crypto_factory_pools()
        )

    if "pool" in metafunc.fixturenames:
        metafunc.parametrize("pool", _get_all_pools())


@pytest.fixture(scope="session")
def stable_registry_pool():
    yield _get_stable_registry_pools()


@pytest.fixture(scope="session")
def stable_factory_pool():
    yield _get_stable_factory_pools()


@pytest.fixture(scope="session")
def crypto_registry_pool():
    yield _get_crypto_registry_pools()


@pytest.fixture(scope="session")
def crypto_factory_pool():
    yield _get_crypto_factory_pools()


@pytest.fixture(scope="session")
def pool():
    yield _get_all_pools()
