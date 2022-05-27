import brownie
from brownie import ZERO_ADDRESS

from ...utils.constants import (
    DAI,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    TRIPOOL,
    TRIPOOL_LPTOKEN,
)


def test_update_address_provider_not_to_address_zero(fn_isolation, metaregistry_mock, owner):
    with brownie.reverts():
        tx = metaregistry_mock.update_address_provider(ZERO_ADDRESS, {"from": owner})
        tx.revert_msg == "dev: not to zero"


def test_update_address_provider(fn_isolation, metaregistry_mock, owner):
    metaregistry_mock.update_address_provider(TRIPOOL, {"from": owner})
    assert metaregistry_mock.address_provider() == TRIPOOL


def test_update_registry_handler_invalid_registry(fn_isolation, metaregistry_mock, owner):
    with brownie.reverts():
        metaregistry_mock.update_registry_handler(10, TRIPOOL, {"from": owner})


def test_update_registry_handler(fn_isolation, metaregistry_mock, owner):
    metaregistry_mock.update_registry_handler(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, TRIPOOL, {"from": owner}
    )
    assert metaregistry_mock.get_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX)[2] == TRIPOOL


def test_update_single_registry(fn_isolation, metaregistry_mock, owner):
    metaregistry_mock.update_single_registry(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        TRIPOOL,
        3,
        TRIPOOL,
        "tripool",
        True,
        {"from": owner},
    )
    assert metaregistry_mock.get_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX) == (
        TRIPOOL,
        3,
        TRIPOOL,
        "tripool",
        True,
    )


def test_switch_registry_active_status_invalid_registry(fn_isolation, metaregistry_mock, owner):
    with brownie.reverts():
        metaregistry_mock.switch_registry_active_status(10, {"from": owner})


def test_switch_registry_active_status(fn_isolation, metaregistry_mock, stable_registry, owner):
    stable_registry.add_pool_without_underlying(
        TRIPOOL,
        3,
        TRIPOOL_LPTOKEN,
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        394770,
        0,
        False,
        False,
        "3pool",
    )
    metaregistry_mock.sync({"from": owner})
    metaregistry_mock.switch_registry_active_status(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, {"from": owner}
    )
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_coins(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_n_coins(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_n_underlying_coins(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_underlying_coins(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.is_registered(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_decimals(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_underlying_decimals(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_balances(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_underlying_balances(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_lp_token(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_gauges(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.is_meta(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_pool_name(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_fees(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_admin_balances(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_pool_asset_type(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_pool_params(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_virtual_price_from_lp_token(TRIPOOL_LPTOKEN)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_base_pool(TRIPOOL)
    with brownie.reverts("no active registry"):
        metaregistry_mock.get_coin_indices(TRIPOOL, DAI, DAI)
