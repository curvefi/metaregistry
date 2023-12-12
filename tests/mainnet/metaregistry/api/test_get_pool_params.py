def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    actual_pool_params = [0] * 20
    actual_pool_params[0] = stable_registry.get_A(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_pool_params(
        stable_registry_pool
    )

    assert actual_pool_params == metaregistry_output


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    metaregistry_output = populated_metaregistry.get_pool_params(
        stable_factory_pool
    )
    actual_pool_params = [0] * 20
    actual_pool_params[0] = stable_factory.get_A(stable_factory_pool)

    assert actual_pool_params == metaregistry_output


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    crypto_registry,
    curve_pool_v2,
):
    metaregistry_output = populated_metaregistry.get_pool_params(
        crypto_registry_pool
    )
    v2_pool = curve_pool_v2(crypto_registry_pool)

    actual_pool_params = [0] * 20
    actual_pool_params[0] = crypto_registry.get_A(crypto_registry_pool)
    actual_pool_params[1] = crypto_registry.get_D(crypto_registry_pool)
    actual_pool_params[2] = crypto_registry.get_gamma(crypto_registry_pool)
    actual_pool_params[3] = v2_pool.allowed_extra_profit()
    actual_pool_params[4] = v2_pool.fee_gamma()
    actual_pool_params[5] = v2_pool.adjustment_step()
    actual_pool_params[6] = v2_pool.ma_half_time()
    assert actual_pool_params == metaregistry_output


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, curve_pool_v2
):
    metaregistry_output = populated_metaregistry.get_pool_params(
        crypto_factory_pool
    )
    v2_pool = curve_pool_v2(crypto_factory_pool)

    actual_pool_params = [0] * 20
    actual_pool_params[0] = v2_pool.A()
    actual_pool_params[1] = v2_pool.D()
    actual_pool_params[2] = v2_pool.gamma()
    actual_pool_params[3] = v2_pool.allowed_extra_profit()
    actual_pool_params[4] = v2_pool.fee_gamma()
    actual_pool_params[5] = v2_pool.adjustment_step()
    actual_pool_params[6] = v2_pool.ma_half_time()
    assert actual_pool_params == metaregistry_output
