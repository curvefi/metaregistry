import brownie

from tests.utils.constants import METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, TRIPOOL


def test_revert_unauthorised_add_registry_handler(metaregistry, unauthorised_account):
    with brownie.reverts():
        tx = metaregistry.add_registry_handler(brownie.ZERO_ADDRESS, {"from": unauthorised_account})
        assert tx.revert_msg == "dev: only owner"


def test_revert_unauthorised_update_registry_handler(metaregistry, unauthorised_account):
    with brownie.reverts():
        tx = metaregistry.update_registry_handler(
            0, brownie.ZERO_ADDRESS, {"from": unauthorised_account}
        )
        assert tx.revert_msg == "dev: only owner"


def test_update_registry_handler_invalid_registry(metaregistry, owner):
    with brownie.reverts():
        metaregistry.update_registry_handler(10, TRIPOOL, {"from": owner})


def test_update_registry_handler(metaregistry, owner):
    metaregistry.update_registry_handler(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, TRIPOOL, {"from": owner}
    )
    assert metaregistry.get_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX) == TRIPOOL
