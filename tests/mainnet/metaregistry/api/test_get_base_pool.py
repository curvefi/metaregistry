from eth.constants import ZERO_ADDRESS


def test_all(populated_metaregistry, populated_base_pool_registry, pool):
    coins = populated_metaregistry.get_coins(pool)
    actual_output = ZERO_ADDRESS
    for coin in coins:
        actual_output = (
            populated_base_pool_registry.get_base_pool_for_lp_token(coin)
        )
        if actual_output != ZERO_ADDRESS:
            break

    metaregistry_output = populated_metaregistry.get_base_pool(pool)
    assert metaregistry_output == actual_output
