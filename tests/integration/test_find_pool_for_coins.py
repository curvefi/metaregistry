import itertools

from tests.utils.constants import ADDRESS_ZERO


def test_find_coins(metaregistry):
    pool_count = metaregistry.pool_count()
    for pool_index in range(pool_count):
        pool = metaregistry.pool_list(pool_index)

        pool_coins = [
            coin for coin in metaregistry.get_coins(pool) if coin != ADDRESS_ZERO
        ]

        base_combinations = list(itertools.combinations(pool_coins, 2))
        all_combinations = base_combinations
        if metaregistry.is_meta(pool):
            underlying_coins = [
                coin
                for coin in metaregistry.get_underlying_coins(pool)
                if coin != ADDRESS_ZERO
            ]
            all_combinations = all_combinations + [
                (pool_coins[0], coin) for coin in underlying_coins
            ]
        print(
            f"Found {len(all_combinations)} combination for pool: {pool} ({pool_index}/{pool_count})"
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
                if pool_for_the_pair == ADDRESS_ZERO:
                    break

            assert registered == True
