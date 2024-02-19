import itertools
import warnings

import pytest
from eth.constants import ZERO_ADDRESS


def _reject_pools_with_one_coin(metaregistry, pool):
    pool_coins = [
        coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS
    ]
    if len(list(set(pool_coins))) == 1:
        warnings.warn(f"Pool {pool} has only one coin!")
        pytest.skip("Pool has only one coin")


def _get_coin_combinations(metaregistry, pool):
    # skip tests if pool has only one coin:
    _reject_pools_with_one_coin(metaregistry, pool)

    is_meta = metaregistry.is_meta(pool)
    pool_coins = [
        coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS
    ]

    base_combinations = list(itertools.combinations(pool_coins, 2))
    all_combinations = base_combinations
    if is_meta:
        underlying_coins = [
            coin
            for coin in metaregistry.get_underlying_coins(pool)
            if coin != ZERO_ADDRESS
        ]
        all_combinations = all_combinations + [
            (pool_coins[0], coin) for coin in underlying_coins
        ]

    return all_combinations


def _get_coin_indices(pool, coin_a, coin_b, metaregistry, max_coins):
    # this is the exact same logic as in the crypto factory handler

    _coins = metaregistry.get_coins(pool)
    found_market: bool = False
    result = [0] * 3

    # check coin markets
    for x in range(max_coins):
        coin = _coins[x]
        if coin == ZERO_ADDRESS:
            # if we reach the end of the coins, reset `found_market` and try again
            # with the underlying coins
            found_market = False
            break
        if coin == coin_a:
            result[0] = x
        elif coin == coin_b:
            result[1] = x
        else:
            continue

        if found_market:
            # the second time we find a match, break out of the loop
            break
        # the first time we find a match, set `found_market` to True
        found_market = True

    if not found_market and metaregistry.is_meta(pool):
        # check underlying coin markets
        underlying_coins = metaregistry.get_underlying_coins(pool)

        for x in range(max_coins):
            coin = underlying_coins[x]
            if coin == ZERO_ADDRESS:
                raise "No available market"
            if coin == coin_a:
                result[0] = x
            elif coin == coin_b:
                result[1] = x
            else:
                continue

            if found_market:
                result[2] = 1
                break
            found_market = True

    return result[0], result[1], result[2] > 0


def _test_coin_indices(coin_a, coin_b, metaregistry, pool, max_coins):
    if coin_a != coin_b:
        metaregistry_output = metaregistry.get_coin_indices(
            pool, coin_a, coin_b
        )

        actual_output = _get_coin_indices(
            pool,
            coin_a,
            coin_b,
            metaregistry,
            max_coins,
        )

        assert tuple(actual_output) == metaregistry_output


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, max_coins
):
    all_combinations = _get_coin_combinations(
        populated_metaregistry, stable_registry_pool
    )

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        _test_coin_indices(
            combination[0],
            combination[1],
            populated_metaregistry,
            stable_registry_pool,
            max_coins,
        )


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, max_coins
):
    all_combinations = _get_coin_combinations(
        populated_metaregistry, stable_factory_pool
    )

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        _test_coin_indices(
            combination[0],
            combination[1],
            populated_metaregistry,
            stable_factory_pool,
            max_coins,
        )


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, max_coins
):
    all_combinations = _get_coin_combinations(
        populated_metaregistry, crypto_registry_pool
    )

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        _test_coin_indices(
            combination[0],
            combination[1],
            populated_metaregistry,
            crypto_registry_pool,
            max_coins,
        )


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, max_coins
):
    all_combinations = _get_coin_combinations(
        populated_metaregistry, crypto_factory_pool
    )

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        _test_coin_indices(
            combination[0],
            combination[1],
            populated_metaregistry,
            crypto_factory_pool,
            max_coins,
        )
