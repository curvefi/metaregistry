@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    metaregistry_output = metaregistry.get_coins(pool)

    actual_output = list(registry.get_coins(pool))
    actual_output += [ape.utils.ZERO_ADDRESS] * (len(metaregistry_output) - len(actual_output))

    assert tuple(actual_output) == metaregistry_output
