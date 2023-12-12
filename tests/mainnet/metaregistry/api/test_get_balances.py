import pytest
from boa import BoaError

from tests.utils import assert_negative_coin_balance


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    actual_output = stable_registry.get_balances(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_balances(
        stable_registry_pool
    )
    for i in range(populated_metaregistry.get_n_coins(stable_registry_pool)):
        assert actual_output[i] == metaregistry_output[i]


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    try:
        actual_output = stable_factory.get_balances(stable_factory_pool)
    except BoaError:
        assert_negative_coin_balance(
            populated_metaregistry, stable_factory_pool
        )
        return pytest.skip(
            f"Pool {stable_factory_pool} has coin balances lower than admin"
        )

    metaregistry_output = populated_metaregistry.get_balances(
        stable_factory_pool
    )
    for i in range(populated_metaregistry.get_n_coins(stable_factory_pool)):
        assert actual_output[i] == metaregistry_output[i]


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    crypto_registry,
    curve_pool_v2,
):
    try:
        actual_output = crypto_registry.get_balances(crypto_registry_pool)
    except BoaError:
        actual_output = []
        pool = curve_pool_v2(crypto_registry_pool)
        for i in range(
            populated_metaregistry.get_n_coins(crypto_registry_pool)
        ):
            actual_output.append(pool.balances(i))

    metaregistry_output = populated_metaregistry.get_balances(
        crypto_registry_pool
    )
    for i in range(populated_metaregistry.get_n_coins(crypto_registry_pool)):
        assert actual_output[i] == metaregistry_output[i]


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory, curve_pool_v2
):
    try:
        actual_output = crypto_factory.get_balances(crypto_factory_pool)
    except BoaError:
        actual_output = []
        pool = curve_pool_v2(crypto_factory_pool)
        for i in range(2):
            actual_output.append(pool.balances(i))

    metaregistry_output = populated_metaregistry.get_balances(
        crypto_factory_pool
    )
    for i in range(populated_metaregistry.get_n_coins(crypto_factory_pool)):
        assert actual_output[i] == metaregistry_output[i]
