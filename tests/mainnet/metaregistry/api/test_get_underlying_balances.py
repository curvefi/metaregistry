@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_balances(
    metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    if sum(metaregistry.get_balances(pool)) == 0:
        pytest.skip(f"Empty pool: {pool}")

    elif registry_id in [
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ] and metaregistry.is_meta(pool):

        # the metaregistry uses get_balances if the pool is not a metapool:
        actual_output = registry.get_underlying_balances(pool)

    elif registry_id == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX and metaregistry.is_meta(pool):
        # crypto factory does not have get_underlying_balances method.
        v2_pool = curve_pool_v2(pool)

        coins = registry.get_coins(pool)
        pool_balances = [0] * MAX_COINS

        for idx, coin in enumerate(coins):
            base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)
            if base_pool != ape.utils.ZERO_ADDRESS:
                basepool_coins = base_pool_registry_updated.get_coins(base_pool)
                basepool_contract = ape.Contract(base_pool)
                basepool_lp_token_balance = v2_pool.balances(idx)
                lp_token_supply = ape.interfaces.ERC20(coin).totalSupply()
                ratio_in_pool = basepool_lp_token_balance / lp_token_supply
                for idy, coin in enumerate(basepool_coins):
                    if coin == ape.utils.ZERO_ADDRESS:
                        break
                    pool_balances[idx] = basepool_contract.balances(idy) * ratio_in_pool

                break
            pool_balances[idx] = v2_pool.balances(idx)
        actual_output = pool_balances

    else:

        actual_output = registry.get_balances(pool)

    metaregistry_output = metaregistry.get_underlying_balances(pool)

    if metaregistry.is_meta(pool):
        assert metaregistry_output[2] > 0  # it must have a third coin
    else:
        assert metaregistry_output[1] > 0  # it must have a second coin

    for idx, registry_value in enumerate(actual_output):
        if metaregistry_output[idx] - registry_value != 0:
            assert registry_value == pytest.approx(metaregistry_output[idx])
        else:
            assert True
