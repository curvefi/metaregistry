import ape
import pytest


ADDRESS_PROVIDER = "0x0000000022D53366457F9d5E68Ec105046FC4383"


@pytest.fixture(scope="module")
def gauge_controller() -> ape.Contract:
    return ape.project.GaugeController.at("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB")


@pytest.fixture(scope="module")
def stable_registry() -> ape.Contract:
    return ape.project.StableRegistry.at("0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5")


@pytest.fixture(scope="module")
def stable_factory() -> ape.Contract:
    return ape.project.StableFactory.at("0xB9fC157394Af804a3578134A6585C0dc9cc990d4")


@pytest.fixture(scope="module")
def crypto_factory() -> ape.Contract:
    return ape.project.CryptoFactory.at("0xF18056Bbd320E96A48e3Fbf8bC061322531aac99")


@pytest.fixture(scope="module")
def base_pool_registry(alice, project):
    return project.BasePoolRegistry.deploy(sender=alice)


@pytest.fixture(scope="module")
def populated_base_pool_registry(base_pool_registry, owner, base_pools):

    for name, data in base_pools.items():
        base_pool_registry.add_base_pool(
            data["pool"],
            data["lp_token"],
            data["num_coins"],
            data["is_legacy"],
            data["is_lending"],
            data["is_v2"],
            sender=owner,
        )

    return base_pool_registry


@pytest.fixture(scope="module")
def crypto_registry(populated_base_pool_registry, owner, project):
    return project.CryptoRegistryV1.deploy(
        ADDRESS_PROVIDER, populated_base_pool_registry, sender=owner
    )


@pytest.fixture(scope="module")
def populated_crypto_registry(crypto_registry, owner, crypto_registry_pools):

    for name, pool in crypto_registry_pools.items():
        crypto_registry.add_pool(
            pool["pool"],
            pool["lp_token"],
            pool["gauge"],
            pool["zap"],
            pool["num_coins"],
            pool["name"],
            pool["base_pool"],
            pool["has_positive_rebasing_tokens"],
            sender=owner,
        )

    return crypto_registry


@pytest.fixture(scope="module", autouse=True)
def address_provider(populated_crypto_registry, owner):
    contract = ape.project.AddressProvider.at("0x0000000022D53366457F9d5E68Ec105046FC4383")
    contract.set_address(5, populated_crypto_registry, sender=owner)
    return contract


@pytest.fixture(scope="module")
def metaregistry(address_provider, owner, project):
    return project.MetaRegistry.deploy(address_provider, sender=owner)


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(stable_registry, owner, project):
    return project.StableRegistryHandler.deploy(stable_registry.address, sender=owner)


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(populated_base_pool_registry, stable_factory, owner, project):
    return project.StableFactoryHandler.deploy(
        stable_factory.address, populated_base_pool_registry, sender=owner
    )


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(owner, populated_crypto_registry, project):
    return project.CryptoRegistryHandler.deploy(populated_crypto_registry, sender=owner)


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(populated_base_pool_registry, crypto_factory, owner, project):
    return project.CryptoFactoryHandler.deploy(
        crypto_factory.address, populated_base_pool_registry, sender=owner
    )


@pytest.fixture(scope="module")
def registries(stable_registry, stable_factory, crypto_registry_v1, crypto_factory):
    return [
        stable_registry,
        stable_factory,
        crypto_registry_v1,
        crypto_factory,
    ]


@pytest.fixture(scope="module")
def handlers(
    stable_registry_handler, stable_factory_handler, crypto_registry_handler, crypto_factory_handler
):
    return [
        stable_registry_handler,
        stable_factory_handler,
        crypto_registry_handler,
        crypto_factory_handler,
    ]


@pytest.fixture(scope="module", autouse=True)
def populated_metaregistry(metaregistry, handlers, owner):
    for handler in handlers:
        metaregistry.add_registry_handler(handler.address, sender=owner)

    return metaregistry
