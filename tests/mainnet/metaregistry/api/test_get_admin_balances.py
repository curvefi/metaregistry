import pytest


def pre_test_checks(metaregistry, pool, project):

    if sum(metaregistry.get_balances(pool)) == 0:
        pytest.skip("empty pool: skipping")

    if project.ERC20.at(metaregistry.get_lp_token(pool)).totalSupply() == 0:
        pytest.skip("lp token supply is zero")


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry, project
):

    pre_test_checks(populated_metaregistry, stable_registry_pool, project)

    actual_output = stable_registry.get_admin_balances(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_admin_balances(stable_registry_pool)
    for i, output in enumerate(actual_output):
        assert output == metaregistry_output[i]


def test_stable_factory_pools(
    populated_metaregistry,
    stable_factory_pool,
    project,
    curve_pool,
):

    pre_test_checks(populated_metaregistry, stable_factory_pool, project)

    pool = curve_pool(stable_factory_pool)
    metaregistry_output = populated_metaregistry.get_admin_balances(stable_factory_pool)
    for i in range(populated_metaregistry.get_n_coins(pool)):
        assert pool.admin_balances(i) == metaregistry_output[i]


# ---- crypto pools are treated differently ----


def _get_crypto_pool_admin_fees(populated_metaregistry, pool, fee_receiver, project, alice, chain):

    lp_token = project.ERC20.at(populated_metaregistry.get_lp_token(pool))
    fee_receiver_token_balance_before = lp_token.balanceOf(fee_receiver)

    chain.snapshot()
    pool.claim_admin_fees(sender=alice)

    claimed_lp_token_as_fee = lp_token.balanceOf(fee_receiver) - fee_receiver_token_balance_before
    total_supply_lp_token = lp_token.totalSupply()
    frac_admin_fee = int(claimed_lp_token_as_fee * 10**18 / total_supply_lp_token)

    # get admin balances in individual assets:
    reserves = populated_metaregistry.get_balances(pool)
    admin_balances = [0] * 8
    for i in range(8):
        admin_balances[i] = int(frac_admin_fee * reserves[i] / 10**18)

    chain.restore()
    return admin_balances


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    curve_pool_v2,
    alice,
    chain,
    project,
):

    pre_test_checks(populated_metaregistry, crypto_registry_pool, project)

    pool = curve_pool_v2(crypto_registry_pool)
    fee_receiver = pool.admin_fee_receiver()
    admin_balances = _get_crypto_pool_admin_fees(
        populated_metaregistry, pool, fee_receiver, project, alice, chain
    )

    metaregistry_output = populated_metaregistry.get_admin_balances(pool)
    for i, output in enumerate(admin_balances):
        assert output == pytest.approx(metaregistry_output[i])


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    curve_pool_v2,
    alice,
    chain,
    project,
):

    pre_test_checks(populated_metaregistry, crypto_factory_pool, project)

    pool = curve_pool_v2(crypto_factory_pool)
    fee_receiver = crypto_factory.fee_receiver()
    admin_balances = _get_crypto_pool_admin_fees(
        populated_metaregistry, pool, fee_receiver, project, alice, chain
    )

    metaregistry_output = populated_metaregistry.get_admin_balances(pool)
    for i, output in enumerate(admin_balances):
        assert output == pytest.approx(metaregistry_output[i])
