import itertools

from brownie import ZERO_ADDRESS


def test_find_coins(metaregistry, max_pools):
    registry_count = metaregistry.registry_length()
    pool_count = (
        metaregistry.pool_count()
        if max_pools == 0
        else min(max_pools * registry_count, metaregistry.pool_count())
    )
    for pool_index in range(pool_count):
        pool = metaregistry.pool_list(pool_index)

        pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS]

        base_combinations = list(itertools.combinations(pool_coins, 2))
        all_combinations = base_combinations
        if metaregistry.is_meta(pool):
            underlying_coins = [
                coin for coin in metaregistry.get_underlying_coins(pool) if coin != ZERO_ADDRESS
            ]
            all_combinations = all_combinations + [
                (pool_coins[0], coin) for coin in underlying_coins if pool_coins[0] != coin
            ]
        print(
            f"Found {len(all_combinations)} "
            f"combination for pool: {pool} ({pool_index}/{pool_count})"
        )
        for combination in all_combinations:
            registered = False
            for j in range(pool_count):
                pool_for_the_pair = metaregistry.find_pool_for_coins(
                    combination[0], combination[1], j
                )
                if pool_for_the_pair == pool:
                    registered = True
                    break
                if pool_for_the_pair == ZERO_ADDRESS:
                    break

            assert registered
