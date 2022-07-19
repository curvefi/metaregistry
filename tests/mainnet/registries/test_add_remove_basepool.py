import brownie

from tests.utils.constants import (
    BTC_BASEPOOL_LP_TOKEN_MAINNET,
    BTC_BASEPOOL_MAINNET,
    DAI,
    RENBTC,
    SBTC,
    TRIPOOL,
    TRIPOOL_LPTOKEN,
    USDC,
    USDT,
    WBTC,
)


def test_revert_unauthorised_add_base_pool(base_pool_registry, unauthorised_account):

    with brownie.reverts():
        base_pool_registry.add_base_pool(
            TRIPOOL,
            TRIPOOL_LPTOKEN,
            3,
            False,
            False,
            False,
            {"from": unauthorised_account},
        )


def test_add_basepool(base_pool_registry, owner):

    base_pool_count = base_pool_registry.base_pool_count()

    base_pool_registry.add_base_pool(
        TRIPOOL,
        TRIPOOL_LPTOKEN,
        3,
        False,
        False,
        False,
        {"from": owner},
    )

    assert base_pool_registry.base_pool_count() == base_pool_count + 1
    assert base_pool_registry.get_base_pool_for_lp_token(TRIPOOL_LPTOKEN) == TRIPOOL
    assert base_pool_registry.get_lp_token(TRIPOOL) == TRIPOOL_LPTOKEN
    assert not base_pool_registry.is_legacy(TRIPOOL)
    assert not base_pool_registry.is_v2(TRIPOOL)
    assert not base_pool_registry.is_lending(TRIPOOL)

    base_pool_coins = base_pool_registry.get_coins(TRIPOOL)
    assert base_pool_coins[0] == DAI
    assert base_pool_coins[1] == USDC
    assert base_pool_coins[2] == USDT
    assert base_pool_coins[3] == brownie.ZERO_ADDRESS
    assert base_pool_registry.get_n_coins(TRIPOOL) == 3

    base_pool_coin_decimals = base_pool_registry.get_decimals(TRIPOOL)
    assert base_pool_coin_decimals[0] == 18
    assert base_pool_coin_decimals[1] == 6
    assert base_pool_coin_decimals[2] == 6


def test_add_basepool_with_legacy_abi(base_pool_registry, owner):

    base_pool_registry.add_base_pool(
        BTC_BASEPOOL_MAINNET,
        BTC_BASEPOOL_LP_TOKEN_MAINNET,
        3,
        True,
        False,
        False,
        {"from": owner},
    )

    assert base_pool_registry.is_legacy(BTC_BASEPOOL_MAINNET)

    base_pool_coins = base_pool_registry.get_coins(BTC_BASEPOOL_MAINNET)
    assert base_pool_coins[0] == RENBTC
    assert base_pool_coins[1] == WBTC
    assert base_pool_coins[2] == SBTC
    assert base_pool_coins[3] == brownie.ZERO_ADDRESS
    assert base_pool_registry.get_n_coins(BTC_BASEPOOL_MAINNET) == 3


def test_revert_unauthorised_remove_base_pool(base_pool_registry_updated, unauthorised_account):

    assert base_pool_registry_updated.get_lp_token(TRIPOOL) != brownie.ZERO_ADDRESS
    with brownie.reverts():
        base_pool_registry_updated.remove_base_pool(TRIPOOL, {"from": unauthorised_account})


def test_remove_base_pool(base_pool_registry_updated, owner):

    base_pool_count = base_pool_registry_updated.base_pool_count()
    last_base_pool = base_pool_registry_updated.base_pool_list(base_pool_count - 1)
    base_pool_location = base_pool_registry_updated.get_location(TRIPOOL)
    base_pool_registry_updated.remove_base_pool(TRIPOOL, {"from": owner})

    assert base_pool_registry_updated.base_pool_count() == base_pool_count - 1
    assert base_pool_registry_updated.get_lp_token(TRIPOOL) == brownie.ZERO_ADDRESS
    assert (
        base_pool_registry_updated.get_base_pool_for_lp_token(TRIPOOL_LPTOKEN)
        == brownie.ZERO_ADDRESS
    )
    assert base_pool_registry_updated.base_pool_list(base_pool_location) == last_base_pool
    assert base_pool_registry_updated.get_n_coins(TRIPOOL) == 0
