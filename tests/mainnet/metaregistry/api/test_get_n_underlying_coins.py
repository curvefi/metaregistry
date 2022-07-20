@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_n_underlying_coins(
    metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    metaregistry_output = metaregistry.get_n_underlying_coins(pool)

    coins = registry.get_coins(pool)
    num_coins = 0
    for coin in coins:
        if coin == ape.utils.ZERO_ADDRESS:
            break
        base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)
        if base_pool != ape.utils.ZERO_ADDRESS:
            basepool_coins = base_pool_registry_updated.get_coins(base_pool)
            num_bp_coins = sum([1 for i in basepool_coins if i != ape.utils.ZERO_ADDRESS])
            num_coins += num_bp_coins
        else:
            num_coins += 1

    assert num_coins == metaregistry_output
