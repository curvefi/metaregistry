def test_add_deployed_pool_to_metaregistry(
    metaregistry_mock,
    sync_stable_factory_registry,
    euro_pool,
    stable_factory_handler,
    stable_factory,
):

    assert metaregistry_mock.is_registered(euro_pool)
