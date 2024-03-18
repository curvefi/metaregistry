from eth.constants import ZERO_ADDRESS


def _get_n_coins_for_pool(registry, pool):
    actual_output = registry.get_n_coins(pool)
    # registry returns tuple, we want the first one (since the second)
    # index is about basepool n coins
    if not isinstance(actual_output, int):
        actual_output = registry.get_n_coins(pool)[0]

    # registry returns 0 value for n coins: something's not right on the
    # registry's side. find n_coins via registry.get_coins:
    elif actual_output == 0:
        coins = registry.get_coins(pool)
        actual_output = sum([1 for coin in coins if coin != ZERO_ADDRESS])

    return actual_output


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    actual_output = _get_n_coins_for_pool(
        stable_registry, stable_registry_pool
    )

    metaregistry_output = populated_metaregistry.get_n_coins(
        stable_registry_pool
    )
    assert metaregistry_output == actual_output


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    actual_output = _get_n_coins_for_pool(stable_factory, stable_factory_pool)

    metaregistry_output = populated_metaregistry.get_n_coins(
        stable_factory_pool
    )
    assert metaregistry_output == actual_output


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    actual_output = _get_n_coins_for_pool(
        crypto_registry, crypto_registry_pool
    )

    metaregistry_output = populated_metaregistry.get_n_coins(
        crypto_registry_pool
    )
    assert metaregistry_output == actual_output


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory
):
    coins = crypto_factory.get_coins(crypto_factory_pool)
    actual_output = sum([1 for coin in coins if coin != ZERO_ADDRESS])
    metaregistry_output = populated_metaregistry.get_n_coins(
        crypto_factory_pool
    )
    assert metaregistry_output == actual_output
