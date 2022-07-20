def test_all_pools(populated_metaregistry, pool):
    assert populated_metaregistry.is_registered(pool)
