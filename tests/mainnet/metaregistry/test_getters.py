import itertools
import warnings

import brownie
import pytest

from tests.abis import curve_pool, curve_pool_v2, gauge_controller, liquidity_gauge
from tests.utils.constants import (
    MAX_COINS,
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


def skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator):
    if pool_id >= len(registry_pool_index_iterator):
        pytest.skip()


# --------- Parameterised Tests: checkers ---------


def test_max_pools_covers_all_pools(registry_pool_index_iterator):
    assert MAX_POOLS > len(registry_pool_index_iterator)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_is_registered(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    if pool != brownie.ZERO_ADDRESS:
        assert metaregistry.is_registered(pool)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_is_meta(metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
        coins = registry.get_coins(pool)
        actual_output = False
        for i in range(len(coins)):
            if (
                base_pool_registry_updated.get_base_pool_for_lp_token(coins[i])
                != brownie.ZERO_ADDRESS
            ):
                actual_output = True
                break
    else:
        actual_output = registry.is_meta(pool)

    metaregistry_output = metaregistry.is_meta(pool)
    assert actual_output == metaregistry_output


# --------- Parameterised Tests: getters ---------


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_lp_token(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    lp_token = metaregistry.get_lp_token(pool)
    metaregistry_output = metaregistry.get_pool_from_lp_token(lp_token)

    assert pool == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_virtual_price_from_lp_token(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    # skip if pool has little to no liquidity, since vprice queries will most likely bork:
    pool_balances = metaregistry.get_balances(pool)
    lp_token = metaregistry.get_lp_token(pool)
    if sum(pool_balances) == 0:

        with brownie.reverts():
            metaregistry.get_virtual_price_from_lp_token(lp_token)

        pytest.skip(f"empty pool: {pool}")

    elif sum(pool_balances) < 100:  # tiny pool
        with brownie.reverts():
            metaregistry.get_virtual_price_from_lp_token(lp_token)

        pytest.skip(f"tiny pool: {pool}")

    coin_decimals = metaregistry.get_decimals(pool)
    coins = metaregistry.get_coins(pool)

    # check if pool balances after accounting for decimals is legible.
    # some scam tokens can have weird token properties (e.g. ELONX)
    pool_balances_float = []
    for i in range(len(pool_balances)):

        if coins[i] == brownie.ZERO_ADDRESS:
            break

        pool_balances_float.append(pool_balances[i] / 10 ** coin_decimals[i])

        if (
            coin_decimals[i] == 0
            and brownie.interface.ERC20(metaregistry.get_coins(pool)[0]).decimals() == 0
        ):
            with brownie.reverts():
                metaregistry.get_virtual_price_from_lp_token(lp_token)
            pytest.skip(f"skem token {coins[i]} in pool {pool} with zero decimals")

    # check if pool balances are skewed: vprice calc will bork if one of the coin
    # balances is close to zero.
    if (
        max(pool_balances_float) - min(pool_balances_float)
        == pytest.approx(max(pool_balances_float))
        and min(pool_balances_float) < 1
    ):
        with brownie.reverts():
            metaregistry.get_virtual_price_from_lp_token(lp_token)

        pytest.skip(
            f"skewed pool: {pool} as num coins (decimals divided) at index {i} is "
            f"{pool_balances[i] / 10 ** coin_decimals[i]}"
        )

    # virtual price from underlying child registries:
    if registry_id in [
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ]:
        actual_output = registry.get_virtual_price_from_lp_token(lp_token)
    else:  # factories dont have virtual price getters
        actual_output = curve_pool(pool).get_virtual_price()

    # virtual price from metaregistry:
    metaregistry_output = metaregistry.get_virtual_price_from_lp_token(lp_token)
    assert actual_output == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_decimals(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    # metaregistry underlying decimals:
    metaregistry_output = metaregistry.get_underlying_decimals(pool)
    assert metaregistry_output[1] != 0  # there has to be a second coin!

    # get actual decimals: first try registry
    # todo: include CryptoRegistryHandler when CryptoRegistry gets updated
    pool_is_metapool = metaregistry.is_meta(pool)
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
        underlying_coins = metaregistry.get_underlying_coins(pool)
        actual_output = []
        for i in range(len(underlying_coins)):
            if underlying_coins[i] == brownie.ZERO_ADDRESS:
                actual_output.append(0)
            else:
                actual_output.append(brownie.interface.ERC20(underlying_coins[i]).decimals())

        assert actual_output[2] != 0  # there has to be a third coin!
    else:
        actual_output = list(registry.get_decimals(pool))

    # pad zeros to match metaregistry_output length
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))

    assert metaregistry_output == tuple(actual_output)


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    metaregistry_output = metaregistry.get_coins(pool)

    actual_output = list(registry.get_coins(pool))
    actual_output += [brownie.ZERO_ADDRESS] * (len(metaregistry_output) - len(actual_output))

    assert tuple(actual_output) == metaregistry_output


def _get_underlying_coins_from_registry(registry_id, registry, base_pool_registry_updated, pool):

    if registry_id in [
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ]:

        return registry.get_underlying_coins(pool)

    else:

        # crypto factory does not have underlying coins methods,
        # so we need to find it out the long way:
        coins = registry.get_coins(pool)
        underlying_coins = [brownie.ZERO_ADDRESS] * MAX_COINS

        for idx, coin in enumerate(coins):

            base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)

            if base_pool != brownie.ZERO_ADDRESS:

                basepool_coins = base_pool_registry_updated.get_coins(base_pool)

                for bp_coin in basepool_coins:

                    if bp_coin == brownie.ZERO_ADDRESS:
                        break

                    underlying_coins[idx] = bp_coin
                    idx += 1

                break

            else:

                underlying_coins[idx] = coin

        return underlying_coins


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_coins(
    metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_underlying_coins(pool)

    if metaregistry.is_meta(pool):
        actual_output = _get_underlying_coins_from_registry(
            registry_id, registry, base_pool_registry_updated, pool
        )
    else:
        actual_output = registry.get_coins(pool)

    for idx, registry_value in enumerate(actual_output):
        assert registry_value == metaregistry_output[idx]


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_balances(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_balances(pool)
    actual_output = list(registry.get_balances(pool))
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))
    assert tuple(actual_output) == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_balances(
    metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if sum(metaregistry.get_balances(pool)) == 0:
        pytest.skip(f"Empty pool: {pool}")

    elif registry_id in [
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ] and metaregistry.is_meta(pool):

        # the metaregistry uses get_balances if the pool is not a metapool:
        actual_output = registry.get_underlying_balances(pool)

    elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX and metaregistry.is_meta(pool):
        # crypto factory does not have get_underlying_balances method.
        v2_pool = curve_pool_v2(pool)

        coins = registry.get_coins(pool)
        pool_balances = [0] * MAX_COINS

        for idx, coin in enumerate(coins):
            base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)
            if base_pool != brownie.ZERO_ADDRESS:
                basepool_coins = base_pool_registry_updated.get_coins(base_pool)
                basepool_contract = brownie.Contract(base_pool)
                basepool_lp_token_balance = v2_pool.balances(idx)
                lp_token_supply = brownie.interfaces.ERC20(coin).totalSupply()
                ratio_in_pool = basepool_lp_token_balance / lp_token_supply
                for idy, coin in enumerate(basepool_coins):
                    if coin == brownie.ZERO_ADDRESS:
                        break
                    pool_balances[idx] = basepool_contract.balances(idy) * ratio_in_pool

                break
            pool_balances[idx] = v2_pool.balances(idx)
        actual_output = pool_balances

    else:

        actual_output = registry.get_balances(pool)

    metaregistry_output = metaregistry.get_underlying_balances(pool)

    if metaregistry.is_meta(pool):
        assert metaregistry_output[2] > 0  # it must have a third coin
    else:
        assert metaregistry_output[1] > 0  # it must have a second coin

    for idx, registry_value in enumerate(actual_output):
        if metaregistry_output[idx] - registry_value != 0:
            assert registry_value == pytest.approx(metaregistry_output[idx])
        else:
            assert True


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_n_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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
def test_get_n_underlying_coins(
    metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    metaregistry_output = metaregistry.get_n_underlying_coins(pool)

    coins = registry.get_coins(pool)
    num_coins = 0
    for idx, coin in enumerate(coins):
        if coin == brownie.ZERO_ADDRESS:
            break
        base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)
        if base_pool != brownie.ZERO_ADDRESS:
            basepool_coins = base_pool_registry_updated.get_coins(base_pool)
            num_bp_coins = sum([1 for i in basepool_coins if i != brownie.ZERO_ADDRESS])
            num_coins += num_bp_coins
        else:
            num_coins += 1

    assert num_coins == metaregistry_output


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_coin_indices(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)
    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    # curve v2 pools need to calculates self.xp() for getting self.fee(), and that is not
    # possible if the pool is empty.
    if (
        registry_id
        in [METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX, METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX]
        and sum(metaregistry.get_balances(pool)) == 0
    ):
        with brownie.reverts():
            curve_pool_v2(pool).fee()
        pytest.skip(
            f"crypto factory pool {pool} is empty and factory pools tend to "
            "revert for `fee()` since calcs are needed and they can't be done "
            "for an empty pool"
        )

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    # get_fees
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

    metaregistry_output = metaregistry.get_fees(pool)
    for j, output in enumerate(actual_output):
        assert output == metaregistry_output[j]


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_name(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

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


def _is_dao_onboarded_gauge(_gauge):

    try:
        gauge_controller().gauge_types(_gauge)
    except brownie.exceptions.VirtualMachineError:
        return False

    if liquidity_gauge(_gauge).is_killed():
        return False

    return True


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_gauges(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    if registry_id in [
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ]:

        actual_output = registry.get_gauges(pool)

    else:  # for factory pools, some checks need to be done

        gauge = registry.get_gauge(pool)

        # we check if the gauge is dao onboarded, else
        # gauge_controller().gauge_types(gauge) will revert
        # as gauge type is zero. This slows down tests significantly
        if _is_dao_onboarded_gauge(gauge):
            actual_output = (
                [gauge] + [brownie.ZERO_ADDRESS] * 9,
                [gauge_controller().gauge_types(gauge)] + [0] * 9,
            )
        else:
            actual_output = (
                [gauge] + [brownie.ZERO_ADDRESS] * 9,
                [0] * 10,
            )

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
