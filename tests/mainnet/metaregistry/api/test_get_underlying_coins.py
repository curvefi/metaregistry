import warnings

import boa
from boa import BoaError
from eth.constants import ZERO_ADDRESS


def _get_underlying_coins(
    registry, base_pool_registry_updated, pool, max_coins
):
    coins = registry.get_coins(pool)
    underlying_coins = [ZERO_ADDRESS] * max_coins

    for idx, coin in enumerate(coins):
        base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)

        if base_pool == ZERO_ADDRESS:
            underlying_coins[idx] = coin

        else:
            basepool_coins = base_pool_registry_updated.get_coins(base_pool)

            for bp_coin in basepool_coins:
                if bp_coin == ZERO_ADDRESS:
                    break

                underlying_coins[idx] = bp_coin
                idx += 1

            break

    return underlying_coins


def _check_fetched_underlying_coins(registry, pool, underlying_coins):
    try:
        registry_underlying_coins = registry.get_underlying_coins(pool)
        if registry_underlying_coins != underlying_coins:
            warnings.warn(f"Pool {pool} might be a lending pool.")
            return registry_underlying_coins

    except BoaError:
        # virtual machine errors prop up for registry.get_underlying_coins if pool
        # is completely depegged. We check this by setting up a revert check and
        # then returning underlying_coins:git
        balances = registry.get_balances(pool)
        decimals = registry.get_decimals(pool)

        float_balances = [
            balances[i] / 10 ** decimals[i] for i in range(len(decimals))
        ]
        if min(float_balances) < 1:
            with boa.reverts():
                registry.get_underlying_coins(pool)
            return underlying_coins

    return underlying_coins


def test_stable_registry_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    stable_registry_pool,
    stable_registry,
    max_coins,
):
    metaregistry_output = populated_metaregistry.get_underlying_coins(
        stable_registry_pool
    )
    actual_output = _get_underlying_coins(
        stable_registry,
        populated_base_pool_registry,
        stable_registry_pool,
        max_coins,
    )
    actual_output = _check_fetched_underlying_coins(
        stable_registry, stable_registry_pool, actual_output
    )

    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]


def test_stable_factory_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    stable_factory_pool,
    stable_factory,
    max_coins,
):
    metaregistry_output = populated_metaregistry.get_underlying_coins(
        stable_factory_pool
    )
    actual_output = _get_underlying_coins(
        stable_factory,
        populated_base_pool_registry,
        stable_factory_pool,
        max_coins,
    )
    actual_output = _check_fetched_underlying_coins(
        stable_factory, stable_factory_pool, actual_output
    )

    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]


def test_crypto_registry_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    crypto_registry_pool,
    crypto_registry,
    max_coins,
):
    metaregistry_output = populated_metaregistry.get_underlying_coins(
        crypto_registry_pool
    )
    actual_output = _get_underlying_coins(
        crypto_registry,
        populated_base_pool_registry,
        crypto_registry_pool,
        max_coins,
    )
    actual_output = _check_fetched_underlying_coins(
        crypto_registry, crypto_registry_pool, actual_output
    )

    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]


def test_crypto_factory_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    crypto_factory_pool,
    crypto_factory,
    max_coins,
):
    metaregistry_output = populated_metaregistry.get_underlying_coins(
        crypto_factory_pool
    )
    actual_output = _get_underlying_coins(
        crypto_factory,
        populated_base_pool_registry,
        crypto_factory_pool,
        max_coins,
    )
    try:
        assert actual_output == metaregistry_output
    except AssertionError:
        # there exist some pools with an LP token as the first coin, that's incorrect
        # example: 0xf5d5305790c1af08e9dF44b30A1afe56cCda72df
        first_coin = metaregistry_output[0]
        assert populated_metaregistry.get_pool_from_lp_token(first_coin)
        assert actual_output == metaregistry_output[1:] + [ZERO_ADDRESS]
