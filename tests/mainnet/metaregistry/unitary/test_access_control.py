import brownie


def test_update_address_provider_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_address_provider(brownie.ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_update_single_registry_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_single_registry(
            0, brownie.ZERO_ADDRESS, 0, brownie.ZERO_ADDRESS, "a", True, {"from": alice}
        )
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_handler_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_registry_handler(0, brownie.ZERO_ADDRESS, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_add_registry_by_address_provider_id_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.add_registry_by_address_provider_id(
            0, brownie.ZERO_ADDRESS, {"from": alice}
        )
        assert tx.revert_msg == "dev: only owner"


def test_switch_registry_active_status(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.switch_registry_active_status(1, {"from": alice})
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_addresses_non_authorized(metaregistry, alice):
    with brownie.reverts():
        tx = metaregistry.update_registry_addresses({"from": alice})
        assert tx.revert_msg == "dev: only owner"
