@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_name(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    if registry_id in [
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ]:

        actual_output = registry.get_pool_name(pool)

    elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:

        actual_output = ape.interface.ERC20(registry.get_token(pool)).name()

    else:

        actual_output = ape.interface.ERC20(pool).name()

    metaregistry_output = metaregistry.get_pool_name(pool)
    assert actual_output == metaregistry_output
