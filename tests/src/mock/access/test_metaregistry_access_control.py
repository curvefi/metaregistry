import brownie
from brownie import ZERO_ADDRESS, chain

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


def test_reset_registry_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.reset_registry(0, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_reset_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.reset({"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_commit_transfer_ownership_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.commit_transfer_ownership(alice, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_apply_transfer_ownership_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.apply_transfer_ownership({"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_apply_transfer_ownership_no_transfer(metaregistry_mock, owner):
    with brownie.reverts():
        tx = metaregistry_mock.apply_transfer_ownership({"from": owner})
        assert tx.revert_msg == "dev: no active transfer"


def test_revert_transfer_ownership_non_authorized(metaregistry_mock, alice):
    with brownie.reverts():
        tx = metaregistry_mock.revert_transfer_ownership({"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_revert_transfer_ownership(metaregistry_mock, alice, owner):
    metaregistry_mock.commit_transfer_ownership(alice, {"from": owner})
    metaregistry_mock.revert_transfer_ownership({"from": owner})
    assert metaregistry_mock.transfer_ownership_deadline() == 0
    assert metaregistry_mock.owner() == owner


def test_ownership_transfer(metaregistry_mock, alice, owner):
    chain.snapshot()
    metaregistry_mock.commit_transfer_ownership(alice, {"from": owner})

    assert metaregistry_mock.future_owner() == alice
    assert metaregistry_mock.transfer_ownership_deadline() > 0

    with brownie.reverts():
        tx = metaregistry_mock.commit_transfer_ownership(alice, {"from": owner})
        assert tx.revert_msg == "dev: active transfer"

    with brownie.reverts():
        tx = metaregistry_mock.apply_transfer_ownership({"from": owner})
        assert tx.revert_msg == "dev: insufficient time"

    chain.sleep(3600 * 24 * 4)
    chain.mine(1)

    metaregistry_mock.apply_transfer_ownership({"from": owner})
    assert metaregistry_mock.owner() == alice
    assert metaregistry_mock.transfer_ownership_deadline() == 0
    chain.revert()
