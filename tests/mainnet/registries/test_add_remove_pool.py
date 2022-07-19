import brownie

from tests.utils.constants import (
    CRV3CRYPTO_MAINNET,
    MAX_COINS,
    TRICRYPTO2_GAUGE,
    TRICRYPTO2_MAINNET,
    TRICRYPTO2_ZAP,
    USDT,
    WBTC,
    WETH,
)


def test_revert_unauthorised_add_pool(crypto_registry_v1, unauthorised_account):

    with brownie.reverts():
        crypto_registry_v1.add_pool(
            TRICRYPTO2_MAINNET,
            CRV3CRYPTO_MAINNET,
            TRICRYPTO2_GAUGE,
            TRICRYPTO2_ZAP,
            3,
            "tricrypto2",
            brownie.ZERO_ADDRESS,
            False,
            {"from": unauthorised_account},
        )


def test_revert_add_existing_pool(crypto_registry_updated, owner):

    with brownie.reverts():
        crypto_registry_updated.add_pool(
            TRICRYPTO2_MAINNET,
            CRV3CRYPTO_MAINNET,
            TRICRYPTO2_GAUGE,
            TRICRYPTO2_ZAP,
            3,
            "tricrypto2",
            brownie.ZERO_ADDRESS,
            False,
            {"from": owner},
        )


def test_add_pool(crypto_registry_v1, owner):

    pool_count = crypto_registry_v1.pool_count()
    assert pool_count == 0

    crypto_registry_v1.add_pool(
        TRICRYPTO2_MAINNET,
        CRV3CRYPTO_MAINNET,
        TRICRYPTO2_GAUGE,
        TRICRYPTO2_ZAP,
        3,
        "tricrypto2",
        brownie.ZERO_ADDRESS,
        False,
        {"from": owner},
    )

    assert crypto_registry_v1.pool_count() == pool_count + 1
    assert crypto_registry_v1.pool_list(pool_count) == TRICRYPTO2_MAINNET
    assert crypto_registry_v1.get_zap(TRICRYPTO2_MAINNET) == TRICRYPTO2_ZAP
    assert crypto_registry_v1.get_lp_token(TRICRYPTO2_MAINNET) == CRV3CRYPTO_MAINNET
    assert crypto_registry_v1.get_pool_from_lp_token(CRV3CRYPTO_MAINNET) == TRICRYPTO2_MAINNET
    assert crypto_registry_v1.get_base_pool(TRICRYPTO2_MAINNET) == brownie.ZERO_ADDRESS
    assert not crypto_registry_v1.is_meta(TRICRYPTO2_MAINNET)
    assert crypto_registry_v1.get_pool_name(TRICRYPTO2_MAINNET) == "tricrypto2"

    assert crypto_registry_v1.get_n_coins(TRICRYPTO2_MAINNET) == 3
    assert crypto_registry_v1.get_decimals(TRICRYPTO2_MAINNET) == [6, 8, 18, 0, 0, 0, 0, 0]
    assert crypto_registry_v1.get_gauges(TRICRYPTO2_MAINNET)[0][0] == TRICRYPTO2_GAUGE
    assert crypto_registry_v1.get_gauges(TRICRYPTO2_MAINNET)[1][0] == 5  # gauge type is 5
    assert (
        crypto_registry_v1.get_coins(TRICRYPTO2_MAINNET)
        == [USDT, WBTC, WETH] + [brownie.ZERO_ADDRESS] * 5
    )

    # check if coins and underlying coins (if any) are added to the underlying market:
    assert crypto_registry_v1.get_coin_indices(TRICRYPTO2_MAINNET, USDT, WBTC) == [0, 1, False]
    assert crypto_registry_v1.get_coin_indices(TRICRYPTO2_MAINNET, WBTC, WETH) == [1, 2, False]
    assert crypto_registry_v1.find_pool_for_coins(USDT, WBTC, 0) == TRICRYPTO2_MAINNET


def test_revert_unauthorised_remove_pool(crypto_registry_updated, unauthorised_account):

    with brownie.reverts():
        crypto_registry_updated.remove_pool(TRICRYPTO2_MAINNET, {"from": unauthorised_account})


def test_remove_pool(crypto_registry_v1, owner):

    # add pool to be removed:
    crypto_registry_v1.add_pool(
        TRICRYPTO2_MAINNET,
        CRV3CRYPTO_MAINNET,
        TRICRYPTO2_GAUGE,
        TRICRYPTO2_ZAP,
        3,
        "tricrypto2",
        brownie.ZERO_ADDRESS,
        False,
        {"from": owner},
    )

    # add EURSUSDC pool as the last pool, since it has no coins overlapping
    # and is not a metapool:
    crypto_registry_v1.add_pool(
        "0x98a7F18d4E56Cfe84E3D081B40001B3d5bD3eB8B",  # _pool
        "0x3D229E1B4faab62F621eF2F6A610961f7BD7b23B",  # _lp_token
        "0x65CA7Dc5CB661fC58De57B1E1aF404649a27AD35",  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        2,  # _n_coins
        "eursusd",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        False,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    pool_count = crypto_registry_v1.pool_count()
    last_pool = crypto_registry_v1.pool_list(pool_count - 1)

    assert crypto_registry_v1.pool_list(0) == TRICRYPTO2_MAINNET
    crypto_registry_v1.remove_pool(TRICRYPTO2_MAINNET, {"from": owner})

    assert crypto_registry_v1.pool_list(0) == last_pool
    assert crypto_registry_v1.pool_count() == pool_count - 1  # one pool should be gone
    assert crypto_registry_v1.get_zap(TRICRYPTO2_MAINNET) == brownie.ZERO_ADDRESS
    assert crypto_registry_v1.get_lp_token(TRICRYPTO2_MAINNET) == brownie.ZERO_ADDRESS
    assert crypto_registry_v1.get_pool_from_lp_token(CRV3CRYPTO_MAINNET) == brownie.ZERO_ADDRESS
    assert crypto_registry_v1.get_pool_name(TRICRYPTO2_MAINNET) == ""

    assert crypto_registry_v1.get_n_coins(TRICRYPTO2_MAINNET) == 0
    assert crypto_registry_v1.get_decimals(TRICRYPTO2_MAINNET) == [0] * MAX_COINS
    assert crypto_registry_v1.get_gauges(TRICRYPTO2_MAINNET)[0][0] == brownie.ZERO_ADDRESS
    assert crypto_registry_v1.get_gauges(TRICRYPTO2_MAINNET)[1][0] == 0

    assert crypto_registry_v1.get_coins(TRICRYPTO2_MAINNET) == [brownie.ZERO_ADDRESS] * MAX_COINS

    for coin_i in [USDT, WBTC, WETH]:
        for coin_j in [USDT, WBTC, WETH]:

            assert crypto_registry_v1.get_coin_indices(TRICRYPTO2_MAINNET, coin_i, coin_j) == [
                0,
                0,
                False,
            ]
