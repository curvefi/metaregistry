import ape
import pytest

pytest_plugins = [
    "fixtures.accounts",
    "fixtures.constants",
    "fixtures.deployments",
    "fixtures.functions",
]

CRYPTO_REGISTRY_POOLS = None
CRYPTO_FACTORY_POOLS = None
STABLE_REGISTRY_POOLS = None
STABLE_FACTORY_POOLS = None
ALL_POOLS = None


def pytest_sessionstart(session):
    """Set up pools into global variables at session start"""
    global CRYPTO_REGISTRY_POOLS
    global CRYPTO_FACTORY_POOLS
    global STABLE_FACTORY_POOLS
    global STABLE_REGISTRY_POOLS
    global ALL_POOLS

    # fetch the pytest ape runner plugin
    ape_runner = session.config.pluginmanager.getplugin("ape-test")

    # connect to the network
    # https://github.com/ApeWorX/ape/blob/main/src/ape/pytest/runners.py#L149-L153
    ape_runner.network_manager.active_provider = (
        ape_runner.network_manager.get_provider_from_choice(
            ape_runner._network_choice
        )
    )
    ape_runner.network_manager.active_provider.connect()
    ape_runner._provider_is_connected = True

    # store instance of registries globally so we don't have to recreate multiple times
    # when generating tests:

    # stable registry:
    registry = ape.project.StableRegistry.at(
        "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5"
    )
    STABLE_REGISTRY_POOLS = [
        registry.pool_list(i) for i in range(registry.pool_count())
    ]

    # stable_factory:
    registry = ape.project.StableFactory.at(
        "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
    )
    STABLE_FACTORY_POOLS = [
        registry.pool_list(i) for i in range(registry.pool_count())
    ]

    # crypto_registry:
    registry = ape.project.CryptoRegistry.at(
        "0x8F942C20D02bEfc377D41445793068908E2250D0"
    )
    CRYPTO_REGISTRY_POOLS = [
        registry.pool_list(i) for i in range(registry.pool_count())
    ]

    # crypto_factory:
    registry = ape.project.CryptoFactory.at(
        "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99"
    )
    CRYPTO_FACTORY_POOLS = [
        registry.pool_list(i) for i in range(registry.pool_count())
    ]

    ALL_POOLS = (
        STABLE_REGISTRY_POOLS
        + STABLE_FACTORY_POOLS
        + CRYPTO_REGISTRY_POOLS
        + CRYPTO_FACTORY_POOLS
    )


def pytest_generate_tests(metafunc):
    if "stable_registry_pool" in metafunc.fixturenames:
        metafunc.parametrize("stable_registry_pool", STABLE_REGISTRY_POOLS)

    if "stable_factory_pool" in metafunc.fixturenames:
        metafunc.parametrize("stable_factory_pool", STABLE_FACTORY_POOLS)

    if "crypto_registry_pool" in metafunc.fixturenames:
        metafunc.parametrize("crypto_registry_pool", CRYPTO_REGISTRY_POOLS)

    if "crypto_factory_pool" in metafunc.fixturenames:
        metafunc.parametrize("crypto_factory_pool", CRYPTO_FACTORY_POOLS)

    if "pool" in metafunc.fixturenames:
        metafunc.parametrize("pool", ALL_POOLS)


@pytest.fixture(scope="session")
def stable_registry_pool():
    yield STABLE_REGISTRY_POOLS


@pytest.fixture(scope="session")
def stable_factory_pool():
    yield STABLE_FACTORY_POOLS


@pytest.fixture(scope="session")
def crypto_registry_pool():
    yield CRYPTO_REGISTRY_POOLS


@pytest.fixture(scope="session")
def crypto_factory_pool():
    yield CRYPTO_FACTORY_POOLS


@pytest.fixture(scope="session")
def pool():
    yield ALL_POOLS
