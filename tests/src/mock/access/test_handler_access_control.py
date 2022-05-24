import brownie


def test_sync_pool_list_non_authorized(handlers, alice):
    for handler in handlers:
        with brownie.reverts():
            tx = handler.sync_pool_list(0, {"from": alice})
            assert tx.revert_msg == "dev: only metaregistry has access"
