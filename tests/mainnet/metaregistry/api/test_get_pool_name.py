import pytest

from tests.utils import ZERO_ADDRESS, get_deployed_token_contract


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
    num_registry_handlers = len(
        list(filter((ZERO_ADDRESS).__ne__, pool_registry_handlers))
    )

    name = populated_metaregistry.get_pool_name(stable_factory_pool)
    if num_registry_handlers == 1:
        assert name == get_deployed_token_contract(stable_factory_pool).name()
    else:
        with pytest.raises(AssertionError):
            assert (
                name == get_deployed_token_contract(stable_factory_pool).name()
            )

        pool_name2 = populated_metaregistry.get_pool_name(
            stable_factory_pool, 1
        )
        assert (
            pool_name2
            == get_deployed_token_contract(stable_factory_pool).name()
        )

    assert num_registry_handlers in (1, 2)


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    pool_name = populated_metaregistry.get_pool_name(crypto_registry_pool)
    assert pool_name == crypto_registry.get_pool_name(crypto_registry_pool)


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory
):
    pool_name = populated_metaregistry.get_pool_name(crypto_factory_pool)
    contract = get_deployed_token_contract(
        crypto_factory.get_token(crypto_factory_pool)
    )
    assert pool_name == contract.name()
