@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_fees(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)
    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    # curve v2 pools need to calculates self.xp() for getting self.fee(), and that is not
    # possible if the pool is empty.
    if (
        registry_id
        in [METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX, METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX]
        and sum(metaregistry.get_balances(pool)) == 0
    ):
        with ape.reverts():
            curve_pool_v2(pool).fee()
        pytest.skip(
            f"crypto factory pool {pool} is empty and factory pools tend to "
            "revert for `fee()` since calcs are needed and they can't be done "
            "for an empty pool"
        )

    if check_pool_already_registered(metaregistry, pool, registry_handler):
        pytest.skip()

    # get_fees
    if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
        actual_output = registry.get_fees(pool)
    else:
        curve_contract = curve_pool_v2(pool)
        actual_output = [
            curve_contract.fee(),
            curve_contract.admin_fee(),
            curve_contract.mid_fee(),
            curve_contract.out_fee(),
        ]

    metaregistry_output = metaregistry.get_fees(pool)
    for j, output in enumerate(actual_output):
        assert output == metaregistry_output[j]
