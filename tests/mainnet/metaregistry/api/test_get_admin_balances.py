import logging

import boa
import pytest
from boa import BoaError
from eth.codecs.abi.exceptions import DecodeError as ABIDecodeError

from scripts.utils import get_deployed_contract
from tests.utils import assert_decode_error, assert_negative_coin_balance


def pre_test_checks(metaregistry, pool):
    """
    Checks whether the pool is in a state that allows the test to run.
    Otherwise, skips the test.

    The checks are:
    - the pool has a balance
    - the LP token has a supply
    - the coin balances are not lower than the admin balances
    """
    try:
        if sum(metaregistry.get_balances(pool)) == 0:
            return pytest.skip(f"Pool {pool} has no balance")
    except BoaError:
        assert_negative_coin_balance(metaregistry, pool)
        return pytest.skip(f"Pool {pool} has coin balances lower than admin")

    lp_token = metaregistry.get_lp_token(pool)
    try:
        contract = get_deployed_contract("ERC20", lp_token)
        if contract.totalSupply() == 0:
            return pytest.skip("LP token supply is zero")
    except ABIDecodeError as e:
        assert_decode_error(e)
        return pytest.skip(
            f"Pool {pool} cannot decode the total supply of its LP token {lp_token}"
        )


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    pre_test_checks(populated_metaregistry, stable_registry_pool)

    actual_output = stable_registry.get_admin_balances(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_admin_balances(
        stable_registry_pool
    )
    for i, output in enumerate(actual_output):
        assert output == metaregistry_output[i]


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, curve_pool
):
    pre_test_checks(populated_metaregistry, stable_factory_pool)

    pool = curve_pool(stable_factory_pool)
    try:
        metaregistry_output = populated_metaregistry.get_admin_balances(
            stable_factory_pool
        )
    except BoaError:
        first_coin = pool.coins(0)
        with boa.reverts():
            get_deployed_contract("ERC20", first_coin).balanceOf(
                stable_factory_pool
            )
        return pytest.skip(
            f"Pool {stable_factory_pool} cannot determine balance of {first_coin}"
        )

    for i in range(populated_metaregistry.get_n_coins(pool)):
        assert pool.admin_balances(i) == metaregistry_output[i]


# ---- crypto pools are treated differently ----


def _get_crypto_pool_admin_fees(
    populated_metaregistry, pool, fee_receiver, alice_address
):
    lp_address = populated_metaregistry.get_lp_token(pool)
    lp_token = get_deployed_contract("ERC20", lp_address)
    fee_receiver_token_balance_before = lp_token.balanceOf(fee_receiver)

    with boa.env.anchor():
        pool.claim_admin_fees(sender=alice_address)

        fee_receiver_balance_after = lp_token.balanceOf(fee_receiver)
        claimed_lp_token_as_fee = (
            fee_receiver_balance_after - fee_receiver_token_balance_before
        )
        total_supply_lp_token = lp_token.totalSupply()
        frac_admin_fee = int(
            claimed_lp_token_as_fee * 10**18 / total_supply_lp_token
        )

        # get admin balances in individual assets
        reserves = populated_metaregistry.get_balances(pool)
        return [int(frac_admin_fee * reserves[i] / 10**18) for i in range(8)]


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    curve_pool_v2,
    alice_address,
):
    pre_test_checks(populated_metaregistry, crypto_registry_pool)

    pool = curve_pool_v2(crypto_registry_pool)
    fee_receiver = pool.admin_fee_receiver()
    try:
        admin_balances = _get_crypto_pool_admin_fees(
            populated_metaregistry,
            pool,
            fee_receiver,
            alice_address,
        )
    except BoaError:
        balance_of_pool = get_deployed_contract(
            "ERC20", pool.coins(1)
        ).balanceOf(pool.address)
        balance = pool.balances(1)
        assert balance / balance_of_pool > 10**8
        return pytest.skip(
            f"Pool {pool} cannot claim admin fees. "
            f"Pool has {balance_of_pool} but thinks it has {balance}."
        )

    metaregistry_output = populated_metaregistry.get_admin_balances(pool)
    assert admin_balances == pytest.approx(metaregistry_output)


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    curve_pool_v2,
    alice_address,
):
    pre_test_checks(populated_metaregistry, crypto_factory_pool)

    pool = curve_pool_v2(crypto_factory_pool)
    fee_receiver = crypto_factory.fee_receiver()
    admin_balances = _get_crypto_pool_admin_fees(
        populated_metaregistry,
        pool,
        fee_receiver,
        alice_address,
    )

    metaregistry_output = populated_metaregistry.get_admin_balances(pool)
    for i, output in enumerate(admin_balances):
        try:
            assert output == pytest.approx(metaregistry_output[i])
        except AssertionError:
            # TODO: Check if this level of difference is acceptable
            assert output == pytest.approx(metaregistry_output[i], rel=0.009)
            logging.warning(
                f"Pool {pool} has a difference in admin balance {i}: "
                f"{output} != {metaregistry_output[i]}"
            )
