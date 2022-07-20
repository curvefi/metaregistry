def _is_dao_onboarded_gauge(_gauge):

    try:
        gauge_controller().gauge_types(_gauge)
    except ape.exceptions.VirtualMachineError:
        return False

    if liquidity_gauge(_gauge).is_killed():
        return False

    return True


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_gauges(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    if registry_id in [
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ]:

        actual_output = registry.get_gauges(pool)

    else:  # for factory pools, some checks need to be done

        gauge = registry.get_gauge(pool)

        # we check if the gauge is dao onboarded, else
        # gauge_controller().gauge_types(gauge) will revert
        # as gauge type is zero. This slows down tests significantly
        if _is_dao_onboarded_gauge(gauge):
            actual_output = (
                [gauge] + [ape.utils.ZERO_ADDRESS] * 9,
                [gauge_controller().gauge_types(gauge)] + [0] * 9,
            )
        else:
            actual_output = (
                [gauge] + [ape.utils.ZERO_ADDRESS] * 9,
                [0] * 10,
            )

    metaregistry_output = metaregistry.get_gauges(pool)
    assert actual_output == metaregistry_output
