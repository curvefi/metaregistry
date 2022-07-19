import ape
import pytest


# - on-chain dependencies -


@pytest.fixture(scope="module")
def address_provider():
    return ape.project.AddressProvider.at("0x0000000022D53366457F9d5E68Ec105046FC4383")


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


# -- contracts to test --


@pytest.fixture(scope="module")
def base_pool_registry(alice, project):
    return project.BasePoolRegistry.deploy(sender=alice)


@pytest.fixture(scope="module")
def base_pool_registry_updated(base_pool_registry, owner, base_pools):

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
def crypto_registry_v1(base_pool_registry_updated, address_provider, owner, project):
    return project.CryptoRegistryV1.deploy(
        address_provider.address, base_pool_registry_updated, sender=owner
    )


@pytest.fixture(scope="module")
def crypto_registry_updated(
    base_pool_registry_updated, address_provider, owner, crypto_registry_pools, project
):

    registry = project.CryptoRegistryV1.deploy(
        address_provider.address, base_pool_registry_updated, sender=owner
    )

    for name, pool in crypto_registry_pools.items():
        registry.add_pool(
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

    return registry


@pytest.fixture(scope="module", autouse=True)
def address_provider_updated(crypto_registry_updated, address_provider, owner):
    address_provider.set_address(5, crypto_registry_updated, sender=owner)
    return address_provider


@pytest.fixture(scope="module")
def metaregistry(address_provider_updated, owner, project):
    return project.MetaRegistry.deploy(address_provider_updated, sender=owner)


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(stable_registry, owner, project):
    return project.StableRegistryHandler.deploy(stable_registry.address, sender=owner)


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(base_pool_registry_updated, stable_factory, owner, project):
    return project.StableFactoryHandler.deploy(
        stable_factory.address, base_pool_registry_updated, sender=owner
    )


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(owner, crypto_registry_updated, project):
    return project.CryptoRegistryHandler.deploy(crypto_registry_updated, sender=owner)


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(base_pool_registry_updated, crypto_factory, owner, project):
    return project.CryptoFactoryHandler.deploy(
        crypto_factory.address, base_pool_registry_updated, sender=owner
    )


# ---- grouped registries/handlers ----


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


@pytest.fixture(scope="module")
def metaregistry_indices(handlers):

    ordering = {}
    for i in range(len(handlers)):
        ordering[handlers[i].address] = i
    return ordering
