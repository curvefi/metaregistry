import boa
from eth.constants import ZERO_ADDRESS

from tests.utils import deploy_contract


def test_revert_unauthorised_add_base_pool(
    owner, unauthorised_address, base_pools
):
    base_pool_registry = deploy_contract(
        "BasePoolRegistry", directory="registries", sender=owner
    )
    base_pool_data = base_pools["tripool"]
    with boa.reverts():
        base_pool_registry.add_base_pool(
            base_pool_data["pool"],
            base_pool_data["lp_token"],
            base_pool_data["num_coins"],
            base_pool_data["is_legacy"],
            base_pool_data["is_lending"],
            base_pool_data["is_v2"],
        )


def test_add_basepool(owner, base_pools, tokens):
    base_pool_registry = deploy_contract(
        "BasePoolRegistry", directory="registries", sender=owner
    )
    base_pool_count = base_pool_registry.base_pool_count()
    base_pool_data = base_pools["tripool"]
    tripool = base_pool_data["pool"]
    tripool_lp_token = base_pool_data["lp_token"]

    base_pool_registry.add_base_pool(
        base_pool_data["pool"],
        base_pool_data["lp_token"],
        base_pool_data["num_coins"],
        base_pool_data["is_legacy"],
        base_pool_data["is_lending"],
        base_pool_data["is_v2"],
        sender=owner,
    )

    assert base_pool_registry.base_pool_count() == base_pool_count + 1
    assert (
        base_pool_registry.get_base_pool_for_lp_token(tripool_lp_token)
        == tripool
    )
    assert base_pool_registry.get_lp_token(tripool) == tripool_lp_token
    assert not base_pool_registry.is_legacy(tripool)
    assert not base_pool_registry.is_v2(tripool)
    assert not base_pool_registry.is_lending(tripool)

    base_pool_coins = base_pool_registry.get_coins(tripool)
    assert base_pool_coins[0].lower() == tokens["dai"].lower()
    assert base_pool_coins[1].lower() == tokens["usdc"].lower()
    assert base_pool_coins[2].lower() == tokens["usdt"].lower()
    assert base_pool_coins[3] == ZERO_ADDRESS
    assert base_pool_registry.get_n_coins(tripool) == 3

    base_pool_coin_decimals = base_pool_registry.get_decimals(tripool)
    assert base_pool_coin_decimals[0] == 18
    assert base_pool_coin_decimals[1] == 6
    assert base_pool_coin_decimals[2] == 6


def test_add_basepool_with_legacy_abi(owner, base_pools, tokens):
    base_pool_registry = deploy_contract(
        "BasePoolRegistry", directory="registries", sender=owner
    )

    base_pool_data = base_pools["sbtc"]
    assert base_pool_data["is_legacy"]

    btc_basepool = base_pool_data["pool"]

    base_pool_registry.add_base_pool(
        base_pool_data["pool"],
        base_pool_data["lp_token"],
        base_pool_data["num_coins"],
        base_pool_data["is_legacy"],
        base_pool_data["is_lending"],
        base_pool_data["is_v2"],
        sender=owner,
    )

    assert base_pool_registry.is_legacy(btc_basepool)

    base_pool_coins = base_pool_registry.get_coins(btc_basepool)
    assert base_pool_coins[0].lower() == tokens["renbtc"].lower()
    assert base_pool_coins[1].lower() == tokens["wbtc"].lower()
    assert base_pool_coins[2].lower() == tokens["sbtc"].lower()
    assert base_pool_coins[3] == ZERO_ADDRESS
    assert base_pool_registry.get_n_coins(btc_basepool) == 3


def test_revert_unauthorised_remove_base_pool(
    populated_base_pool_registry, unauthorised_address, base_pools
):
    tripool_address = base_pools["tripool"]["pool"]

    assert (
        populated_base_pool_registry.get_lp_token(tripool_address)
        != ZERO_ADDRESS
    )
    with boa.reverts():
        populated_base_pool_registry.remove_base_pool(
            tripool_address, sender=unauthorised_address
        )


def test_remove_base_pool(populated_base_pool_registry, owner, base_pools):
    tripool_address = base_pools["tripool"]["pool"]
    tripool_lp_token = base_pools["tripool"]["lp_token"]

    base_pool_count = populated_base_pool_registry.base_pool_count()
    last_base_pool = populated_base_pool_registry.base_pool_list(
        base_pool_count - 1
    )
    base_pool_location = populated_base_pool_registry.get_location(
        tripool_address
    )
    populated_base_pool_registry.remove_base_pool(
        tripool_address, sender=owner
    )

    assert (
        populated_base_pool_registry.base_pool_count() == base_pool_count - 1
    )
    assert (
        populated_base_pool_registry.get_lp_token(tripool_address)
        == ZERO_ADDRESS
    )
    assert (
        populated_base_pool_registry.get_base_pool_for_lp_token(
            tripool_lp_token
        )
        == ZERO_ADDRESS
    )
    assert (
        populated_base_pool_registry.base_pool_list(base_pool_location)
        == last_base_pool
    )
    assert populated_base_pool_registry.get_n_coins(tripool_address) == 0
