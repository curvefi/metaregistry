def test_all_pools(populated_metaregistry, pool):
    lp_token = populated_metaregistry.get_lp_token(pool)
    metaregistry_output = populated_metaregistry.get_pool_from_lp_token(
        lp_token
    )
    assert pool == metaregistry_output
