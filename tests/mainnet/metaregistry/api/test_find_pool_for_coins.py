import itertools

import ape


def _get_all_combinations(metaregistry, pool):

    pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != ape.utils.ZERO_ADDRESS]
    base_combinations = list(itertools.combinations(pool_coins, 2))
    all_combinations = base_combinations

    if metaregistry.is_meta(pool):
        underlying_coins = [
            coin
            for coin in metaregistry.get_underlying_coins(pool)
            if coin != ape.utils.ZERO_ADDRESS
        ]
        all_combinations = all_combinations + [
            (pool_coins[0], coin) for coin in underlying_coins if pool_coins[0] != coin
        ]

    return all_combinations


def test_all(populated_metaregistry, pool):

    pool_count = populated_metaregistry.pool_count()
    for combination in _get_all_combinations(populated_metaregistry, pool):

        registered = False

        for i in range(pool_count):

            pool_for_the_pair = populated_metaregistry.find_pool_for_coins(
                combination[0], combination[1], i
            )

            if pool_for_the_pair == pool:
                registered = True
                break

            if pool_for_the_pair == ape.utils.ZERO_ADDRESS:
                break

        assert registered
