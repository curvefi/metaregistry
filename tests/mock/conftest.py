import pytest
import time
from brownie import ZERO_ADDRESS
from brownie import (
    MetaRegistry,
    StableFactoryHandler,
    StableFactory,
    AddressProvider,
    TwoCoinPlainPoolNoLendingImplementation,
)

from tests.utils.constants import ADMIN_FEE_RECEIVER, sEUR, agEUR


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def address_provider(owner):
    try:
        yield AddressProvider.deploy(owner, {"from": owner})
    except Exception as e:
        print(f"Error deploying AddressProvider: {e}\n Retrying")
        time.sleep(5)
        yield AddressProvider.deploy(owner, {"from": owner})


@pytest.fixture(scope="module")
def two_coin_plain_pool_implementation(owner):
    try:
        yield TwoCoinPlainPoolNoLendingImplementation.deploy({"from": owner})
    except Exception as e:
        print(
            f"Error deploying TwoCoinPlainPoolNoLendingImplementation: {e}\n Retrying"
        )
        time.sleep(5)
        yield TwoCoinPlainPoolNoLendingImplementation.deploy({"from": owner})


@pytest.fixture(scope="module")
def address_provider_index_for_stable_factory():
    yield 1


@pytest.fixture(scope="module")
def stable_factory(owner, address_provider, address_provider_index_for_stable_factory):
    try:
        factory = StableFactory.deploy(ADMIN_FEE_RECEIVER, {"from": owner})
        address_provider.add_new_id(factory, "StableFactory", {"from": owner})
        address_provider.set_address(
            address_provider_index_for_stable_factory, factory, {"from": owner}
        )
        yield factory
    except Exception as e:
        print(f"Error setting address in AddressProvider: {e}\n Retrying")
        time.sleep(5)
        factory = StableFactory.deploy(ADMIN_FEE_RECEIVER, {"from": owner})
        address_provider.add_new_id(factory, "StableFactory", {"from": owner})
        address_provider.set_address(
            address_provider_index_for_stable_factory, factory, {"from": owner}
        )
        yield factory


@pytest.fixture(scope="module")
def euro_pool(owner, stable_factory, two_coin_plain_pool_implementation):

    tx = stable_factory.set_plain_implementations(
        2,
        [
            two_coin_plain_pool_implementation,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        {"from": owner},
    )

    tx = stable_factory.deploy_plain_pool(
        "seur-ageur",
        "eur2pool",
        [
            sEUR,
            agEUR,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        10000,
        4000000,
        0,
        0,
        {"from": owner},
    )
    yield tx.new_contracts[0]


@pytest.fixture(scope="module")
def metaregistry_mock(owner, address_provider):
    try:
        yield MetaRegistry.deploy(owner, address_provider, {"from": owner})
    except Exception as e:
        print(f"Error deploying MetaRegistry: {e}\n Retrying")
        yield MetaRegistry.deploy(owner, address_provider, {"from": owner})


@pytest.fixture(scope="module")
def stable_factory_handler(
    owner,
    stable_factory,
    metaregistry_mock,
    euro_pool,
    address_provider_index_for_stable_factory,
    address_provider,
):
    handler = StableFactoryHandler.deploy(
        metaregistry_mock,
        address_provider_index_for_stable_factory,
        address_provider,
        {"from": owner},
    )
    metaregistry_mock.add_registry_by_address_provider_id(
        address_provider_index_for_stable_factory, handler, {"from": owner}
    )
    yield handler


@pytest.fixture(scope="module")
def metaregistry_index_for_stable_factory_handler():
    yield 0


@pytest.fixture(scope="module", autouse=True)
def sync_stable_factory_registry(
    address_provider,
    metaregistry_mock,
    stable_factory,
    stable_factory_handler,
    owner,
    metaregistry_index_for_stable_factory_handler,
):
    total_pools = stable_factory.pool_count()
    metaregistry_mock.sync_registry(
        metaregistry_index_for_stable_factory_handler, total_pools, {"from": owner}
    )
