import ape


def test_new_crypto_factory_pool(metaregistry, crypto_factory, tokens, lp_tokens, alice):
    test_pool_name = "test_pool"

    assert (
        metaregistry.find_pool_for_coins(tokens["dai"], lp_tokens["cvxFXSFXS-f"], 0)
        == ape.utils.ZERO_ADDRESS
    )

    crypto_factory.deploy_pool(
        test_pool_name,
        test_pool_name,
        [tokens["dai"], lp_tokens["cvxFXSFXS-f"]],
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
        sender=alice,
    )
    new_pool = crypto_factory.pool_list(crypto_factory.pool_count() - 1)
    lp_token = crypto_factory.get_token(new_pool)

    assert (
        metaregistry.get_coins(new_pool)
        == [tokens["dai"], lp_tokens["cvxFXSFXS-f"]] + [ape.utils.ZERO_ADDRESS] * 6
    )
    assert test_pool_name in metaregistry.get_pool_name(new_pool)
    assert metaregistry.get_pool_from_lp_token(lp_token) == new_pool
    assert metaregistry.find_pool_for_coins(tokens["dai"], lp_tokens["cvxFXSFXS-f"], 0) == new_pool


def test_new_stable_factory_pool(metaregistry, stable_factory, lp_tokens, alice):
    test_pool_name = "test_pool"

    assert (
        metaregistry.find_pool_for_coins(lp_tokens["bveCVX-CVX-f"], lp_tokens["cvxFXSFXS-f"], 0)
        == ape.utils.ZERO_ADDRESS
    )

    stable_factory.deploy_plain_pool(
        test_pool_name,
        test_pool_name,
        [
            lp_tokens["bveCVX-CVX-f"],
            lp_tokens["cvxFXSFXS-f"],
            ape.utils.ZERO_ADDRESS,
            ape.utils.ZERO_ADDRESS,
        ],
        10000,
        4000000,
        0,
        0,
        sender=alice,
    )

    new_pool = stable_factory.pool_list(stable_factory.pool_count() - 1)
    lp_token = new_pool  # pool == lp_token fot stable_factory

    assert (
        metaregistry.get_coins(new_pool)
        == [lp_tokens["bveCVX-CVX-f"], lp_tokens["cvxFXSFXS-f"]] + [ape.utils.ZERO_ADDRESS] * 6
    )
    assert test_pool_name in metaregistry.get_pool_name(new_pool)
    assert metaregistry.get_pool_from_lp_token(lp_token) == new_pool
    assert (
        metaregistry.find_pool_for_coins(lp_tokens["bveCVX-CVX-f"], lp_tokens["cvxFXSFXS-f"], 0)
        == new_pool
    )
