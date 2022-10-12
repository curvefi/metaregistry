import ape
import pytest


def test_stable_registry_pools(populated_metaregistry, stable_registry_pool, stable_registry):

    assert populated_metaregistry.get_pool_name(
        stable_registry_pool
    ) == stable_registry.get_pool_name(stable_registry_pool)


def test_stable_factory_pools(populated_metaregistry, stable_factory_pool):

    # same issues where a pool that was first in a registry got ported over to the
    # factory incorrectly. so we try different handler indices to check if we get
    # the right result:
    pool_registry_handlers = populated_metaregistry.get_registry_handlers_from_pool(
        stable_factory_pool
    )
    num_registry_handlers = len(
        list(filter((ape.utils.ZERO_ADDRESS).__ne__, pool_registry_handlers))
    )

    if num_registry_handlers == 1:

        assert (
            populated_metaregistry.get_pool_name(stable_factory_pool)
            == ape.Contract(stable_factory_pool).name()
        )

    elif num_registry_handlers == 2:

        with pytest.raises(AssertionError):

            assert (
                populated_metaregistry.get_pool_name(stable_factory_pool)
                == ape.Contract(stable_factory_pool).name()
            )

        assert (
            populated_metaregistry.get_pool_name(stable_factory_pool, 1)
            == ape.Contract(stable_factory_pool).name()
        )

    else:

        raise


def test_crypto_registry_pools(populated_metaregistry, crypto_registry_pool, crypto_registry):

    assert populated_metaregistry.get_pool_name(
        crypto_registry_pool
    ) == crypto_registry.get_pool_name(crypto_registry_pool)


def test_crypto_factory_pools(populated_metaregistry, crypto_factory_pool, crypto_factory):

    assert (
        populated_metaregistry.get_pool_name(crypto_factory_pool)
        == ape.Contract(crypto_factory.get_token(crypto_factory_pool)).name()
    )
