import itertools

from brownie import ZERO_ADDRESS


def test_get_coin_indices(metaregistry, registries, sync_limit):

    print("MetaRegistry registry_length(): ", metaregistry.registry_length())

    for i, registry in enumerate(registries):

        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit

        for pool_index in range(total_pools):

            pool = registry.pool_list(pool_index)

            print(f"Checking if pool {pool} is a metapool, in registry {registry}")
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

            for combination in all_combinations:
                if combination[0] == combination[1]:
                    continue
                metaregistry_output = metaregistry.get_coin_indices(
                    pool, combination[0], combination[1]
                )
                if i >= 2:
                    indices = registry.get_coin_indices(
                        pool, combination[0], combination[1]
                    )
                    actual_output = (indices[0], indices[1], False)
                else:
                    actual_output = registry.get_coin_indices(
                        pool, combination[0], combination[1]
                    )
                # fix bug with stable registry & is_underlying always true
                if metaregistry.pool_to_registry(pool)[0] == 1:
                    actual_output = list(actual_output)
                    actual_output[-1] = not registry.is_meta(pool)
                assert actual_output == metaregistry_output
