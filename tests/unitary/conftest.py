import boa
import pytest

from tests.utils import deploy_contract

pytest_plugins = [
    "tests.fixtures.accounts",
    "tests.fixtures.constants",
    "tests.fixtures.deployments",
    "tests.fixtures.functions",
]


@pytest.fixture(scope="module")
def metaregistry(ng_owner):
    return deploy_contract("MetaRegistry", sender=ng_owner)


@pytest.fixture(scope="module")
def base_pool_registry(ng_owner):
    return deploy_contract(
        "BasePoolRegistry", sender=ng_owner, directory="registries"
    )


@pytest.fixture(scope="module")
def populated_base_pool_registry(base_pool_registry, ng_owner, base_pools):
    with boa.env.sender(ng_owner):
        for data in base_pools.values():
            base_pool_registry.add_base_pool(
                data["pool"],
                data["lp_token"],
                data["num_coins"],
                data["is_legacy"],
                data["is_lending"],
                data["is_v2"],
            )
    return base_pool_registry


@pytest.fixture(scope="module")
def stable_factory_handler(
    populated_base_pool_registry, stableswap_ng_factory, owner
):
    return deploy_contract(
        "StableFactoryHandler",
        stableswap_ng_factory.address,
        populated_base_pool_registry.address,
        sender=owner,
        directory="registry_handlers",
    )


@pytest.fixture(scope="module")
def crypto_registry_handler(owner, crypto_registry):
    return deploy_contract(
        "CryptoRegistryHandler",
        crypto_registry.address,
        sender=owner,
        directory="registry_handlers",
    )


@pytest.fixture(scope="module")
def crypto_factory_handler(
    populated_base_pool_registry, crypto_factory, owner
):
    return deploy_contract(
        "CryptoFactoryHandler",
        crypto_factory.address,
        populated_base_pool_registry.address,
        sender=owner,
        directory="registry_handlers",
    )


@pytest.fixture(scope="module")
def registries(
    stable_registry, stable_factory, crypto_registry, crypto_factory
):
    return [stable_registry, stable_factory, crypto_registry, crypto_factory]


@pytest.fixture(scope="module")
def handlers(
    stable_registry_handler,
    stable_factory_handler,
    crypto_registry_handler,
    crypto_factory_handler,
):
    return [
        stable_registry_handler,
        stable_factory_handler,
        crypto_registry_handler,
        crypto_factory_handler,
    ]


@pytest.fixture(scope="module")
def populated_metaregistry(metaregistry, handlers, owner):
    for handler in handlers:
        metaregistry.add_registry_handler(handler.address, sender=owner)
    return metaregistry


@pytest.fixture(scope="module")
def stable_registry_handler_index():
    return 0
