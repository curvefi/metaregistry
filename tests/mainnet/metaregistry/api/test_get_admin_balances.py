import boa
import pytest
from boa import BoaError
from eth.codecs.abi.exceptions import DecodeError as ABIDecodeError

from tests.utils import ZERO_ADDRESS, get_deployed_token_contract


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
        contract = get_deployed_token_contract(lp_token)
        if contract.totalSupply() == 0:
            return pytest.skip("LP token supply is zero")
    except ABIDecodeError as e:
        assert e.msg == "Value length is not the expected size of 32 bytes"
        assert len(e.value) == 4096
        return pytest.skip(
            f"Pool {pool} cannot decode the total supply of its LP token {lp_token}"
        )


def assert_negative_coin_balance(metaregistry, pool):
    """
    The implementation of get_balance calculates (balance - admin_balance) but sometimes the coin
    balance might be lower than the admin balance, resulting in an uint underflow.
    """
    coins = [
        coin for coin in metaregistry.get_coins(pool) if coin != ZERO_ADDRESS
    ]
    coin_balances = [
        get_deployed_token_contract(coin).balanceOf(pool) for coin in coins
    ]
    admin_balances = metaregistry.get_admin_balances(pool)
    assert any(
        coin_balance < admin_balance
        for coin_balance, admin_balance in zip(coin_balances, admin_balances)
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
    metaregistry_output = populated_metaregistry.get_admin_balances(
        stable_factory_pool
    )
    for i in range(populated_metaregistry.get_n_coins(pool)):
        assert pool.admin_balances(i) == metaregistry_output[i]


# ---- crypto pools are treated differently ----


def _get_crypto_pool_admin_fees(
    populated_metaregistry, pool, fee_receiver, alice_address
):
    lp_token = get_deployed_token_contract(
        populated_metaregistry.get_lp_token(pool)
    )
    fee_receiver_token_balance_before = lp_token.balanceOf(fee_receiver)

    with boa.env.anchor():
        pool.claim_admin_fees(sender=alice_address)

        claimed_lp_token_as_fee = (
            lp_token.balanceOf(fee_receiver)
            - fee_receiver_token_balance_before
        )
        total_supply_lp_token = lp_token.totalSupply()
        frac_admin_fee = int(
            claimed_lp_token_as_fee * 10**18 / total_supply_lp_token
        )

        # get admin balances in individual assets:
        reserves = populated_metaregistry.get_balances(pool)
        admin_balances = [0] * 8
        for i in range(8):
            admin_balances[i] = int(frac_admin_fee * reserves[i] / 10**18)

    return admin_balances


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    curve_pool_v2,
    alice_address,
):
    pre_test_checks(populated_metaregistry, crypto_registry_pool)

    pool = curve_pool_v2(crypto_registry_pool)
    fee_receiver = pool.admin_fee_receiver()
    admin_balances = _get_crypto_pool_admin_fees(
        populated_metaregistry,
        pool,
        fee_receiver,
        alice_address,
    )

    metaregistry_output = populated_metaregistry.get_admin_balances(pool)
    for i, output in enumerate(admin_balances):
        assert output == pytest.approx(metaregistry_output[i])


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
        assert output == pytest.approx(metaregistry_output[i])
