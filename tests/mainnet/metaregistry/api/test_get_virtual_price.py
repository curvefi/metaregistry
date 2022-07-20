@pytest.mark.parametrize("pool_id", range(MAX_POOLS))
def test_get_virtual_price_from_lp_token(metaregistry, registry_pool_index_iterator, pool_id):

    skip_if_pool_id_gte_max_pools_in_registry(pool_id, registry_pool_index_iterator)

    registry_id, registry_handler, registry, pool = registry_pool_index_iterator[pool_id]

    # skip if pool has little to no liquidity, since vprice queries will most likely bork:
    pool_balances = metaregistry.get_balances(pool)
    lp_token = metaregistry.get_lp_token(pool)
    if sum(pool_balances) == 0:

        with ape.reverts():
            metaregistry.get_virtual_price_from_lp_token(lp_token)

        pytest.skip(f"empty pool: {pool}")

    elif sum(pool_balances) < 100:  # tiny pool
        with ape.reverts():
            metaregistry.get_virtual_price_from_lp_token(lp_token)

        pytest.skip(f"tiny pool: {pool}")

    coin_decimals = metaregistry.get_decimals(pool)
    coins = metaregistry.get_coins(pool)

    # check if pool balances after accounting for decimals is legible.
    # some scam tokens can have weird token properties (e.g. ELONX)
    pool_balances_float = []
    for i in range(len(pool_balances)):

        if coins[i] == ape.utils.ZERO_ADDRESS:
            break

        pool_balances_float.append(pool_balances[i] / 10 ** coin_decimals[i])

        if (
            coin_decimals[i] == 0
            and ape.interface.ERC20(metaregistry.get_coins(pool)[0]).decimals() == 0
        ):
            with ape.reverts():
                metaregistry.get_virtual_price_from_lp_token(lp_token)
            pytest.skip(f"skem token {coins[i]} in pool {pool} with zero decimals")

    # check if pool balances are skewed: vprice calc will bork if one of the coin
    # balances is close to zero.
    if (
        max(pool_balances_float) - min(pool_balances_float)
        == pytest.approx(max(pool_balances_float))
        and min(pool_balances_float) < 1
    ):
        with ape.reverts():
            metaregistry.get_virtual_price_from_lp_token(lp_token)

        pytest.skip(
            f"skewed pool: {pool} as num coins (decimals divided) at index {i} is "
            f"{pool_balances[i] / 10 ** coin_decimals[i]}"
        )

    # virtual price from underlying child registries:
    if registry_id in [
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    ]:
        actual_output = registry.get_virtual_price_from_lp_token(lp_token)
    else:  # factories dont have virtual price getters
        actual_output = curve_pool(pool).get_virtual_price()

    # virtual price from metaregistry:
    metaregistry_output = metaregistry.get_virtual_price_from_lp_token(lp_token)
    assert actual_output == metaregistry_output
