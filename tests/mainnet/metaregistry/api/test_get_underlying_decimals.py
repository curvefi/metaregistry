@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_underlying_decimals(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    # metaregistry underlying decimals:
    metaregistry_output = metaregistry.get_underlying_decimals(pool)
    assert metaregistry_output[1] != 0  # there has to be a second coin!

    # get actual decimals: first try registry
    # todo: include CryptoRegistryHandler when CryptoRegistry gets updated
    pool_is_metapool = metaregistry.is_meta(pool)
    pool_underlying_decimals_exceptions = {
        # eth: ankreth pool returns [18, 0] when it should return:
        "0xA96A65c051bF88B4095Ee1f2451C2A9d43F53Ae2": [18, 18],
        # compound pools. ctokens are 8 decimals. underlying is dai usdc:
        "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56": [18, 6],
        # cream-yearn cytokens are 8 decimals, whereas underlying is
        # dai usdc usdt:
        "0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF": [18, 6, 6],
        # usdt pool has cDAI, cUSDC and USDT (which is 8, 8, 6):
        "0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C": [18, 6, 6],
    }

    if pool in pool_underlying_decimals_exceptions:
        actual_output = pool_underlying_decimals_exceptions[pool]
    elif pool_is_metapool:
        underlying_coins = metaregistry.get_underlying_coins(pool)
        actual_output = []
        for i in range(len(underlying_coins)):
            if underlying_coins[i] == ape.utils.ZERO_ADDRESS:
                actual_output.append(0)
            else:
                actual_output.append(ape.interface.ERC20(underlying_coins[i]).decimals())

        assert actual_output[2] != 0  # there has to be a third coin!
    else:
        actual_output = list(registry.get_decimals(pool))

    # pad zeros to match metaregistry_output length
    actual_output += [0] * (len(metaregistry_output) - len(actual_output))

    assert metaregistry_output == tuple(actual_output)
