def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    metaregistry_output = populated_metaregistry.get_decimals(
        stable_registry_pool
    )
    actual_output = list(stable_registry.get_decimals(stable_registry_pool))
    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]


def test_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    metaregistry_output = populated_metaregistry.get_decimals(
        stable_factory_pool
    )
    actual_output = list(stable_factory.get_decimals(stable_factory_pool))
    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    metaregistry_output = populated_metaregistry.get_decimals(
        crypto_registry_pool
    )
    actual_output = list(crypto_registry.get_decimals(crypto_registry_pool))
    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory
):
    metaregistry_output = populated_metaregistry.get_decimals(
        crypto_factory_pool
    )
    actual_output = list(crypto_factory.get_decimals(crypto_factory_pool))
    for idx, coin in enumerate(actual_output):
        assert coin == metaregistry_output[idx]
