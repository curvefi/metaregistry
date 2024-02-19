from eth.constants import ZERO_ADDRESS

from scripts.deployment_utils import get_deployed_contract


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    assert populated_metaregistry.get_pool_name(
        stable_registry_pool
    ) == stable_registry.get_pool_name(stable_registry_pool)


def test_stable_factory_pools(populated_metaregistry, stable_factory_pool):
    # same issues where a pool that was first in a registry got ported over to the
    # factory incorrectly. so we try different handler indices to check if we get
    # the right result:
    pool_registry_handlers = (
        populated_metaregistry.get_registry_handlers_from_pool(
            stable_factory_pool
        )
    )
    pool_registry_handlers = [
        handler
        for handler in pool_registry_handlers
        if handler != ZERO_ADDRESS
    ]
    num_registry_handlers = len(pool_registry_handlers)

    pool_name = populated_metaregistry.get_pool_name(stable_factory_pool)
    token_name = get_deployed_contract("ERC20", stable_factory_pool).name()
    assert num_registry_handlers in (1, 2), (
        f"Invalid number of registry handlers for {stable_factory_pool}. "
        f"Metaregistry returned {num_registry_handlers} handlers: {pool_registry_handlers}"
    )
    if num_registry_handlers == 1:
        assert pool_name == token_name
        return

    assert pool_name != token_name
    second_pool_name = populated_metaregistry.get_pool_name(
        stable_factory_pool, 1
    )
    assert second_pool_name == token_name


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    pool_name = populated_metaregistry.get_pool_name(crypto_registry_pool)
    assert pool_name == crypto_registry.get_pool_name(crypto_registry_pool)


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory
):
    pool_name = populated_metaregistry.get_pool_name(crypto_factory_pool)
    lp_token = crypto_factory.get_token(crypto_factory_pool)
    contract = get_deployed_contract("ERC20", lp_token)
    assert pool_name == contract.name()
