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

from tests.utils.constants import ADMIN_FEE_RECEIVER, sEUR, agEUR, ADDRESS_PROVIDER_STABLE_FACTORY_INDEX, METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def address_provider(owner):
    yield AddressProvider.deploy(owner, {"from": owner})


@pytest.fixture(scope="module")
def two_coin_plain_pool_implementation(owner):
    yield TwoCoinPlainPoolNoLendingImplementation.deploy({"from": owner})


@pytest.fixture(scope="module")
def stable_factory(owner, address_provider):
    factory = StableFactory.deploy(ADMIN_FEE_RECEIVER, {"from": owner})
    address_provider.add_new_id(factory, "StableFactory", {"from": owner})
    address_provider.set_address(
        ADDRESS_PROVIDER_STABLE_FACTORY_INDEX, factory, {"from": owner}
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
    yield MetaRegistry.deploy(owner, address_provider, {"from": owner})


@pytest.fixture(scope="module")
def stable_factory_handler(
    owner,
    stable_factory,
    metaregistry_mock,
    euro_pool,
    address_provider,
):
    handler = StableFactoryHandler.deploy(
        metaregistry_mock,
        ADDRESS_PROVIDER_STABLE_FACTORY_INDEX,
        address_provider,
        {"from": owner},
    )
    metaregistry_mock.add_registry_by_address_provider_id(
        ADDRESS_PROVIDER_STABLE_FACTORY_INDEX, handler, {"from": owner}
    )
    yield handler


@pytest.fixture(scope="module", autouse=True)
def sync_stable_factory_registry(
    address_provider,
    metaregistry_mock,
    stable_factory,
    stable_factory_handler,
    owner
):
    total_pools = stable_factory.pool_count()
    metaregistry_mock.sync_registry(
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX, total_pools, {"from": owner}
    )
