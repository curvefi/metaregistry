import boa
from eth.constants import ZERO_ADDRESS

from tests.utils import deploy_contract


def test_add_metapool(
    owner,
    gauge_controller,
    address_provider,
    populated_base_pool_registry,
    crypto_registry_pools,
    base_pools,
    tokens,
):
    crypto_registry = deploy_contract(
        "CryptoRegistryV1",
        address_provider,
        populated_base_pool_registry,
        directory="registries",
        sender=owner,
    )

    pool_count = crypto_registry.pool_count()
    assert pool_count == 0

    pool_data = crypto_registry_pools["eurt3crv"]

    crypto_registry.add_pool(
        pool_data["pool"],
        pool_data["lp_token"],
        pool_data["gauge"],
        pool_data["zap"],
        pool_data["num_coins"],
        pool_data["name"],
        pool_data["base_pool"],
        pool_data["has_positive_rebasing_tokens"],
        sender=owner,
    )

    assert crypto_registry.pool_count() == pool_count + 1

    assert (
        crypto_registry.pool_list(pool_count).lower()
        == pool_data["pool"].lower()
    )
    assert (
        crypto_registry.get_zap(pool_data["pool"]).lower()
        == pool_data["zap"].lower()
    )
    assert (
        crypto_registry.get_lp_token(pool_data["pool"]).lower()
        == pool_data["lp_token"].lower()
    )
    assert (
        crypto_registry.get_pool_from_lp_token(pool_data["lp_token"]).lower()
        == pool_data["pool"].lower()
    )
    assert (
        crypto_registry.get_base_pool(pool_data["pool"]).lower()
        == base_pools["tripool"]["pool"].lower()
    )
    assert (
        crypto_registry.get_pool_name(pool_data["pool"]).lower()
        == "eurtusd".lower()
    )

    assert crypto_registry.is_meta(pool_data["pool"])
    assert crypto_registry.get_n_coins(pool_data["pool"]) == 2
    assert crypto_registry.get_n_underlying_coins(pool_data["pool"]) == 4
    assert crypto_registry.get_decimals(pool_data["pool"]) == [6, 18] + [0] * 6
    assert (
        crypto_registry.get_underlying_decimals(pool_data["pool"])
        == [6, 18, 6, 6] + [0] * 4
    )

    # gauge checks:
    assert (
        crypto_registry.get_gauges(pool_data["pool"])[0][0].lower()
        == pool_data["gauge"].lower()
    )
    # special check: eurtusd has gauge_type 0 but it should be 5! The following check
    # will pass regardless:
    gauge_type_actual = gauge_controller.gauge_types(pool_data["gauge"])
    assert gauge_type_actual == 0
    # this has no impact since gauge types 0 and 5 are mainnet gauges and have the same
    # gauge weight
    assert (
        crypto_registry.get_gauges(pool_data["pool"])[1][0]
        == gauge_type_actual
    )

    # coin checks:
    assert [
        i.lower() for i in crypto_registry.get_coins(pool_data["pool"])
    ] == [
        tokens["eurt"].lower(),
        base_pools["tripool"]["lp_token"].lower(),
    ] + [
        ZERO_ADDRESS
    ] * 6
    assert [
        i.lower()
        for i in crypto_registry.get_underlying_coins(pool_data["pool"])
    ] == [
        tokens["eurt"].lower(),
        tokens["dai"].lower(),
        tokens["usdc"].lower(),
        tokens["usdt"].lower(),
    ] + [
        ZERO_ADDRESS
    ] * 4

    assert crypto_registry.get_coin_indices(
        pool_data["pool"], tokens["eurt"], base_pools["tripool"]["lp_token"]
    ) == (
        0,
        1,
        False,
    )
    assert crypto_registry.get_coin_indices(
        pool_data["pool"], base_pools["tripool"]["lp_token"], tokens["eurt"]
    ) == (
        1,
        0,
        False,
    )

    # for exchange_underlying:
    assert crypto_registry.get_coin_indices(
        pool_data["pool"], tokens["eurt"], tokens["dai"]
    ) == (
        0,
        1,
        True,
    )
    assert crypto_registry.get_coin_indices(
        pool_data["pool"], tokens["eurt"], tokens["usdc"]
    ) == (
        0,
        2,
        True,
    )
    assert crypto_registry.get_coin_indices(
        pool_data["pool"], tokens["eurt"], tokens["usdt"]
    ) == (
        0,
        3,
        True,
    )
    # the following should revert since we didn't add any basepool lp token <> coin pairs:
    for coin in [tokens["dai"], tokens["usdc"], tokens["usdt"]]:
        with boa.reverts():
            crypto_registry.get_coin_indices(
                pool_data["pool"], base_pools["tripool"]["lp_token"], coin
            )

    # find pool for coins:
    coins = [
        tokens["eurt"],
        base_pools["tripool"]["lp_token"],
        tokens["dai"],
        tokens["usdc"],
        tokens["usdt"],
    ]
    for coin_a in coins:
        for coin_b in coins:
            # if both coins are the same, then it should return ZERO_ADDRESS:
            if coin_a == coin_b:
                assert (
                    crypto_registry.find_pool_for_coins(coin_a, coin_b, 0)
                    == ZERO_ADDRESS
                )

            # if basepool lp token <> underlying, then it should return ZERO_ADDRESS:
            elif base_pools["tripool"]["lp_token"] in [
                coin_a,
                coin_b,
            ] and not set(
                [tokens["dai"], tokens["usdc"], tokens["usdt"]]
            ).isdisjoint(
                [coin_a, coin_b]
            ):
                crypto_registry.find_pool_for_coins(
                    coin_a, coin_b, 0
                ) == ZERO_ADDRESS

            elif not set(
                [tokens["dai"], tokens["usdc"], tokens["usdt"]]
            ).isdisjoint([coin_a, coin_b]):
                crypto_registry.find_pool_for_coins(
                    coin_a, coin_b, 0
                ) == ZERO_ADDRESS

            # everything else should go to EURTUSD pool:
            else:
                assert (
                    crypto_registry.find_pool_for_coins(
                        coin_a, coin_b, 0
                    ).lower()
                    == pool_data["pool"].lower()
                )


def test_remove_metapool(
    address_provider,
    populated_base_pool_registry,
    owner,
    crypto_registry_pools,
    max_coins,
    base_pools,
    tokens,
):
    crypto_registry = deploy_contract(
        "CryptoRegistryV1",
        address_provider,
        populated_base_pool_registry,
        directory="registries",
        sender=owner,
    )

    # add EURT3CRV pool
    eurt3crv = crypto_registry_pools["eurt3crv"]
    crypto_registry.add_pool(
        eurt3crv["pool"],
        eurt3crv["lp_token"],
        eurt3crv["gauge"],
        eurt3crv["zap"],
        eurt3crv["num_coins"],
        eurt3crv["name"],
        eurt3crv["base_pool"],
        eurt3crv["has_positive_rebasing_tokens"],
        sender=owner,
    )

    # add tricrypto2 as the last pool:
    tricrypto2 = crypto_registry_pools["tricrypto2"]
    crypto_registry.add_pool(
        tricrypto2["pool"],
        tricrypto2["lp_token"],
        tricrypto2["gauge"],
        tricrypto2["zap"],
        tricrypto2["num_coins"],
        tricrypto2["name"],
        tricrypto2["base_pool"],
        tricrypto2["has_positive_rebasing_tokens"],
        sender=owner,
    )

    pool_count = crypto_registry.pool_count()
    last_pool = crypto_registry.pool_list(pool_count - 1)

    assert crypto_registry.pool_list(0).lower() == eurt3crv["pool"].lower()

    crypto_registry.remove_pool(eurt3crv["pool"], sender=owner)

    assert crypto_registry.pool_list(0).lower() == last_pool.lower()
    assert (
        crypto_registry.pool_count() == pool_count - 1
    )  # one pool should be gone

    assert crypto_registry.get_zap(eurt3crv["pool"]) == ZERO_ADDRESS
    assert crypto_registry.get_lp_token(eurt3crv["pool"]) == ZERO_ADDRESS
    assert (
        crypto_registry.get_pool_from_lp_token(eurt3crv["lp_token"])
        == ZERO_ADDRESS
    )
    assert crypto_registry.get_base_pool(eurt3crv["pool"]) == ZERO_ADDRESS
    assert not crypto_registry.is_meta(eurt3crv["pool"])
    assert crypto_registry.get_pool_name(eurt3crv["pool"]) == ""

    assert crypto_registry.get_n_coins(eurt3crv["pool"]) == 0
    assert crypto_registry.get_n_underlying_coins(eurt3crv["pool"]) == 0
    assert crypto_registry.get_decimals(eurt3crv["pool"]) == [0] * max_coins
    assert crypto_registry.get_underlying_decimals(eurt3crv["pool"]) == [0] * 8

    # gauge checks:
    assert crypto_registry.get_gauges(eurt3crv["pool"])[0][0] == ZERO_ADDRESS
    assert crypto_registry.get_gauges(eurt3crv["pool"])[1][0] == 0

    # coin checks:
    assert crypto_registry.get_coins(eurt3crv["pool"]) == [ZERO_ADDRESS] * 8
    assert (
        crypto_registry.get_underlying_coins(eurt3crv["pool"])
        == [ZERO_ADDRESS] * 8
    )

    coins = [
        tokens["eurt"],
        base_pools["tripool"]["lp_token"],
        tokens["dai"],
        tokens["usdc"],
        tokens["usdt"],
    ]
    # find pool for coins:
    for coin_a in coins:
        for coin_b in coins:
            assert crypto_registry.get_coin_indices(
                eurt3crv["pool"], coin_a, coin_b
            ) == (
                0,
                0,
                False,
            )

            assert (
                crypto_registry.find_pool_for_coins(coin_a, coin_b, 0)
                == ZERO_ADDRESS
            )
