import itertools
import warnings

import brownie
import pytest

from .abis import curve_pool, curve_pool_v2, gauge_controller
from .utils.constants import (
    BTC_BASEPOOL_LP_TOKEN_MAINNET,
    BTC_BASEPOOL_MAINNET,
    ETH,
    METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    WETH,
)

# --------- Parameterised Tests: checkers ---------


def test_is_registered(metaregistry, registry_pool_index_iterator):
    for registry_id, registry, pool in registry_pool_index_iterator:
        if pool != brownie.ZERO_ADDRESS:
            assert metaregistry.is_registered(pool)


def test_is_meta(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        if registry_id in [
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
        ]:
            actual_output = False
        else:
            actual_output = registry.is_meta(pool)

        metaregistry_output = metaregistry.is_meta(pool)
        assert actual_output == metaregistry_output


# --------- Parameterised Tests: getters ---------


def test_get_lp_token(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        # get_lp_token
        if registry_id in [
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        ]:
            actual_output = registry.get_lp_token(pool)
        elif registry_id == METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX:
            actual_output = pool
        else:
            actual_output = registry.get_token(pool)

        metaregistry_output = metaregistry.get_lp_token(pool)
        assert actual_output == metaregistry_output


def test_get_pool_from_lp_token(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        lp_token = metaregistry.get_lp_token(pool)
        metaregistry_output = metaregistry.get_pool_from_lp_token(lp_token)

        assert pool == metaregistry_output


def test_get_virtual_price_from_lp_token(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        lp_token = metaregistry.get_lp_token(pool)

        # virtual price from metaregistry:
        metaregistry_reverts = False
        try:
            metaregistry_output = metaregistry.get_virtual_price_from_lp_token(lp_token)
        except brownie.exceptions.VirtualMachineError:
            metaregistry_reverts = True

        # virtual price from underlying child registries:
        actual_output_reverts = False
        try:
            if registry_id in [
                METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
                METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
            ]:
                actual_output = registry.get_virtual_price_from_lp_token(lp_token)
            else:
                actual_output = curve_pool(pool).get_virtual_price()
        except brownie.exceptions.VirtualMachineError:
            actual_output_reverts = True

        if not (metaregistry_reverts and actual_output_reverts):
            assert actual_output == metaregistry_output
        else:
            # both should revert for consistency:
            skip_reason = (
                f"virtual price getter reverts for pool {pool}, "
                f"registry {registry} and metaregistry"
            )
            pytest.skip(skip_reason)


def test_get_decimals(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:
        metaregistry_output = metaregistry.get_decimals(pool)

        # get actuals and pad zeroes to match metaregistry_output length
        actual_output = list(registry.get_decimals(pool))
        actual_output += [0] * (len(metaregistry_output) - len(actual_output))

        # check if there are more than 1 decimals:
        assert metaregistry_output[1] != 0
        assert actual_output[1] != 0

        # check if they match:
        assert tuple(actual_output) == metaregistry_output


def test_get_underlying_decimals(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        # metaregistry underlying decimals:
        metaregistry_output = metaregistry.get_underlying_decimals(pool)
        assert metaregistry_output[1] != 0  # there has to be a second coin!

        # get actual decimals: first try registry
        # todo: include CryptoRegistryHandler when CryptoRegistry gets updated
        pool_is_metapool = False
        if registry_id in [
            METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        ]:
            pool_is_metapool = registry.is_meta(pool)

        if pool_is_metapool:
            actual_output = list(registry.get_underlying_decimals(pool))
            assert actual_output[2] != 0  # there has to be a third coins!
        else:
            actual_output = list(registry.get_decimals(pool))

        # pad zeros to match metaregistry_output length
        actual_output += [0] * (len(metaregistry_output) - len(actual_output))

        assert metaregistry_output == tuple(actual_output)


def test_get_coins(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        metaregistry_output = metaregistry.get_coins(pool)

        actual_output = list(registry.get_coins(pool))
        actual_output += [brownie.ZERO_ADDRESS] * (len(metaregistry_output) - len(actual_output))

        assert tuple(actual_output) == metaregistry_output


def test_get_underlying_coins(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        metaregistry_output = metaregistry.get_underlying_coins(pool)

        if registry_id in [
            METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        ]:
            try:
                actual_output = list(registry.get_underlying_coins(pool))
            except brownie.exceptions.VirtualMachineError:
                # it will revert if its not a metapool
                actual_output = list(registry.get_coins(pool))

        else:

            actual_output = list(registry.get_coins(pool))

        actual_output += [brownie.ZERO_ADDRESS] * (len(metaregistry_output) - len(actual_output))
        assert tuple(actual_output) == metaregistry_output


def test_get_balances(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:
        metaregistry_output = metaregistry.get_balances(pool)
        actual_output = list(registry.get_balances(pool))
        actual_output += [0] * (len(metaregistry_output) - len(actual_output))
        assert tuple(actual_output) == metaregistry_output


def test_get_underlying_balances(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        if sum(registry.get_balances(pool)) == 0:
            pytest.skip(f"Empty pool: {pool}")

        metaregistry_output = metaregistry.get_underlying_balances(pool)
        if metaregistry.is_meta(pool):
            assert metaregistry_output[2] > 0  # it must have a third coin
        else:
            assert metaregistry_output[1] > 0  # it must have a second coin

        is_btc_basepool = False
        if registry_id in [
            METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        ]:

            try:

                coins_in_pool = metaregistry.get_coins(pool)
                # if it is paired with a btc metapool, then the registry query
                # `get_underlying_balances` will revert since BTC metapools do not
                # have `base_pool` attribute (bug). So we'll have to try
                # getting the right balances another way:

                if coins_in_pool[1] == BTC_BASEPOOL_LP_TOKEN_MAINNET:
                    is_btc_basepool = True
                    pool_balances = registry.get_balances(pool)
                    base_pool_balances = metaregistry.get_balances(BTC_BASEPOOL_MAINNET)
                    actual_output = [0] * len(metaregistry_output)

                    # paired coin balance is on the first index
                    actual_output[0] = pool_balances[0]

                    # get btc lp token share of the pool vs total supply and get
                    # individual balances of underlying:
                    total_supply_btc_basepool_lp_token = brownie.Contract(
                        BTC_BASEPOOL_LP_TOKEN_MAINNET
                    ).totalSupply()
                    pct_pool_btc_lp_token_share = int(
                        pool_balances[1] * 10**36 / total_supply_btc_basepool_lp_token
                    )
                    for coin_id in range(3):
                        actual_output[coin_id + 1] = int(
                            base_pool_balances[coin_id] * pct_pool_btc_lp_token_share / 10**36
                        )

                else:

                    # the metaregistry uses get_balances if the pool is not a metapool:
                    if registry.is_meta(pool):
                        actual_output = registry.get_underlying_balances(pool)
                    else:
                        actual_output = registry.get_balances(pool)

            # for any other reverts, just get balances and check with metaregistry output.
            # assertion errors there will catch issues:
            except brownie.exceptions.VirtualMachineError:

                actual_output = registry.get_balances(pool)

        else:

            actual_output = registry.get_balances(pool)

        actual_output = list(actual_output)
        actual_output += [0] * (len(metaregistry_output) - len(actual_output))

        if not is_btc_basepool:
            assert tuple(actual_output) == metaregistry_output
        else:
            # because btc basepool balances are calculated, there can be
            # precision errors (different oc <1000 Wei)
            for coin_id, calculated_actual_balance in enumerate(actual_output):
                assert calculated_actual_balance - actual_output[coin_id] < 1000  # Wei


def test_get_n_coins(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        metaregistry_output = metaregistry.get_n_coins(pool)

        # crypto factory does not have get_n_coins method
        if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:

            actual_output = registry.get_n_coins(pool)

            # registry returns tuple, we want the first one (since the second)
            # index is about basepool n coins
            if not type(actual_output) == brownie.convert.datatypes.Wei:

                actual_output = actual_output[0]

            # registry returns 0 value for n coins: something's not right on the
            # registry's side. find n_coins via registry.get_coins:
            elif actual_output == 0:

                coins = registry.get_coins(pool)
                actual_output = sum([1 for coin in coins if coin != brownie.ZERO_ADDRESS])

        else:

            # do get_coins for crypto factory:
            coins = registry.get_coins(pool)
            actual_output = sum([1 for coin in coins if coin != brownie.ZERO_ADDRESS])

        assert actual_output == metaregistry_output


def test_get_n_underlying_coins(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        metaregistry_output = metaregistry.get_n_underlying_coins(pool)

        # check registry for n_coins first:
        if registry_id in [
            METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        ]:

            n_coins = registry.get_n_coins(pool)

            if type(n_coins) == brownie.convert.datatypes.Wei:

                try:

                    assert n_coins == metaregistry_output

                except AssertionError:

                    warnings.warn("Assertion broken: could be a btc metapool issue")
                    coins = registry.get_coins(pool)

                    # have to hardcode this test since btc metapool accounting
                    # has some bugs with registry:
                    if coins[1] == BTC_BASEPOOL_LP_TOKEN_MAINNET:
                        # add btc coins (3) and remove 1 lp coin = add 2:
                        assert n_coins + 2 == metaregistry_output

            elif len(list(set(n_coins))) == 1:
                # the registry returns a tuple with the same value, e.g. (3, 3)
                # such that length of the output's set is 1.
                # so we take the first one:
                assert n_coins[0] == metaregistry_output

        else:
            # if the pool contains a basepool:
            coins = registry.get_coins(pool)
            num_coins = sum([1 for coin in coins if coin != brownie.ZERO_ADDRESS])
            assert num_coins == metaregistry_output


def test_get_coin_indices(metaregistry, stable_factory_handler, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        is_meta = metaregistry.is_meta(pool)
        pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != brownie.ZERO_ADDRESS]

        base_combinations = list(itertools.combinations(pool_coins, 2))
        all_combinations = base_combinations
        if is_meta:
            underlying_coins = [
                coin
                for coin in metaregistry.get_underlying_coins(pool)
                if coin != brownie.ZERO_ADDRESS
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
            if registry_id > 1:
                indices = registry.get_coin_indices(pool, combination[0], combination[1])
                actual_output = (indices[0], indices[1], False)
            else:
                actual_output = registry.get_coin_indices(pool, combination[0], combination[1])
            # fix bug with stable registry & is_underlying always true
            if metaregistry.get_registry_handler_from_pool(pool) == stable_factory_handler.address:
                actual_output = list(actual_output)
                actual_output[-1] = not registry.is_meta(pool)
            assert actual_output == metaregistry_output


def test_get_pool_params_stableswap_cryptoswap(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        """This test is only for stableswap and cryptoswap amms"""

        print(f"testing get_pool_params for pool: {pool}")
        metaregistry_output = metaregistry.get_pool_params(pool)
        print(f"metaregistry output: {metaregistry_output}")
        actual_pool_params = [0] * 20

        v2_pool = curve_pool_v2(pool)

        # A
        if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
            actual_pool_params[0] = registry.get_A(pool)
        else:
            actual_pool_params[0] = v2_pool.A()

        # D, gamma
        if registry_id == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
            actual_pool_params[1] = registry.get_D(pool)
            actual_pool_params[2] = registry.get_gamma(pool)
        elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
            actual_pool_params[1] = v2_pool.D()
            actual_pool_params[2] = v2_pool.gamma()

        # allowed_extra_profit
        if registry_id in [
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
        ]:
            actual_pool_params[3] = v2_pool.allowed_extra_profit()
            actual_pool_params[4] = v2_pool.fee_gamma()
            actual_pool_params[5] = v2_pool.adjustment_step()
            actual_pool_params[6] = v2_pool.ma_half_time()

        print(f"actual pool params: {actual_pool_params}")
        assert actual_pool_params == metaregistry_output
        print(f"passed for pool: {pool}.")


def test_get_base_pool(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        # get_base_pool
        if registry_id in [
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
        ]:
            actual_output = brownie.ZERO_ADDRESS
        elif registry_id == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX:
            if not registry.is_meta(pool):
                actual_output = brownie.ZERO_ADDRESS
            elif registry.get_pool_asset_type(pool) == 2:
                actual_output = BTC_BASEPOOL_LP_TOKEN_MAINNET
            else:
                actual_output = registry.get_base_pool(pool)
        else:
            if not registry.is_meta(pool):
                actual_output = brownie.ZERO_ADDRESS
            else:
                actual_output = curve_pool(pool).base_pool()

        metaregistry_output = metaregistry.get_base_pool(pool)
        assert actual_output == metaregistry_output


def test_get_pool_asset_type(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        # get_pool_asset_type
        if registry_id in [
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
        ]:
            actual_output = 4
        else:
            actual_output = registry.get_pool_asset_type(pool)

        metaregistry_output = metaregistry.get_pool_asset_type(pool)
        assert actual_output == metaregistry_output


def test_get_admin_balances(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        metaregistry_output = metaregistry.get_admin_balances(pool)

        # get_admin_balances
        if registry_id != METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
            actual_output = registry.get_admin_balances(pool)
        else:
            balances = registry.get_balances(pool)
            coins = registry.get_coins(pool)
            for k in range(len(coins)):
                coin = coins[k]
                if coin in [ETH, WETH]:
                    balances[k] = brownie.accounts.at(pool).balance() - balances[k]
                else:
                    balances[k] = brownie.interface.ERC20(coin).balanceOf(pool) - balances[k]
            actual_output = balances

        for j, output in enumerate(actual_output):
            assert output == metaregistry_output[j]


def test_get_fees(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        # get_fees
        if registry_id != METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
            actual_output = registry.get_fees(pool)
        else:
            curve_contract = curve_pool_v2(pool)
            actual_output = [
                curve_contract.fee(),
                curve_contract.admin_fee(),
                curve_contract.mid_fee(),
                curve_contract.out_fee(),
            ]
        metaregistry_output = metaregistry.get_fees(pool)
        for j, output in enumerate(actual_output):
            assert output == metaregistry_output[j]


def test_get_pool_name(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        if registry_id in [
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        ]:

            actual_output = registry.get_pool_name(pool)

        elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:

            actual_output = brownie.interface.ERC20(registry.get_token(pool)).name()

        else:

            actual_output = brownie.interface.ERC20(pool).name()

        metaregistry_output = metaregistry.get_pool_name(pool)

        assert actual_output == metaregistry_output


def test_get_gauges(metaregistry, registry_pool_index_iterator):

    for registry_id, registry, pool in registry_pool_index_iterator:

        # get_gauges
        if registry_id in [
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        ]:

            actual_output = registry.get_gauges(pool)

        else:

            gauge = registry.get_gauge(pool)
            actual_output = (
                [gauge] + [brownie.ZERO_ADDRESS] * 9,
                [gauge_controller().gauge_types(gauge)] + [0] * 9,
            )

        metaregistry_output = metaregistry.get_gauges(pool)
        assert actual_output == metaregistry_output


def test_find_pool_for_coins(metaregistry, max_pools):

    registry_count = metaregistry.registry_length()
    pool_count = (
        metaregistry.pool_count()
        if max_pools == 0
        else min(max_pools * registry_count, metaregistry.pool_count())
    )

    for pool_index in range(pool_count):

        pool = metaregistry.pool_list(pool_index)
        pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != brownie.ZERO_ADDRESS]
        base_combinations = list(itertools.combinations(pool_coins, 2))
        all_combinations = base_combinations

        if metaregistry.is_meta(pool):
            underlying_coins = [
                coin
                for coin in metaregistry.get_underlying_coins(pool)
                if coin != brownie.ZERO_ADDRESS
            ]
            all_combinations = all_combinations + [
                (pool_coins[0], coin) for coin in underlying_coins if pool_coins[0] != coin
            ]

        for combination in all_combinations:

            registered = False

            for j in range(pool_count):

                pool_for_the_pair = metaregistry.find_pool_for_coins(
                    combination[0], combination[1], j
                )

                if pool_for_the_pair == pool:
                    registered = True
                    break

                if pool_for_the_pair == brownie.ZERO_ADDRESS:
                    break

            assert registered
