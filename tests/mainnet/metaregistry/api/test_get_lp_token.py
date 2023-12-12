def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    actual_output = stable_registry.get_lp_token(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_lp_token(
        stable_registry_pool
    )
    assert metaregistry_output == actual_output


def test_stable_factory_pools(populated_metaregistry, stable_factory_pool):
    metaregistry_output = populated_metaregistry.get_lp_token(
        stable_factory_pool
    )

    # pool == lp_token for stable factory
    assert stable_factory_pool == metaregistry_output


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    actual_output = crypto_registry.get_lp_token(crypto_registry_pool)
    metaregistry_output = populated_metaregistry.get_lp_token(
        crypto_registry_pool
    )
    assert metaregistry_output == actual_output


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory
):
    actual_output = crypto_factory.get_token(crypto_factory_pool)
    metaregistry_output = populated_metaregistry.get_lp_token(
        crypto_factory_pool
    )
    assert metaregistry_output == actual_output
