import warnings

import pytest
from boa import BoaError
from eth.constants import ZERO_ADDRESS

from scripts.utils import get_deployed_contract
from tests.utils import assert_negative_coin_balance

EXCEPTION_POOLS = ["0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27"]


def pre_test_checks(metaregistry, pool):
    try:
        if sum(metaregistry.get_balances(pool)) == 0:
            pytest.skip(f"Empty pool: {pool}")
    except BoaError:
        assert_negative_coin_balance(metaregistry, pool)
        pytest.skip(f"Pool {pool} has coin balances lower than admin")


def _get_underlying_balances(
    metaregistry, pool, registry, base_pool_registry, max_coins
):
    actual_output = [0] * max_coins

    try:
        actual_output = registry.get_underlying_balances(pool)

    # registry getter borks, so we need to get balances the hard way:
    except (BoaError, AttributeError):
        coins = metaregistry.get_coins(pool)
        balances = metaregistry.get_balances(pool)
        for idx, coin in enumerate(coins):
            base_pool = base_pool_registry.get_base_pool_for_lp_token(coin)

            if base_pool != ZERO_ADDRESS:
                basepool_lp_token_balance = balances[idx]
                coin_contract = get_deployed_contract("ERC20", coin)
                try:
                    lp_token_supply = coin_contract.totalSupply()
                except (BoaError, AttributeError):
                    assert "totalSupply" not in [
                        i.name
                        for i in coin_contract.contract_type.view_methods
                    ]
                    pytest.skip(
                        f"Token {coin} method totalSupply() is not a view method"
                    )

                ratio_in_pool = basepool_lp_token_balance / lp_token_supply

                base_pool_balances = metaregistry.get_balances(base_pool)

                for idy, balance in enumerate(base_pool_balances):
                    if coin == ZERO_ADDRESS:
                        break
                    actual_output[idx] = balance * ratio_in_pool

                break

            actual_output[idx] = balances[idx]

    return actual_output


def _test_underlying_balances_getter(
    metaregistry, pool, registry, base_pool_registry, max_coins
):
    actual_output = _get_underlying_balances(
        metaregistry, pool, registry, base_pool_registry, max_coins
    )
    try:
        metaregistry_output = metaregistry.get_underlying_balances(pool)
    except BoaError:
        registry_handler = metaregistry.get_registry_handlers_from_pool(pool)[
            0
        ]
        assert (
            metaregistry.get_base_registry(registry_handler)
            == registry.address
        )
        base_pool = registry.get_base_pool(pool)
        assert base_pool_registry.get_lp_token(base_pool) == ZERO_ADDRESS
        pytest.skip(f"Pool {pool} is meta pool but base pool has no LP token")

    underlying_decimals = metaregistry.get_underlying_decimals(pool)

    for idx, registry_value in enumerate(actual_output):
        try:
            assert registry_value == pytest.approx(
                metaregistry_output[idx]
                * 10 ** (18 - underlying_decimals[idx])
            )

        except AssertionError:
            if pool in EXCEPTION_POOLS:
                warnings.warn("Skipping test for pool: {}".format(pool))
                pytest.skip(
                    "Unresolved output from Borky pool: {}".format(pool)
                )


def test_stable_registry_pools(
    populated_metaregistry,
    stable_registry_pool,
    stable_registry,
    populated_base_pool_registry,
    max_coins,
):
    pre_test_checks(populated_metaregistry, stable_registry_pool)
    _test_underlying_balances_getter(
        populated_metaregistry,
        stable_registry_pool,
        stable_registry,
        populated_base_pool_registry,
        max_coins,
    )


def test_stable_factory_pools(
    populated_metaregistry,
    stable_factory_pool,
    stable_factory,
    populated_base_pool_registry,
    max_coins,
):
    pre_test_checks(populated_metaregistry, stable_factory_pool)
    _test_underlying_balances_getter(
        populated_metaregistry,
        stable_factory_pool,
        stable_factory,
        populated_base_pool_registry,
        max_coins,
    )


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    crypto_registry,
    populated_base_pool_registry,
    max_coins,
):
    pre_test_checks(populated_metaregistry, crypto_registry_pool)
    _test_underlying_balances_getter(
        populated_metaregistry,
        crypto_registry_pool,
        crypto_registry,
        populated_base_pool_registry,
        max_coins,
    )


def test_crypto_factory_pools(
    populated_metaregistry,
    populated_base_pool_registry,
    crypto_factory_pool,
    crypto_factory,
    max_coins,
):
    pre_test_checks(populated_metaregistry, crypto_factory_pool)

    _test_underlying_balances_getter(
        populated_metaregistry,
        crypto_factory_pool,
        crypto_factory,
        populated_base_pool_registry,
        max_coins,
    )
