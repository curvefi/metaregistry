@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_lp_token(
    metaregistry,
    registry_pool_index_iterator,
    stable_registry_handler_index,
    stable_factory_handler_index,
    crypto_registry_handler_index,
    crypto_factory_handler_index,
    pool_id,
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, _, registry, pool = registry_pool_index_iterator[pool_id]

    # stable_registry and crypto_registry have lp_tokens
    if registry_id in [
        stable_registry_handler_index,
        crypto_registry_handler_index,
    ]:

        actual_output = registry.get_lp_token(pool)

    # pool == lp_token for stable factory
    elif registry_id == stable_factory_handler_index:

        actual_output = pool

    else:

        actual_output = registry.get_token(pool)

    metaregistry_output = metaregistry.get_lp_token(pool)
    assert actual_output == metaregistry_output
