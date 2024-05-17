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
def stable_ng_factory_handler(
    populated_base_pool_registry, stableswap_ng_factory, ng_owner
):
    with boa.env.prank(ng_owner):
        return boa.load(
            "contracts/registry_handlers/ng/CurveStableSwapFactoryNGHandler.vy",
            stableswap_ng_factory.address,
            populated_base_pool_registry.address,
        )


@pytest.fixture(scope="module")
def twocrypto_ng_factory_handler(twocrypto_ng_factory, ng_owner):
    with boa.env.prank(ng_owner):
        return boa.load(
            "contracts/registry_handlers/ng/CurveTwocryptoFactoryHandler.vy",
            twocrypto_ng_factory.address,
        )


@pytest.fixture(scope="module")
def tricrypto_ng_factory_handler(tricrypto_ng_factory, ng_owner):
    with boa.env.prank(ng_owner):
        return boa.load(
            "contracts/registry_handlers/ng/CurveTricryptoFactoryHandler.vy",
            tricrypto_ng_factory.address,
        )


@pytest.fixture(scope="module")
def handlers(
    stable_ng_factory_handler,
    twocrypto_ng_factory_handler,
    tricrypto_ng_factory_handler,
):
    return [
        stable_ng_factory_handler,
        twocrypto_ng_factory_handler,
        tricrypto_ng_factory_handler,
    ]


@pytest.fixture(scope="module")
def registries(handlers):
    registries = []
    for handler in handlers:
        registries.append(handler.base_registry())
    return registries


@pytest.fixture(scope="module")
def metaregistry(handlers, ng_owner):
    metaregistry_contract = deploy_contract("MetaRegistry", sender=ng_owner)
    for handler in handlers:
        metaregistry_contract.add_registry_handler(
            handler.address, sender=ng_owner
        )
    return metaregistry_contract
