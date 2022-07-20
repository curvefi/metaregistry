import pytest

from tests.mainnet.metaregistry.api.utils import check_pool_already_registered


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry, stable_registry_handler
):

    if check_pool_already_registered(
        populated_metaregistry, stable_registry_pool, stable_registry_handler
    ):
        pytest.skip()

    assert populated_metaregistry.get_pool_name(
        stable_registry_pool
    ) == stable_registry.get_pool_name(stable_registry_pool)


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory_handler, project
):

    if check_pool_already_registered(
        populated_metaregistry, stable_factory_pool, stable_factory_handler
    ):
        pytest.skip()

    assert (
        populated_metaregistry.get_pool_name(stable_factory_pool)
        == project.ERC20.at(stable_factory_pool).name()
    )


def test_crypto_registry_pools(populated_metaregistry, crypto_registry_pool, crypto_registry):

    if check_pool_already_registered(populated_metaregistry, crypto_registry_pool, crypto_registry):
        pytest.skip()

    assert populated_metaregistry.get_pool_name(
        crypto_registry_pool
    ) == crypto_registry.get_pool_name(crypto_registry_pool)


def test_crypto_factory_pools(populated_metaregistry, crypto_factory_pool, crypto_factory, project):

    if check_pool_already_registered(populated_metaregistry, crypto_factory_pool, crypto_factory):
        pytest.skip()

    assert (
        populated_metaregistry.get_pool_name(crypto_factory_pool)
        == project.ERC20.at(crypto_factory.get_token(crypto_factory_pool)).name()
    )
