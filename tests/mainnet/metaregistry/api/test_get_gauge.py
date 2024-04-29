from boa import BoaError
from eth.constants import ZERO_ADDRESS


def _is_dao_onboarded_gauge(_gauge, gauge_controller, liquidity_gauge):
    try:
        gauge_controller.gauge_types(_gauge)
    except BoaError:
        return False

    if liquidity_gauge(_gauge).is_killed():
        return False

    return True


def _get_factory_gauge(
    registry,
    pool,
    gauge_controller,
    liquidity_gauge,
    default_gauge_type: int = 0,
):
    gauge = registry.get_gauge(pool)

    # we check if the gauge is dao onboarded, else
    # gauge_controller.gauge_types(gauge) will revert
    # as gauge type is zero. This slows down tests significantly
    if _is_dao_onboarded_gauge(gauge, gauge_controller, liquidity_gauge):
        return (
            [gauge] + [ZERO_ADDRESS] * 9,
            [gauge_controller.gauge_types(gauge)] + [0] * 9,
        )
    else:
        return (
            [gauge] + [ZERO_ADDRESS] * 9,
            [default_gauge_type] * 10,
        )


def test_stable_registry_pools(
    populated_metaregistry,
    stable_registry_pool,
    stable_registry,
):
    actual_output = stable_registry.get_gauges(stable_registry_pool)
    metaregistry_output_gauge = populated_metaregistry.get_gauge(
        stable_registry_pool
    )
    metaregistry_output_gauge_type = populated_metaregistry.get_gauge_type(
        stable_registry_pool
    )

    assert actual_output[0][0] == metaregistry_output_gauge
    assert actual_output[1][0] == metaregistry_output_gauge_type


def test_stable_factory_pools(
    populated_metaregistry,
    stable_factory_pool,
    stable_factory,
    gauge_controller,
    liquidity_gauge,
):
    actual_output = _get_factory_gauge(
        stable_factory, stable_factory_pool, gauge_controller, liquidity_gauge
    )

    # lots of stable registry pools were actually factory pools which then got moved
    # over to the stable factory's storage. During this process, gauge data was not
    # moved over properly. For these pools, the metaregistry automatically goes to
    # the stable registry handler (where the correct gauge data is stored), but the
    # stable factory will not have the right data. We therefore do a manual check for
    # this case:
    pool_registry_handlers = (
        populated_metaregistry.get_registry_handlers_from_pool(
            stable_factory_pool
        )
    )
    num_registry_handlers = len(
        list(filter((ZERO_ADDRESS).__ne__, pool_registry_handlers))
    )

    metaregistry_output_gauge = populated_metaregistry.get_gauge(
        stable_factory_pool, 0, num_registry_handlers - 1
    )
    metaregistry_output_gauge_type = populated_metaregistry.get_gauge_type(
        stable_factory_pool, 0, num_registry_handlers - 1
    )

    assert actual_output[0][0] == metaregistry_output_gauge
    assert actual_output[1][0] == metaregistry_output_gauge_type


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    actual_output = crypto_registry.get_gauges(crypto_registry_pool)
    metaregistry_output_gauge = populated_metaregistry.get_gauge(
        crypto_registry_pool
    )
    metaregistry_output_gauge_type = populated_metaregistry.get_gauge_type(
        crypto_registry_pool
    )

    assert actual_output[0][0] == metaregistry_output_gauge
    assert actual_output[1][0] == metaregistry_output_gauge_type


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    gauge_controller,
    liquidity_gauge,
):
    # warning: gauge_type == 5 : this is true only for crypto pools on ethereum
    actual_output = _get_factory_gauge(
        crypto_factory,
        crypto_factory_pool,
        gauge_controller,
        liquidity_gauge,
        5,  # DEFAULT_GAUGE_TYPE_CRYPTO_FACTORY_POOLS
    )
    metaregistry_output_gauge = populated_metaregistry.get_gauge(
        crypto_factory_pool
    )
    metaregistry_output_gauge_type = populated_metaregistry.get_gauge_type(
        crypto_factory_pool
    )

    assert actual_output[0][0] == metaregistry_output_gauge
    assert metaregistry_output_gauge_type == 5
