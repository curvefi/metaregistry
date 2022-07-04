import pytest

from tests.abis import (
    address_provider,
    crypto_factory,
    crypto_registry,
    stable_factory,
    stable_registry,
)


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
def owner():
    yield address_provider().admin()


@pytest.fixture(scope="module")
def metaregistry(MetaRegistry, owner):
    yield MetaRegistry.deploy({"from": owner})


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(StableRegistryHandler, owner, metaregistry):
    handler = StableRegistryHandler.deploy(metaregistry, 0, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(0, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(
    StableFactoryHandler, owner, metaregistry, stable_registry_handler
):  # ensure registry fixtures exec order
    handler = StableFactoryHandler.deploy(metaregistry, 3, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(3, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(CryptoRegistryHandler, owner, metaregistry, stable_factory_handler):
    handler = CryptoRegistryHandler.deploy(metaregistry, 5, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(5, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(CryptoFactoryHandler, owner, metaregistry, crypto_registry_handler):
    handler = CryptoFactoryHandler.deploy(metaregistry, 6, {"from": owner})
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


@pytest.fixture(scope="module")
def handlers(
    stable_registry_handler, stable_factory_handler, crypto_registry_handler, crypto_factory_handler
):
    yield [
        stable_registry_handler,
        stable_factory_handler,
        crypto_registry_handler,
        crypto_factory_handler,
    ]


@pytest.fixture(scope="module", autouse=True)
def registry_pool_index_iterator(registries, handlers):

    pool_count = [registry.pool_count() for registry in registries]
    registry_indices = range(len(registries))

    iterable = []
    for registry_id in registry_indices:

        registry = registries[registry_id]
        registry_handler = handlers[registry_id]

        for pool_index in range(pool_count[registry_id]):

            pool = registry.pool_list(pool_index)
            iterable.append((registry_id, registry_handler, registry, pool))

    return iterable
