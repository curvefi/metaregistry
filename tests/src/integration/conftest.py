import math
import time

import pytest
from brownie import (
    CryptoFactoryHandler,
    CryptoRegistryHandler,
    MetaRegistry,
    StableFactoryHandler,
    StableRegistryHandler,
)

from ..abis import crypto_factory, crypto_registry, stable_factory, stable_registry
from ..utils.constants import ADDRESS_PROVIDER


def pytest_addoption(parser):
    parser.addoption(
        "--synclimit",
        type=int,
        action="store",
        default=0,
        help="Only syncs up to the specified number of pools on each registry",
    )


@pytest.fixture(scope="session")
def sync_limit(request):
    return request.config.getoption("--synclimit")


@pytest.fixture(scope="session")
def metaregistry(owner):
    yield MetaRegistry.deploy(owner, ADDRESS_PROVIDER, {"from": owner})


@pytest.fixture(scope="session")
def stable_registry_handler(owner, metaregistry):
    handler = StableRegistryHandler.deploy(metaregistry, 0, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(0, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="session")
def stable_factory_handler(owner, metaregistry):
    handler = StableFactoryHandler.deploy(metaregistry, 3, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(3, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="session")
def crypto_registry_handler(owner, metaregistry):
    handler = CryptoRegistryHandler.deploy(metaregistry, 5, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(5, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="session")
def crypto_factory_handler(owner, metaregistry):
    handler = CryptoFactoryHandler.deploy(metaregistry, 6, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(6, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="session")
def registries():
    yield [
        stable_factory(),
        stable_registry(),
        crypto_factory(),
        crypto_registry(),
    ]


@pytest.fixture(scope="session", autouse=True)
def sync_registries(
    metaregistry,
    registries,
    stable_factory_handler,
    stable_registry_handler,
    crypto_factory_handler,
    crypto_registry_handler,
    owner,
    sync_limit,
):

    # split the initial syncs to avoid hitting gas limit
    for i in range(metaregistry.registry_length()):
        registry = registries[i]
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        print(f"total pools in registry {registry}: ", total_pools)
        for j in range((math.ceil(total_pools / 10))):
            print(f"Syncing {j+1} * 10 ({(j+1) * 10}) pools out of {total_pools} for registry {i}")
            try:
                metaregistry.sync_registry(i, 10, {"from": owner})
            except Exception as e:
                print(f"Error 1: {e}\n Retrying")
                time.sleep(10)
                metaregistry.sync_registry(i, 10, {"from": owner})
