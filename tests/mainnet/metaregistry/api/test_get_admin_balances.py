import boa
import pytest
from boa import BoaError
from eth.codecs.abi.exceptions import DecodeError

from tests.utils import get_deployed_token_contract


def pre_test_checks(metaregistry, pool):
    if sum(metaregistry.get_balances(pool)) == 0:
        pytest.skip("empty pool: skipping")

    try:
        contract = get_deployed_token_contract(metaregistry.get_lp_token(pool))
        if contract.totalSupply() == 0:
            pytest.skip("LP token supply is zero")
    except (BoaError, DecodeError) as err:  # TODO: Document why this happens
        pytest.skip(
            f"{type(err).__name__} for token {metaregistry.get_lp_token(pool)}: "
            f"Skipping because of {err.msg}"
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
