import itertools

import pytest

from tests.utils import ZERO_ADDRESS

# NOTE: This is the most important method in the metaregistry contract since it will be used
# by integrators to find pools for coin pairs. It finds pools even if the coin pair is not
# a direct coin pair, but has a path through a metapool.


def _get_all_combinations(metaregistry, pool):
    pool_coins = [
        coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS
    ]
    all_combinations = list(itertools.combinations(pool_coins, 2))
    first_coin = pool_coins[0]

    if metaregistry.is_meta(pool):
        underlying_coins = [
            coin
            for coin in metaregistry.get_underlying_coins(pool)
            if coin != ZERO_ADDRESS
        ]
        all_combinations += [
            (first_coin, coin)
            for coin in underlying_coins
            if first_coin != coin
        ]

    return all_combinations


@pytest.mark.skip()  # TODO: This test is spawning a lot of test cases and takes >1:30h to run
def test_all(populated_metaregistry, pool):
    combinations = _get_all_combinations(populated_metaregistry, pool)
    for combination in combinations:
        pools_containing_pair = populated_metaregistry.find_pools_for_coins(
            *combination
        )
        assert pool in pools_containing_pair

        for i, found_pool in enumerate(pools_containing_pair):
            assert (
                populated_metaregistry.find_pool_for_coins(*combination, i)
                == found_pool
            )
