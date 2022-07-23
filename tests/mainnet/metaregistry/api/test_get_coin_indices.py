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


def _get_coin_indices(pool, coin_a, coin_b, metaregistry, max_coins):
    # this is the exact same logic as in the crypto factory handler

    _coins = metaregistry.get_coins(pool)
    found_market: bool = False
    result = [0] * 3

    # check coin markets
    for x in range(max_coins):
        coin = _coins[x]
        if coin == ape.utils.ZERO_ADDRESS:
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
            if coin == ape.utils.ZERO_ADDRESS:
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


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory, max_coins
):

    all_combinations = _get_coin_combinations(populated_metaregistry, crypto_factory_pool)

    for combination in all_combinations:
        if combination[0] == combination[1]:
            continue
        metaregistry_output = populated_metaregistry.get_coin_indices(
            crypto_factory_pool, combination[0], combination[1]
        )

        try:

            actual_output = list(
                crypto_factory.get_coin_indices(crypto_factory_pool, combination[0], combination[1])
            )

        # ---- Crypto factory: 0xF18056Bbd320E96A48e3Fbf8bC061322531aac99> method get_coin_indices
        # ---- reverts for pool: 0x595146ED98c81Dde9bD23d0c2Ab5b807C7Fe2D9f. special treatment:
        except ape.exceptions.ContractLogicError:

            actual_output = _get_coin_indices(
                crypto_factory_pool,
                combination[0],
                combination[1],
                populated_metaregistry,
                max_coins,
            )

        for i in range(len(actual_output)):
            assert actual_output[i] == metaregistry_output[i]
