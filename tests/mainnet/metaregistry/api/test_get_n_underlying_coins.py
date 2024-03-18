from eth.constants import ZERO_ADDRESS


def _get_num_coins(registry, pool, base_pool_registry):
    coins = registry.get_coins(pool)
    num_coins = 0
    for coin in coins:
        if coin == ZERO_ADDRESS:
            break

        base_pool = base_pool_registry.get_base_pool_for_lp_token(coin)

        if base_pool != ZERO_ADDRESS:
            basepool_coins = base_pool_registry.get_coins(base_pool)
            num_bp_coins = sum(
                [1 for i in basepool_coins if i != ZERO_ADDRESS]
            )
            num_coins += num_bp_coins

        else:
            num_coins += 1

    return num_coins


def test_stable_registry_pools(
    populated_metaregistry,
    stable_registry_pool,
    stable_registry,
    populated_base_pool_registry,
):
    metaregistry_output = populated_metaregistry.get_n_underlying_coins(
        stable_registry_pool
    )
    num_coins = _get_num_coins(
        stable_registry, stable_registry_pool, populated_base_pool_registry
    )

    assert metaregistry_output == num_coins


def test_stable_factory_pools(
    populated_metaregistry,
    stable_factory_pool,
    stable_factory,
    populated_base_pool_registry,
):
    metaregistry_output = populated_metaregistry.get_n_underlying_coins(
        stable_factory_pool
    )
    num_coins = _get_num_coins(
        stable_factory, stable_factory_pool, populated_base_pool_registry
    )

    assert metaregistry_output == num_coins


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    crypto_registry,
    populated_base_pool_registry,
):
    metaregistry_output = populated_metaregistry.get_n_underlying_coins(
        crypto_registry_pool
    )
    num_coins = _get_num_coins(
        crypto_registry, crypto_registry_pool, populated_base_pool_registry
    )

    assert metaregistry_output == num_coins


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    populated_base_pool_registry,
):
    metaregistry_output = populated_metaregistry.get_n_underlying_coins(
        crypto_factory_pool
    )
    num_coins = _get_num_coins(
        crypto_factory, crypto_factory_pool, populated_base_pool_registry
    )

    assert metaregistry_output == num_coins
