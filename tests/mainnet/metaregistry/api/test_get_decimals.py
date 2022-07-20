@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_decimals(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_decimals(pool)

    # get actuals and pad zeroes to match metaregistry_output length
    actual_output = list(registry.get_decimals(pool))
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))

    # check if there are more than 1 decimals:
    assert metaregistry_output[1] != 0
    assert actual_output[1] != 0

    # check if they match:
    assert tuple(actual_output) == metaregistry_output
