@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_n_coins(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    metaregistry_output = metaregistry.get_n_coins(pool)

    # crypto factory does not have get_n_coins method
    if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:

        actual_output = registry.get_n_coins(pool)

        # registry returns tuple, we want the first one (since the second)
        # index is about basepool n coins
        if not type(actual_output) == ape.convert.datatypes.Wei:

            actual_output = actual_output[0]

        # registry returns 0 value for n coins: something's not right on the
        # registry's side. find n_coins via registry.get_coins:
        elif actual_output == 0:

            coins = registry.get_coins(pool)
            actual_output = sum([1 for coin in coins if coin != ape.utils.ZERO_ADDRESS])

    else:

        # do get_coins for crypto factory:
        coins = registry.get_coins(pool)
        actual_output = sum([1 for coin in coins if coin != ape.utils.ZERO_ADDRESS])

    assert actual_output == metaregistry_output
