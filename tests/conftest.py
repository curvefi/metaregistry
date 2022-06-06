import pytest
from brownie import (
    CryptoFactoryHandler,
    CryptoRegistryHandler,
    MetaRegistry,
    StableFactoryHandler,
    StableRegistryHandler,
)

from .abis import crypto_factory, crypto_registry, stable_factory, stable_registry
from .utils.constants import ADDRESS_PROVIDER


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def metaregistry(owner):
    yield MetaRegistry.deploy(owner, ADDRESS_PROVIDER, {"from": owner})


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(owner, metaregistry):
    handler = StableRegistryHandler.deploy(metaregistry, 0, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(0, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(
    owner, metaregistry, stable_registry_handler
):  # ensure registry fixtures exec order
    handler = StableFactoryHandler.deploy(metaregistry, 3, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(3, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(owner, metaregistry, stable_factory_handler):
    handler = CryptoRegistryHandler.deploy(metaregistry, 5, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(5, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(owner, metaregistry, crypto_registry_handler):
    handler = CryptoFactoryHandler.deploy(metaregistry, 6, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(6, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module")
def registries():
    yield [
        stable_registry(),
        stable_factory(),
        crypto_registry(),
        crypto_factory(),
    ]
