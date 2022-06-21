import pytest

from .abis import crypto_factory, crypto_registry, stable_factory, stable_registry
from .utils.constants import ADDRESS_PROVIDER


def pytest_addoption(parser):
    parser.addoption(
        "--pools",
        type=int,
        action="store",
        default=0,
        help="Only syncs up to the specified number of pools on each registry",
    )


@pytest.fixture(scope="session")
def max_pools(request):
    return request.config.getoption("--pools")


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
def metaregistry(MetaRegistry, owner):
    yield MetaRegistry.deploy(owner, ADDRESS_PROVIDER, {"from": owner})


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(StableRegistryHandler, owner, metaregistry):
    handler = StableRegistryHandler.deploy(metaregistry, 0, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(0, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(
    StableFactoryHandler, owner, metaregistry, stable_registry_handler
):  # ensure registry fixtures exec order
    handler = StableFactoryHandler.deploy(metaregistry, 3, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(3, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(CryptoRegistryHandler, owner, metaregistry, stable_factory_handler):
    handler = CryptoRegistryHandler.deploy(metaregistry, 5, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(5, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(CryptoFactoryHandler, owner, metaregistry, crypto_registry_handler):
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


@pytest.fixture(scope="module", autouse=True)
def registry_pool_index_iterator(registries, max_pools):

    pool_count = [registry.pool_count() for registry in registries]
    registry_indices = list(range(len(registries)))

    iterable = []
    for registry_id in registry_indices:

        registry = registries[registry_id]
        pool_indices = list(range(pool_count[registry_id]))

        for pool_index in pool_indices:

            # limit pools if max_pools is specified (>0)
            if pool_index > max_pools - 1 and max_pools > 0:
                break

            pool = registry.pool_list(pool_index)
            iterable.append((registry_id, registry, pool))

    return iterable


@pytest.fixture(scope="module", autouse=True)
def registry_pool_count(registries):
    pool_count_per_registry = [registry.pool_count() for registry in registries]
    return {registries[i]: max_pools for i, max_pools in enumerate(pool_count_per_registry)}
