def _get_underlying_coins_from_registry(registry_id, registry, base_pool_registry_updated, pool):

    coins = registry.get_coins(pool)
    underlying_coins = [ape.utils.ZERO_ADDRESS] * MAX_COINS

    for idx, coin in enumerate(coins):

        base_pool = base_pool_registry_updated.get_base_pool_for_lp_token(coin)

        if base_pool == ape.utils.ZERO_ADDRESS:

            underlying_coins[idx] = coin

        else:

            basepool_coins = base_pool_registry_updated.get_coins(base_pool)

            for bp_coin in basepool_coins:

                if bp_coin == ape.utils.ZERO_ADDRESS:
                    break

                underlying_coins[idx] = bp_coin
                idx += 1

            break

    if registry_id != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:

        try:

            registry_underlying_coins = registry.get_underlying_coins(pool)
            if registry_underlying_coins != underlying_coins:
                warnings.warn(f"Pool {pool} might be a lending pool.")
                return registry_underlying_coins

        except ape.exceptions.VirtualMachineError:
            # virtual machine errors prop up for registry.get_underlying_coins if pool
            # is completely depegged. We check this by setting up a revert check and
            # then returning underlying_coins:git
            balances = registry.get_balances(pool)
            decimals = registry.get_decimals(pool)

            float_balances = [balances[i] / 10 ** decimals[i] for i in range(len(decimals))]
            if min(float_balances) < 1:
                with ape.reverts():
                    registry.get_underlying_coins(pool)
                return underlying_coins

    return underlying_coins


@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_coins(
    metaregistry, registry_pool_index_iterator, base_pool_registry_updated, pool_id
):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]
    metaregistry_output = metaregistry.get_underlying_coins(pool)

    actual_output = _get_underlying_coins_from_registry(
        registry_id, registry, base_pool_registry_updated, pool
    )

    for idx, registry_value in enumerate(actual_output):
        assert registry_value == metaregistry_output[idx]
