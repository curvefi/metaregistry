import itertools

import ape


def _get_coin_combinations(metaregistry, pool):

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

    return all_combinations


def test_stable_registry_pools(populated_metaregistry, stable_registry_pool, stable_registry):

    all_combinations = _get_coin_combinations(populated_metaregistry, stable_registry_pool)

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        metaregistry_output = populated_metaregistry.get_coin_indices(
            stable_registry_pool, combination[0], combination[1]
        )
        actual_output = list(
            stable_registry.get_coin_indices(stable_registry_pool, combination[0], combination[1])
        )

        assert tuple(actual_output) == metaregistry_output


def test_stable_factory_pools(populated_metaregistry, stable_factory_pool, stable_factory):

    all_combinations = _get_coin_combinations(populated_metaregistry, stable_factory_pool)

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        metaregistry_output = populated_metaregistry.get_coin_indices(
            stable_factory_pool, combination[0], combination[1]
        )
        actual_output = list(
            stable_factory.get_coin_indices(stable_factory_pool, combination[0], combination[1])
        )

        # fix bug with stable factory where returned `is_underlying` is always True
        # so check if pool is metapool and basepool lp token is not in combination
        # (then `is_underlying` == True)
        actual_output[-1] = False
        if (
            stable_factory.is_meta(stable_factory_pool)
            and not stable_factory.get_coins(stable_factory_pool)[1] in combination
        ):
            actual_output[-1] = True

        assert tuple(actual_output) == metaregistry_output


def test_crypto_registry_pools(populated_metaregistry, crypto_registry_pool, crypto_registry):

    all_combinations = _get_coin_combinations(populated_metaregistry, crypto_registry_pool)

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        metaregistry_output = populated_metaregistry.get_coin_indices(
            crypto_registry_pool, combination[0], combination[1]
        )
        actual_output = list(
            crypto_registry.get_coin_indices(crypto_registry_pool, combination[0], combination[1])
        )

        # mainnet crypto registry and crypto factory do not return `is_underlying`
        # but metaregistry does (since stable registry and factory do)
        actual_output = (actual_output[0], actual_output[1], False)

        assert tuple(actual_output) == metaregistry_output


def test_crypto_factory_pools(populated_metaregistry, crypto_factory_pool, crypto_factory):

    all_combinations = _get_coin_combinations(populated_metaregistry, crypto_factory_pool)

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        metaregistry_output = populated_metaregistry.get_coin_indices(
            crypto_factory_pool, combination[0], combination[1]
        )
        actual_output = list(
            crypto_factory.get_coin_indices(crypto_factory_pool, combination[0], combination[1])
        )

        # mainnet crypto registry and crypto factory do not return `is_underlying`
        # but metaregistry does (since stable registry and factory do)
        actual_output = (actual_output[0], actual_output[1], False)

        assert tuple(actual_output) == metaregistry_output
