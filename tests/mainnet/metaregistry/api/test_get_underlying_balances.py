import ape
import pytest


def pre_test_checks(metaregistry, pool):

    if sum(metaregistry.get_balances(pool)) == 0:
        pytest.skip(f"Empty pool: {pool}")


def _test_underlying_balances_getter(metaregistry, pool, registry):

    if metaregistry.is_meta(pool):
        actual_output = registry.get_underlying_balances(pool)

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


def test_stable_registry_pools(populated_metaregistry, stable_registry_pool, stable_registry):
    pre_test_checks(populated_metaregistry, stable_registry_pool)
    _test_underlying_balances_getter(populated_metaregistry, stable_registry_pool, stable_registry)


def test_stable_factory_pools(populated_metaregistry, stable_factory_pool, stable_factory):
    pre_test_checks(populated_metaregistry, stable_factory_pool)
    _test_underlying_balances_getter(populated_metaregistry, stable_factory_pool, stable_factory)


def test_crypto_registry_pools(populated_metaregistry, crypto_registry_pool, crypto_registry):
    pre_test_checks(populated_metaregistry, crypto_registry_pool)
    _test_underlying_balances_getter(populated_metaregistry, crypto_registry_pool, crypto_registry)


def test_crypto_factory_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    crypto_factory_pool,
    crypto_factory,
    curve_pool_v2,
    max_coins,
):

    pre_test_checks(populated_metaregistry, crypto_factory_pool)

    v2_pool = curve_pool_v2(crypto_factory_pool)
    coins = crypto_factory.get_coins(crypto_factory_pool)
    pool_balances = [0] * max_coins

    for idx, coin in enumerate(coins):
        base_pool = populated_base_pool_registry.get_base_pool_for_lp_token(coin)
        if base_pool != ape.utils.ZERO_ADDRESS:
            basepool_coins = populated_base_pool_registry.get_coins(base_pool)
            basepool_contract = ape.Contract(base_pool)
            basepool_lp_token_balance = v2_pool.balances(idx)
            lp_token_supply = ape.interfaces.ERC20(coin).totalSupply()
            ratio_in_pool = basepool_lp_token_balance / lp_token_supply
            for idy, coin in enumerate(basepool_coins):
                if coin == ape.utils.ZERO_ADDRESS:
                    break
                pool_balances[idx] = basepool_contract.balances(idy) * ratio_in_pool

            break
        pool_balances[idx] = v2_pool.balances(idx)

    if populated_metaregistry.is_meta(pool):
        assert populated_metaregistry[2] > 0  # it must have a third coin
    else:
        assert populated_metaregistry[1] > 0  # it must have a second coin

    for idx, registry_value in enumerate(pool_balances):
        if populated_metaregistry[idx] - registry_value != 0:
            assert registry_value == pytest.approx(populated_metaregistry[idx])
        else:
            assert True
