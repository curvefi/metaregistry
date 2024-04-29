from eth.constants import ZERO_ADDRESS


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    actual_output = stable_registry.is_meta(stable_registry_pool)
    metaregistry_output = populated_metaregistry.is_meta(stable_registry_pool)
    assert actual_output == metaregistry_output


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    actual_output = stable_factory.is_meta(stable_factory_pool)
    metaregistry_output = populated_metaregistry.is_meta(stable_factory_pool)
    assert actual_output == metaregistry_output


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    actual_output = crypto_registry.is_meta(crypto_registry_pool)
    metaregistry_output = populated_metaregistry.is_meta(crypto_registry_pool)
    assert actual_output == metaregistry_output


def test_crypto_factory_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    crypto_factory_pool,
    crypto_factory,
):
    coins = crypto_factory.get_coins(crypto_factory_pool)
    actual_output = False
    for i in range(len(coins)):
        if (
            populated_base_pool_registry.get_base_pool_for_lp_token(coins[i])
            != ZERO_ADDRESS
        ):
            actual_output = True
            break

    metaregistry_output = populated_metaregistry.is_meta(crypto_factory_pool)
    assert actual_output == metaregistry_output
