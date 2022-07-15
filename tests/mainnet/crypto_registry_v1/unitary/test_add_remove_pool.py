import brownie

from tests.utils.constants import (
    CRV3CRYPTO_MAINNET,
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
    assert crypto_registry_v1.coin_count() == 3
    assert crypto_registry_v1.get_coin_swap_complement(USDT, 0) == WBTC
    assert crypto_registry_v1.get_coin_swap_complement(USDT, 1) == WETH
    assert crypto_registry_v1.get_coin_swap_complement(WBTC, 0) == USDT
    assert crypto_registry_v1.get_coin_swap_complement(WBTC, 1) == WETH
    assert crypto_registry_v1.get_coin_swap_complement(WETH, 0) == USDT
    assert crypto_registry_v1.get_coin_swap_complement(WETH, 1) == WBTC

    for coin in [USDT, WBTC, WETH]:
        assert crypto_registry_v1.get_coin_swap_count(coin) == 2

    assert crypto_registry_v1.get_coin_indices(TRICRYPTO2_MAINNET, USDT, WBTC) == [0, 1, False]
    assert crypto_registry_v1.get_coin_indices(TRICRYPTO2_MAINNET, WBTC, WETH) == [1, 2, False]
    assert crypto_registry_v1.find_pool_for_coins(USDT, WBTC, 0) == TRICRYPTO2_MAINNET


def test_remove_pool(crypto_registry_updated, owner):
    pass
