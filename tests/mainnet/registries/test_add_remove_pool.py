import boa
from eth.constants import ZERO_ADDRESS

from tests.utils import deploy_contract


def test_revert_unauthorised_add_pool(
    crypto_registry, unauthorised_address, crypto_registry_pools
):
    pool_data = crypto_registry_pools["tricrypto2"]

    with boa.reverts():
        crypto_registry.add_pool(
            pool_data["pool"],
            pool_data["lp_token"],
            pool_data["gauge"],
            pool_data["zap"],
            pool_data["num_coins"],
            pool_data["name"],
            pool_data["base_pool"],
            pool_data["has_positive_rebasing_tokens"],
            sender=unauthorised_address,
        )


def test_revert_add_existing_pool(
    crypto_registry, owner, crypto_registry_pools
):
    pool_data = crypto_registry_pools["tricrypto2"]

    with boa.reverts():
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


def test_add_pool(
    crypto_registry_pools,
    populated_base_pool_registry,
    address_provider,
    owner,
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

    pool_data = crypto_registry_pools["tricrypto2"]

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
    assert crypto_registry.pool_list(pool_count) == pool_data["pool"]
    assert crypto_registry.get_zap(pool_data["pool"]) == pool_data["zap"]
    assert (
        crypto_registry.get_lp_token(pool_data["pool"])
        == pool_data["lp_token"]
    )
    assert (
        crypto_registry.get_pool_from_lp_token(pool_data["lp_token"])
        == pool_data["pool"]
    )
    assert crypto_registry.get_base_pool(pool_data["pool"]) == ZERO_ADDRESS
    assert not crypto_registry.is_meta(pool_data["pool"])
    assert crypto_registry.get_pool_name(pool_data["pool"]) == "tricrypto2"

    assert crypto_registry.get_n_coins(pool_data["pool"]) == 3
    assert crypto_registry.get_decimals(pool_data["pool"]) == [
        6,
        8,
        18,
        0,
        0,
        0,
        0,
        0,
    ]
    assert (
        crypto_registry.get_gauges(pool_data["pool"])[0][0]
        == pool_data["gauge"]
    )
    assert (
        crypto_registry.get_gauges(pool_data["pool"])[1][0] == 5
    )  # gauge type is 5
    assert [
        i.lower() for i in crypto_registry.get_coins(pool_data["pool"])
    ] == [
        tokens["usdt"].lower(),
        tokens["wbtc"].lower(),
        tokens["weth"].lower(),
    ] + [
        ZERO_ADDRESS
    ] * 5

    # check if coins and underlying coins (if any) are added to the underlying market:
    assert crypto_registry.get_coin_indices(
        pool_data["pool"], tokens["usdt"], tokens["wbtc"]
    ) == (
        0,
        1,
        False,
    )
    assert crypto_registry.get_coin_indices(
        pool_data["pool"], tokens["wbtc"], tokens["weth"]
    ) == (
        1,
        2,
        False,
    )
    assert (
        crypto_registry.find_pool_for_coins(
            tokens["usdt"], tokens["wbtc"], 0
        ).lower()
        == pool_data["pool"].lower()
    )


def test_revert_unauthorised_remove_pool(
    crypto_registry, unauthorised_address, crypto_registry_pools
):
    with boa.reverts():
        crypto_registry.remove_pool(
            crypto_registry_pools["tricrypto2"]["pool"],
            sender=unauthorised_address,
        )


def test_remove_pool(
    crypto_registry_pools,
    address_provider,
    populated_base_pool_registry,
    owner,
    max_coins,
    tokens,
):
    crypto_registry = deploy_contract(
        "CryptoRegistryV1",
        address_provider,
        populated_base_pool_registry,
        directory="registries",
        sender=owner,
    )

    # add pool to be removed:
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

    # add EURSUSDC pool as the last pool, since it has no coins overlapping
    # and is not a metapool:
    eursusdc = crypto_registry_pools["eursusdc"]

    crypto_registry.add_pool(
        eursusdc["pool"],
        eursusdc["lp_token"],
        eursusdc["gauge"],
        eursusdc["zap"],
        eursusdc["num_coins"],
        eursusdc["name"],
        eursusdc["base_pool"],
        eursusdc["has_positive_rebasing_tokens"],
        sender=owner,
    )

    pool_count = crypto_registry.pool_count()
    last_pool = crypto_registry.pool_list(pool_count - 1)

    assert crypto_registry.pool_list(0).lower() == tricrypto2["pool"].lower()
    crypto_registry.remove_pool(tricrypto2["pool"], sender=owner)

    assert crypto_registry.pool_list(0).lower() == last_pool.lower()
    assert (
        crypto_registry.pool_count() == pool_count - 1
    )  # one pool should be gone
    assert crypto_registry.get_zap(tricrypto2["pool"]) == ZERO_ADDRESS
    assert crypto_registry.get_lp_token(tricrypto2["pool"]) == ZERO_ADDRESS
    assert (
        crypto_registry.get_pool_from_lp_token(tricrypto2["lp_token"])
        == ZERO_ADDRESS
    )
    assert crypto_registry.get_pool_name(tricrypto2["pool"]) == ""

    assert crypto_registry.get_n_coins(tricrypto2["pool"]) == 0
    assert crypto_registry.get_decimals(tricrypto2["pool"]) == [0] * max_coins
    assert crypto_registry.get_gauges(tricrypto2["pool"])[0][0] == ZERO_ADDRESS
    assert crypto_registry.get_gauges(tricrypto2["pool"])[1][0] == 0

    assert (
        crypto_registry.get_coins(tricrypto2["pool"])
        == [ZERO_ADDRESS] * max_coins
    )

    for coin_i in [tokens["usdt"], tokens["wbtc"], tokens["weth"]]:
        for coin_j in [tokens["usdt"], tokens["wbtc"], tokens["weth"]]:
            assert crypto_registry.get_coin_indices(
                tricrypto2["pool"], coin_i, coin_j
            ) == (
                0,
                0,
                False,
            )
