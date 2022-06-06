import brownie
from brownie import ZERO_ADDRESS, chain


def test_update_address_provider_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_address_provider(ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_update_single_registry_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_single_registry(
            0, ZERO_ADDRESS, 0, ZERO_ADDRESS, "a", True, {"from": alice}
        )
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_handler_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_registry_handler(0, ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_add_registry_by_address_provider_id_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.add_registry_by_address_provider_id(0, ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_switch_registry_active_status(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.switch_registry_active_status(1, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_addresses_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_registry_addresses({"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_commit_transfer_ownership_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.commit_transfer_ownership(alice, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_apply_transfer_ownership_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.apply_transfer_ownership({"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_apply_transfer_ownership_no_transfer(metaregistry, owner):
    with brownie.reverts():
        tx = metaregistry.apply_transfer_ownership({"from": owner})
        assert tx.revert_msg == "dev: no active transfer"


def test_revert_transfer_ownership_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.revert_transfer_ownership({"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_revert_transfer_ownership(metaregistry, alice, owner):
    metaregistry.commit_transfer_ownership(alice, {"from": owner})
    metaregistry.revert_transfer_ownership({"from": owner})
    assert metaregistry.transfer_ownership_deadline() == 0
    assert metaregistry.owner() == owner


def test_ownership_transfer(metaregistry, alice, owner):
    chain.snapshot()
    metaregistry.commit_transfer_ownership(alice, {"from": owner})

    assert metaregistry.future_owner() == alice
    assert metaregistry.transfer_ownership_deadline() > 0

    with brownie.reverts():
        tx = metaregistry.commit_transfer_ownership(alice, {"from": owner})
        assert tx.revert_msg == "dev: active transfer"

    with brownie.reverts():
        tx = metaregistry.apply_transfer_ownership({"from": owner})
        assert tx.revert_msg == "dev: insufficient time"

    chain.sleep(3600 * 24 * 4)
    chain.mine(1)

    metaregistry.apply_transfer_ownership({"from": owner})
    assert metaregistry.owner() == alice
    assert metaregistry.transfer_ownership_deadline() == 0
    chain.revert()
