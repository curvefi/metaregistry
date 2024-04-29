import boa
import pytest
from boa.vyper.contract import VyperContract

from scripts.deployment_utils import get_deployed_contract
from tests.utils import deploy_contract

ADDRESS_PROVIDER = "0x0000000022D53366457F9d5E68Ec105046FC4383"


@pytest.fixture(scope="module")
def gauge_controller() -> VyperContract:
    return get_deployed_contract(
        "GaugeController", "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"
    )


@pytest.fixture(scope="module")
def stable_registry() -> VyperContract:
    return get_deployed_contract(
        "StableRegistry", "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5"
    )


@pytest.fixture(scope="module")
def stable_factory() -> VyperContract:
    return get_deployed_contract(
        "StableFactory", "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
    )


@pytest.fixture(scope="module")
def crypto_factory() -> VyperContract:
    return get_deployed_contract(
        "CryptoFactory", "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99"
    )


@pytest.fixture(scope="module")
def base_pool_registry(owner):
    return deploy_contract(
        "BasePoolRegistry", sender=owner, directory="registries"
    )


@pytest.fixture(scope="module")
def populated_base_pool_registry(base_pool_registry, owner, base_pools):
    with boa.env.sender(owner):
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
def crypto_registry(
    populated_base_pool_registry, owner, crypto_registry_pools
):
    crypto_registry = deploy_contract(
        "CryptoRegistryV1",
        ADDRESS_PROVIDER,
        populated_base_pool_registry,
        directory="registries",
        sender=owner,
    )

    with boa.env.sender(owner):
        for _, pool in crypto_registry_pools.items():
            crypto_registry.add_pool(
                pool["pool"],
                pool["lp_token"],
                pool["gauge"],
                pool["zap"],
                pool["num_coins"],
                pool["name"],
                pool["base_pool"],
                pool["has_positive_rebasing_tokens"],
            )

    return crypto_registry


@pytest.fixture(scope="module")
def address_provider(crypto_registry, owner):
    contract = get_deployed_contract("AddressProvider", ADDRESS_PROVIDER)
    contract.set_address(5, crypto_registry, sender=owner)
    return contract


@pytest.fixture(scope="module")
def metaregistry(owner):
    return deploy_contract("MetaRegistry", sender=owner)


@pytest.fixture(scope="module")
def stable_registry_handler(stable_registry, owner):
    return deploy_contract(
        "StableRegistryHandler",
        stable_registry.address,
        sender=owner,
        directory="registry_handlers",
    )


@pytest.fixture(scope="module")
def stable_factory_handler(
    populated_base_pool_registry, stable_factory, owner
):
    return deploy_contract(
        "StableFactoryHandler",
        stable_factory.address,
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
