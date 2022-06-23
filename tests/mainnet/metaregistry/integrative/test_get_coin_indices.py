import itertools

from brownie import ZERO_ADDRESS


def test_get_coin_indices(metaregistry, registries, stable_factory_handler, max_pools):

    print("MetaRegistry registry_length(): ", metaregistry.registry_length())

    for i, registry in enumerate(registries):

        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )

        for pool_index in range(total_pools):

            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            if registry != registry_in_meta_registry:
                continue

            print(f"Checking if pool {pool} is a metapool, in registry {registry}")
            is_meta = metaregistry.is_meta(pool)
            pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS]

            base_combinations = list(itertools.combinations(pool_coins, 2))
            all_combinations = base_combinations
            if is_meta:
                underlying_coins = [
                    coin for coin in metaregistry.get_underlying_coins(pool) if coin != ZERO_ADDRESS
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
                    indices = registry.get_coin_indices(pool, combination[0], combination[1])
                    actual_output = (indices[0], indices[1], False)
                else:
                    actual_output = registry.get_coin_indices(pool, combination[0], combination[1])
                # fix bug with stable registry & is_underlying always true
                if (
                    metaregistry.get_registry_handler_from_pool(pool)
                    == stable_factory_handler.address
                ):
                    actual_output = list(actual_output)
                    actual_output[-1] = not registry.is_meta(pool)
                assert actual_output == metaregistry_output
