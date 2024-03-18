from itertools import combinations
from os import environ

import pytest
from eth.constants import ZERO_ADDRESS

# NOTE: This is the most important method in the metaregistry contract since it will be used
# by integrators to find pools for coin pairs. It finds pools even if the coin pair is not
# a direct coin pair, but has a path through a metapool.


def _get_all_combinations(metaregistry, pool):
    pool_coins = [
        coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS
    ]
    all_combinations = list(combinations(pool_coins, 2))
    first_coin = pool_coins[0]

    # there exist some pools with an LP token as the first coin, that's incorrect
    # example: 0xf5d5305790c1af08e9df44b30a1afe56ccda72df
    lp_token_pool = metaregistry.get_pool_from_lp_token(first_coin)
    is_first_coin_lp_token = lp_token_pool and lp_token_pool != ZERO_ADDRESS

    if metaregistry.is_meta(pool) and not is_first_coin_lp_token:
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


@pytest.mark.skipif(
    condition=environ.get("TEST_ALL") == "False",
    reason="This test is too slow, don't run it locally every time.",
)
def test_all(populated_metaregistry, pool):
    all_combinations = _get_all_combinations(populated_metaregistry, pool)
    for coin1, coin2 in all_combinations:
        pools_containing_pair = populated_metaregistry.find_pools_for_coins(
            coin1, coin2
        )
        assert pool in pools_containing_pair, (
            f"Cannot find pool {pool} for coin combination {coin1} and {coin2}. "
            f"Pools found {pools_containing_pair}"
        )

        # test with specified index
        assert pools_containing_pair == [
            populated_metaregistry.find_pool_for_coins(coin1, coin2, i)
            for i in range(len(pools_containing_pair))
        ]
