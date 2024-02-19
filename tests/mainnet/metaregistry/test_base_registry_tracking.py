from eth.constants import ZERO_ADDRESS


def test_new_crypto_factory_pool(
    populated_metaregistry, crypto_factory, tokens, lp_tokens, alice_address
):
    metaregistry, test_pool_name = populated_metaregistry, "test_pool"
    dai_token, cvx_token = tokens["dai"], lp_tokens["cvxFXSFXS-f"]

    pool_before = metaregistry.find_pool_for_coins(dai_token, cvx_token, 0)
    assert pool_before == ZERO_ADDRESS

    crypto_factory.deploy_pool(
        test_pool_name,
        test_pool_name,
        [dai_token, cvx_token],
        200000000,
        100000000000000,
        1000000,
        10000000,
        10000000000,
        5000000000000000,
        5500000000000,
        5000000000,
        600,
        994000214704046300,
        sender=alice_address,
    )
    new_pool = crypto_factory.pool_list(crypto_factory.pool_count() - 1)
    lp_token = crypto_factory.get_token(new_pool)

    expected_coins = [dai_token, cvx_token] + [ZERO_ADDRESS] * 6
    assert metaregistry.get_coins(new_pool) == expected_coins
    assert test_pool_name in metaregistry.get_pool_name(new_pool)
    assert metaregistry.get_pool_from_lp_token(lp_token) == new_pool
    pool_after = metaregistry.find_pool_for_coins(dai_token, cvx_token, 0)
    assert pool_after == new_pool


def test_new_stable_factory_pool(
    populated_metaregistry, stable_factory, lp_tokens, alice_address
):
    metaregistry, test_pool_name = populated_metaregistry, "test_pool"
    bve_token, cvx_token = lp_tokens["bveCVX-CVX-f"], lp_tokens["cvxFXSFXS-f"]
    pool_before = metaregistry.find_pool_for_coins(bve_token, cvx_token, 0)
    assert pool_before == ZERO_ADDRESS

    stable_factory.deploy_plain_pool(
        test_pool_name,
        test_pool_name,
        [
            bve_token,
            cvx_token,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        10000,
        4000000,
        0,
        0,
        sender=alice_address,
    )

    new_pool = stable_factory.pool_list(stable_factory.pool_count() - 1)
    lp_token = new_pool  # pool == lp_token fot stable_factory

    expected_coins = [bve_token, cvx_token] + [ZERO_ADDRESS] * 6
    assert metaregistry.get_coins(new_pool) == expected_coins
    assert test_pool_name in metaregistry.get_pool_name(new_pool)
    assert metaregistry.get_pool_from_lp_token(lp_token) == new_pool
    pool_after = metaregistry.find_pool_for_coins(bve_token, cvx_token, 0)
    assert pool_after == new_pool
