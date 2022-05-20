import brownie
from brownie import ZERO_ADDRESS

from ...utils.constants import MAX_COINS


def test_update_coin_map_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_coin_map(
            ZERO_ADDRESS, [ZERO_ADDRESS] * MAX_COINS, 2, {"from": alice}
        )
        assert tx.revert_msg == "dev: authorized handlers only"


def test_update_coin_map_for_underlying_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_coin_map_for_underlying(
            ZERO_ADDRESS, [ZERO_ADDRESS] * MAX_COINS, [ZERO_ADDRESS] * MAX_COINS, 2, {"from": alice}
        )
        assert tx.revert_msg == "dev: authorized handlers only"


def test_update_address_provider_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_address_provider(ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_update_lp_token_mapping_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_lp_token_mapping(ZERO_ADDRESS, ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: authorized handlers only"


def test_update_internal_pool_registry_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_internal_pool_registry(ZERO_ADDRESS, 1, {"from": alice})
        assert tx.revert_msg == "dev: authorized handlers only"


def test_update_single_registry_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_single_registry(
            0, ZERO_ADDRESS, 0, ZERO_ADDRESS, "a", True, {"from": alice}
        )
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_handler_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_registry_handler(0, ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_add_registry_by_address_provider_id_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.add_registry_by_address_provider_id(0, ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_switch_registry_active_status(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.switch_registry_active_status(1, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_addresses_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.update_registry_addresses({"from": alice})
        assert tx.revert_msg == "dev: only owner"
