import ape
import itertools


def test_get_coin_indices(metaregistry, pool):

    is_meta = metaregistry.is_meta(pool)
    pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != ape.utils.ZERO_ADDRESS]

    base_combinations = list(itertools.combinations(pool_coins, 2))
    all_combinations = base_combinations
    if is_meta:
        underlying_coins = [
            coin
            for coin in metaregistry.get_underlying_coins(pool)
            if coin != ape.utils.ZERO_ADDRESS
        ]
        all_combinations = all_combinations + [(pool_coins[0], coin) for coin in underlying_coins]

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        metaregistry_output = metaregistry.get_coin_indices(pool, combination[0], combination[1])
        actual_output = list(registry.get_coin_indices(pool, combination[0], combination[1]))

        if registry_id == 1:
            # fix bug with stable factory where returned `is_underlying` is always True

            # so check if pool is metapool and basepool lp token is not in combination
            # (then `is_underlying` == True)
            actual_output[-1] = False
            if registry.is_meta(pool) and not registry.get_coins(pool)[1] in combination:
                actual_output[-1] = True

        elif registry_id in [2, 3]:
            # mainnet crypto registry and crypto factory do not return `is_underlying`
            # but metaregistry does (since stable registry and factory do)
            actual_output = (actual_output[0], actual_output[1], False)

        assert actual_output == metaregistry_output
