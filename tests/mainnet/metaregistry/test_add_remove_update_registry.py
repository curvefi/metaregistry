import boa


def test_revert_unauthorised_add_registry_handler(
    metaregistry, unauthorised_address, random_address
):
    with boa.reverts():
        tx = metaregistry.add_registry_handler(
            random_address, sender=unauthorised_address
        )
        assert tx.revert_msg == "dev: only owner"


def test_revert_unauthorised_update_registry_handler(
    populated_metaregistry, unauthorised_address, random_address
):
    with boa.reverts():
        tx = populated_metaregistry.update_registry_handler(
            0, random_address, sender=unauthorised_address
        )
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_handler_invalid_registry(
    populated_metaregistry, random_address, owner
):
    with boa.reverts():
        populated_metaregistry.update_registry_handler(
            10, random_address, sender=owner
        )


def test_update_registry_handler(
    populated_metaregistry,
    stable_registry_handler,
    stable_registry_handler_index,
    random_address,
    owner,
):
    assert (
        populated_metaregistry.get_registry(stable_registry_handler_index)
        == stable_registry_handler.address
    )

    populated_metaregistry.update_registry_handler(
        stable_registry_handler_index,
        random_address,
        sender=owner,
    )
    assert (
        populated_metaregistry.get_registry(stable_registry_handler_index)
        == random_address
    )
