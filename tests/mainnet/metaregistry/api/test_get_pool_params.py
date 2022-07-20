@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_pool_params_stableswap_cryptoswap(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    """This test is only for stableswap and cryptoswap amms"""

    print(f"testing get_pool_params for pool: {pool}")
    metaregistry_output = metaregistry.get_pool_params(pool)
    print(f"metaregistry output: {metaregistry_output}")
    actual_pool_params = [0] * 20

    v2_pool = curve_pool_v2(pool)

    # A
    if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
        actual_pool_params[0] = registry.get_A(pool)
    else:
        actual_pool_params[0] = v2_pool.A()

    # D, gamma
    if registry_id == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
        actual_pool_params[1] = registry.get_D(pool)
        actual_pool_params[2] = registry.get_gamma(pool)
    elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
        actual_pool_params[1] = v2_pool.D()
        actual_pool_params[2] = v2_pool.gamma()

    # allowed_extra_profit
    if registry_id in [
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    ]:
        actual_pool_params[3] = v2_pool.allowed_extra_profit()
        actual_pool_params[4] = v2_pool.fee_gamma()
        actual_pool_params[5] = v2_pool.adjustment_step()
        actual_pool_params[6] = v2_pool.ma_half_time()

    print(f"actual pool params: {actual_pool_params}")
    assert actual_pool_params == metaregistry_output
    print(f"passed for pool: {pool}.")
