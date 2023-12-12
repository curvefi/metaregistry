# pool is asset type 0 on metaregistry at _handler_id == 0 but 3 (correct)
# at _handler_id == 1
EXCEPTIONS = {"0xFD5dB7463a3aB53fD211b4af195c5BCCC1A03890": 3}


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    assert populated_metaregistry.get_pool_asset_type(
        stable_registry_pool
    ) == stable_registry.get_pool_asset_type(stable_registry_pool)


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    metaregistry_output = populated_metaregistry.get_pool_asset_type(
        stable_factory_pool
    )
    if stable_factory_pool in EXCEPTIONS:
        metaregistry_output = EXCEPTIONS[stable_factory_pool]
    assert metaregistry_output == stable_factory.get_pool_asset_type(
        stable_factory_pool
    )


def test_crypto_registry_pools(populated_metaregistry, crypto_registry_pool):
    assert (
        populated_metaregistry.get_pool_asset_type(crypto_registry_pool) == 4
    )


def test_crypto_factory_pools(populated_metaregistry, crypto_factory_pool):
    assert populated_metaregistry.get_pool_asset_type(crypto_factory_pool) == 4
