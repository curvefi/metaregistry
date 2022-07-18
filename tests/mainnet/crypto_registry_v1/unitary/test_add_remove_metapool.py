import brownie
from tests.abis import gauge_controller

from tests.utils.constants import (
    # CRV3CRYPTO_MAINNET,
    CRVEURTUSD,
    DAI,
    EURT,
    EURTUSD_GAUGE,
    EURTUSD_MAINNET,
    EURTUSD_ZAP,
    MAX_COINS,
    # TRICRYPTO2_GAUGE,
    # TRICRYPTO2_MAINNET,
    TRICRYPTO2_ZAP,
    TRIPOOL,
    TRIPOOL_LPTOKEN,
    USDC,
    USDT,
    # WBTC,
    # WETH,
)


def test_add_metapool(crypto_registry_v1, owner):

    pool_count = crypto_registry_v1.pool_count()
    assert pool_count == 0

    # add EURT3CRV pool
    crypto_registry_v1.add_pool(
        EURTUSD_MAINNET,  # _pool
        CRVEURTUSD,  # _lp_token
        EURTUSD_GAUGE,  # _gauge
        EURTUSD_ZAP,  # _zap
        2,  # _n_coins
        "eurtusd",  # _name
        TRIPOOL,  # _base_pool
        False,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    assert crypto_registry_v1.pool_count() == pool_count + 1

    assert crypto_registry_v1.pool_list(pool_count) == EURTUSD_MAINNET
    assert crypto_registry_v1.get_zap(EURTUSD_MAINNET) == EURTUSD_ZAP
    assert crypto_registry_v1.get_lp_token(EURTUSD_MAINNET) == CRVEURTUSD
    assert crypto_registry_v1.get_pool_from_lp_token(CRVEURTUSD) == EURTUSD_MAINNET
    assert crypto_registry_v1.get_base_pool(EURTUSD_MAINNET) == TRIPOOL
    assert crypto_registry_v1.is_meta(EURTUSD_MAINNET)
    assert crypto_registry_v1.get_pool_name(EURTUSD_MAINNET) == "eurtusd"

    assert crypto_registry_v1.get_n_coins(EURTUSD_MAINNET) == 2
    assert crypto_registry_v1.get_n_underlying_coins(EURTUSD_MAINNET) == 4
    assert crypto_registry_v1.get_decimals(EURTUSD_MAINNET) == [6, 18] + [0] * 6
    assert crypto_registry_v1.get_underlying_decimals(EURTUSD_MAINNET) == [6, 18, 6, 6] + [0] * 4

    # gauge checks:
    assert crypto_registry_v1.get_gauges(EURTUSD_MAINNET)[0][0] == EURTUSD_GAUGE
    # special check: eurtusd has gauge_type 0 but it should be 5! The following check
    # will pass regardless:
    gauge_type_actual = gauge_controller().gauge_types(EURTUSD_GAUGE)
    assert gauge_type_actual == 0
    # this has no impact since gauge types 0 and 5 are mainnet gauges and have the same
    # gauge weight
    assert crypto_registry_v1.get_gauges(EURTUSD_MAINNET)[1][0] == gauge_type_actual

    # coin checks:
    assert (
        crypto_registry_v1.get_coins(EURTUSD_MAINNET)
        == [EURT, TRIPOOL_LPTOKEN] + [brownie.ZERO_ADDRESS] * 6
    )
    assert (
        crypto_registry_v1.get_underlying_coins(EURTUSD_MAINNET)
        == [EURT, DAI, USDC, USDT] + [brownie.ZERO_ADDRESS] * 4
    )

    assert crypto_registry_v1.get_coin_indices(EURTUSD_MAINNET, EURT, TRIPOOL_LPTOKEN) == [
        0,
        1,
        False,
    ]
    assert crypto_registry_v1.get_coin_indices(EURTUSD_MAINNET, TRIPOOL_LPTOKEN, EURT) == [
        1,
        0,
        False,
    ]

    # for exchange_underlying:
    assert crypto_registry_v1.get_coin_indices(EURTUSD_MAINNET, EURT, DAI) == [0, 1, True]
    assert crypto_registry_v1.get_coin_indices(EURTUSD_MAINNET, EURT, USDC) == [0, 2, True]
    assert crypto_registry_v1.get_coin_indices(EURTUSD_MAINNET, EURT, USDT) == [0, 3, True]
    # the following should revert since we didn't add any basepool lp token <> coin pairs:
    for coin in [DAI, USDC, USDT]:
        with brownie.reverts():
            crypto_registry_v1.get_coin_indices(EURTUSD_MAINNET, TRIPOOL_LPTOKEN, coin)

    # find pool for coins:
    for coin_a in [EURT, TRIPOOL_LPTOKEN, DAI, USDT, USDC]:
        for coin_b in [EURT, TRIPOOL_LPTOKEN, DAI, USDC, USDT]:

            # if both coins are the same, then it should return ZERO_ADDRESS:
            if coin_a == coin_b:
                assert (
                    crypto_registry_v1.find_pool_for_coins(coin_a, coin_b, 0)
                    == brownie.ZERO_ADDRESS
                )

            # if basepool lp token <> underlying, then it should return ZERO_ADDRESS:
            elif TRIPOOL_LPTOKEN in [coin_a, coin_b] and not set([DAI, USDC, USDT]).isdisjoint(
                [coin_a, coin_b]
            ):
                crypto_registry_v1.find_pool_for_coins(coin_a, coin_b, 0) == brownie.ZERO_ADDRESS

            elif not set([DAI, USDC, USDT]).isdisjoint([coin_a, coin_b]):
                crypto_registry_v1.find_pool_for_coins(coin_a, coin_b, 0) == brownie.ZERO_ADDRESS

            # everything else should go to EURTUSD pool:
            else:
                assert crypto_registry_v1.find_pool_for_coins(coin_a, coin_b, 0) == EURTUSD_MAINNET


def test_remove_metapool(crypto_registry_v1, owner):

    pass
