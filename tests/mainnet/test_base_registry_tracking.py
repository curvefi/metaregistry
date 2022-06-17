from brownie import ZERO_ADDRESS

from .utils.constants import (
    BVECVX_LPTOKEN,
    CVXFXS_LPTOKEN,
    DAI,
    METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
)


def test_new_crypto_factory_pool(fn_isolation, metaregistry, registries, owner):
    test_pool_name = "test"
    crypto_factory = registries[METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX]
    assert metaregistry.find_pool_for_coins(DAI, CVXFXS_LPTOKEN) == ZERO_ADDRESS
    crypto_factory.deploy_pool(
        test_pool_name,
        test_pool_name,
        [DAI, CVXFXS_LPTOKEN],
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
        {"from": owner},
    )
    new_pool = crypto_factory.pool_list(crypto_factory.pool_count() - 1)
    lp_token = crypto_factory.get_token(new_pool)
    assert metaregistry.get_coins(new_pool) == [DAI, CVXFXS_LPTOKEN] + [ZERO_ADDRESS] * 6
    assert test_pool_name in metaregistry.get_pool_name(new_pool)
    assert metaregistry.get_pool_from_lp_token(lp_token) == new_pool
    assert metaregistry.find_pool_for_coins(DAI, CVXFXS_LPTOKEN) == new_pool


def test_new_stable_factory_pool(fn_isolation, metaregistry, registries, owner):
    test_pool_name = "test2"
    stable_factory = registries[METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX]
    assert metaregistry.find_pool_for_coins(BVECVX_LPTOKEN, CVXFXS_LPTOKEN) == ZERO_ADDRESS
    stable_factory.deploy_plain_pool(
        test_pool_name,
        test_pool_name,
        [BVECVX_LPTOKEN, CVXFXS_LPTOKEN, ZERO_ADDRESS, ZERO_ADDRESS],
        10000,
        4000000,
        0,
        0,
        {"from": owner},
    )
    new_pool = stable_factory.pool_list(stable_factory.pool_count() - 1)
    lp_token = new_pool
    assert metaregistry.get_coins(new_pool) == [BVECVX_LPTOKEN, CVXFXS_LPTOKEN] + [ZERO_ADDRESS] * 6
    assert test_pool_name in metaregistry.get_pool_name(new_pool)
    assert metaregistry.get_pool_from_lp_token(lp_token) == new_pool
    assert metaregistry.find_pool_for_coins(BVECVX_LPTOKEN, CVXFXS_LPTOKEN) == new_pool
