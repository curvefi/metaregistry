import itertools
import warnings

import brownie
import pytest

from tests.abis import curve_pool, curve_pool_v2, gauge_controller
from tests.utils.constants import (
    BTC_BASEPOOL_LP_TOKEN_MAINNET,
    METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
)

MAX_POOLS = 1000


def check_pool_already_registered(
    metaregistry, pool, registry_handler_for_pool, handler_id: int = 0
):
    """Checks whether the pool was already registered in a different registry.

    Args:
        metaregistry (fixture): MetaRegistry contract fixture.
        pool (str): address of pool
        registry (brownie.Contract): Contract instance of registry.
        handler_id (int): 0 if pool is registered at only 1 registry, > 0 otherwise.
    """
    registered_handlers = metaregistry.get_registry_handlers_from_pool(pool)
    registry_handlers = []
    for registry_handler in registered_handlers:
        if registry_handler == brownie.ZERO_ADDRESS:
            break
        registry_handlers.append(registry_handler)

    if len(registry_handlers) > 1:
        warnings.warn(f"Pool {pool} is registered in more than one registry.")

    if registry_handler_for_pool != registry_handlers[handler_id]:
        warnings.warn(
            "Pool already registred in another registry. "
            f"Pool: {pool}, "
            f"registry handler for pool: {registry_handler_for_pool}, "
            f"registry handler in metaregistry: {registry_handlers[handler_id]}"
        )
        return True
    return False


def skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator):
    if pool_id >= len(registry_pool_index_iterator):
        pytest.skip()


# --------- Parameterised Tests: checkers ---------


def test_max_pools_covers_all_pools(registry_pool_index_iterator):
    assert MAX_POOLS > len(registry_pool_index_iterator)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_is_registered(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    if pool != brownie.ZERO_ADDRESS:
        assert metaregistry.is_registered(pool)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_is_meta(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if registry_id in [
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    ]:
        actual_output = False  # mainnet crypto registries don't have this method.
    else:
        actual_output = registry.is_meta(pool)

    metaregistry_output = metaregistry.is_meta(pool)
    assert actual_output == metaregistry_output


# --------- Parameterised Tests: getters ---------


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_lp_token(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

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


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_from_lp_token(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    lp_token = metaregistry.get_lp_token(pool)
    metaregistry_output = metaregistry.get_pool_from_lp_token(lp_token)

    assert pool == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_virtual_price_from_lp_token(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    lp_token = metaregistry.get_lp_token(pool)

    registry_reverts = False
    try:
        # virtual price from underlying child registries:
        if registry_id in [
            METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        ]:
            actual_output = registry.get_virtual_price_from_lp_token(lp_token)
        else:
            actual_output = curve_pool(pool).get_virtual_price()
    except brownie.exceptions.VirtualMachineError:
        registry_reverts = True

    # if child registry call reverts, then metaregistry must revert too
    if registry_reverts:
        with brownie.reverts():
            metaregistry.get_virtual_price_from_lp_token(pool)
    else:
        # virtual price from metaregistry:
        metaregistry_output = metaregistry.get_virtual_price_from_lp_token(lp_token)
        assert actual_output == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_decimals(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_decimals(pool)

    # get actuals and pad zeroes to match metaregistry_output length
    actual_output = list(registry.get_decimals(pool))
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))

    # check if there are more than 1 decimals:
    assert metaregistry_output[1] != 0
    assert actual_output[1] != 0

    # check if they match:
    assert tuple(actual_output) == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_decimals(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

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

    pool_underlying_decimals_exceptions = {
        # eth: ankreth pool returns [18, 0] when it should return:
        "0xA96A65c051bF88B4095Ee1f2451C2A9d43F53Ae2": [18, 18],
        # compound pools. ctokens are 8 decimals. underlying is dai usdc:
        "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56": [18, 6],
        # cream-yearn cytokens are 8 decimals, whereas underlying is
        # dai usdc usdt:
        "0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF": [18, 6, 6],
        # usdt pool has cDAI, cUSDC and USDT (which is 8, 8, 6):
        "0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C": [18, 6, 6],
    }

    if pool in pool_underlying_decimals_exceptions:
        actual_output = pool_underlying_decimals_exceptions[pool]
    elif pool_is_metapool:
        actual_output = list(registry.get_underlying_decimals(pool))
        assert actual_output[2] != 0  # there has to be a third coins!
    else:
        actual_output = list(registry.get_decimals(pool))

    # pad zeros to match metaregistry_output length
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))

    assert metaregistry_output == tuple(actual_output)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    metaregistry_output = metaregistry.get_coins(pool)

    actual_output = list(registry.get_coins(pool))
    actual_output += [brownie.ZERO_ADDRESS] * (len(metaregistry_output) - len(actual_output))

    assert tuple(actual_output) == metaregistry_output


def _get_underlying_coins_from_registry(registry_id, registry, pool):

    if registry_id in [
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    ]:

        return registry.get_underlying_coins(pool)

    else:

        return registry.get_coins(pool)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_underlying_coins(pool)

    try:
        actual_output = _get_underlying_coins_from_registry(registry_id, registry, pool)
    except brownie.exceptions.VirtualMachineError:
        assert not registry.is_meta(pool)
        actual_output = registry.get_coins(pool)

    for idx, registry_value in enumerate(actual_output):
        assert registry_value == metaregistry_output[idx]


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_balances(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_balances(pool)
    actual_output = list(registry.get_balances(pool))
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))
    assert tuple(actual_output) == metaregistry_output


def _get_underlying_balances_from_registry(registry_id, registry, pool):

    if registry_id in [
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    ] and registry.is_meta(pool):

        # the metaregistry uses get_balances if the pool is not a metapool:
        return registry.get_underlying_balances(pool)

    else:

        return registry.get_balances(pool)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_balances(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    registry_query_reverts = False
    try:
        actual_output = _get_underlying_balances_from_registry(registry_id, registry, pool)
    except brownie.exceptions.VirtualMachineError:
        registry_query_reverts = True

    if sum(registry.get_balances(pool)) == 0:
        pytest.skip(f"Empty pool: {pool}")

    if registry_query_reverts:
        with brownie.reverts():
            metaregistry.get_underlying_balances(pool)
    else:
        metaregistry_output = metaregistry.get_underlying_balances(pool)

        if metaregistry.is_meta(pool):
            assert metaregistry_output[2] > 0  # it must have a third coin
        else:
            assert metaregistry_output[1] > 0  # it must have a second coin

        for idx, registry_value in enumerate(actual_output):
            assert registry_value == metaregistry_output[idx]


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_n_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

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


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_n_underlying_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

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
                # have to hardcode this test since btc metapool accounting
                # has some bugs with registry:
                coins = registry.get_coins(pool)
                if coins[1] == BTC_BASEPOOL_LP_TOKEN_MAINNET:
                    # add btc coins (3) and remove 1 lp coin = add 2:
                    assert n_coins + 2 == metaregistry_output

        elif len(set(n_coins)) == 1:
            # the registry returns a tuple with the same value, e.g. (3, 3)
            # such that length of the output's set is 1.
            # so we take the first one:
            assert n_coins[0] == metaregistry_output

    else:
        # if the pool contains a basepool:
        coins = registry.get_coins(pool)
        num_coins = sum([1 for coin in coins if coin != brownie.ZERO_ADDRESS])
        assert num_coins == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_coin_indices(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    is_meta = metaregistry.is_meta(pool)
    pool_coins = [coin for coin in metaregistry.get_coins(pool) if coin != brownie.ZERO_ADDRESS]

    base_combinations = list(itertools.combinations(pool_coins, 2))
    all_combinations = base_combinations
    if is_meta:
        underlying_coins = [
            coin for coin in metaregistry.get_underlying_coins(pool) if coin != brownie.ZERO_ADDRESS
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


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_params_stableswap_cryptoswap(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

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


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_base_pool(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    actual_output = brownie.ZERO_ADDRESS

    if registry_id == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX and registry.is_meta(pool):
        # stable registry does not have get_base_pool method
        actual_output = registry.get_pool_from_lp_token(registry.get_coins(pool)[1])

    elif registry_id == METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX and metaregistry.is_meta(pool):

        # this might exclude BTC pools, since they dont have a base pool!
        actual_output = registry.get_base_pool(pool)

    metaregistry_output = metaregistry.get_base_pool(pool)
    assert actual_output == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_asset_type(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

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


def _get_admin_balances_crypto(registry_id, registry, pool, metaregistry, alice):

    v2_pool = curve_pool_v2(pool)
    if registry_id == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
        fee_receiver = v2_pool.admin_fee_receiver()
    elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
        fee_receiver = registry.fee_receiver()

    lp_token = brownie.interface.ERC20(metaregistry.get_lp_token(pool))
    fee_receiver_token_balance_before = lp_token.balanceOf(fee_receiver)
    v2_pool.claim_admin_fees({"from": alice})
    claimed_lp_token_as_fee = lp_token.balanceOf(fee_receiver) - fee_receiver_token_balance_before
    total_supply_lp_token = lp_token.totalSupply()

    frac_admin_fee = int(claimed_lp_token_as_fee * 10**18 / total_supply_lp_token)

    # get admin balances in individual assets:
    reserves = metaregistry.get_balances(pool)
    admin_balances = [0] * 8
    for i in range(8):
        admin_balances[i] = int(frac_admin_fee * reserves[i] / 10**18)

    return admin_balances


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_admin_balances(metaregistry, registry_pool_index_iterator, pool_id, alice, chain):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    if sum(metaregistry.get_balances(pool)) == 0:
        pytest.skip("empty pool: skipping")

    if brownie.interface.ERC20(metaregistry.get_lp_token(pool)).totalSupply() == 0:
        pytest.skip("lp token supply is zero")

    if registry_id in [
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    ]:
        actual_output = registry.get_admin_balances(pool)
        metaregistry_output = metaregistry.get_admin_balances(pool)
        for i, output in enumerate(actual_output):
            assert output == metaregistry_output[i]
    else:
        chain.snapshot()
        actual_output = _get_admin_balances_crypto(registry_id, registry, pool, metaregistry, alice)
        chain.revert()
        metaregistry_output = metaregistry.get_admin_balances(pool)
        for i, output in enumerate(actual_output):
            assert output == pytest.approx(metaregistry_output[i])


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_fees(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    # get_fees
    actuals_reverts = False
    try:
        if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
            actual_output = registry.get_fees(pool)
        else:
            curve_contract = curve_pool_v2(pool)
            actual_output = [
                curve_contract.fee(),
                curve_contract.admin_fee(),
                curve_contract.mid_fee(),
                curve_contract.out_fee(),
            ]
    except brownie.exceptions.VirtualMachineError:
        actuals_reverts = True

    if actuals_reverts:
        with brownie.reverts():
            metaregistry.get_fees(pool)
    else:
        metaregistry_output = metaregistry.get_fees(pool)
        for j, output in enumerate(actual_output):
            assert output == metaregistry_output[j]


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_name(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

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


def _get_gauges_actual(registry, registry_id, pool):

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

    return actual_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_gauges(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gt_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    # check if registry query reverts:
    registry_reverts = False
    try:
        actual_output = _get_gauges_actual(registry, registry_id, pool)
    except brownie.exceptions.VirtualMachineError:
        registry_reverts = True

    if registry_reverts:
        with brownie.reverts():
            metaregistry.get_gauges(pool)
    else:
        metaregistry_output = metaregistry.get_gauges(pool)
        assert actual_output == metaregistry_output


def test_find_pool_for_coins(metaregistry):

    pool_count = metaregistry.pool_count()
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
