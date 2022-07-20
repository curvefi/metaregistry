from this import d
import ape
import pytest

from tests.mainnet.metaregistry.api.utils import check_pool_already_registered


def _is_dao_onboarded_gauge(_gauge, gauge_controller, liquidity_gauge):

    try:
        gauge_controller().gauge_types(_gauge)
    except ape.exceptions.VirtualMachineError:
        return False

    if liquidity_gauge(_gauge).is_killed():
        return False

    return True


def _get_factory_gauge(registry, pool, gauge_controller, liquidity_gauge):

    gauge = registry.get_gauge(pool)

    # we check if the gauge is dao onboarded, else
    # gauge_controller().gauge_types(gauge) will revert
    # as gauge type is zero. This slows down tests significantly
    if _is_dao_onboarded_gauge(gauge, gauge_controller, liquidity_gauge):
        return (
            [gauge] + [ape.utils.ZERO_ADDRESS] * 9,
            [gauge_controller.gauge_types(gauge)] + [0] * 9,
        )
    else:
        return (
            [gauge] + [ape.utils.ZERO_ADDRESS] * 9,
            [0] * 10,
        )


def test_stable_registry_pools(
    populated_metaregistry,
    stable_registry_pool,
    stable_registry,
    stable_registry_handler,
):

    if check_pool_already_registered(
        populated_metaregistry, stable_registry_pool, stable_registry_handler
    ):
        pytest.skip()

    actual_output = stable_registry.get_gauges(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_gauges(stable_registry_pool)
    assert actual_output == metaregistry_output


def test_stable_factory_pools(
    populated_metaregistry,
    stable_factory_pool,
    stable_factory,
    stable_factory_handler,
    gauge_controller,
    liquidity_gauge,
):

    if check_pool_already_registered(
        populated_metaregistry, stable_factory_pool, stable_factory_handler
    ):
        pytest.skip()

    actual_output = _get_factory_gauge(
        stable_factory, stable_factory_pool, gauge_controller, liquidity_gauge
    )
    metaregistry_output = populated_metaregistry.get_gauges(stable_factory_pool)
    assert actual_output == metaregistry_output


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry, crypto_registry_handler
):

    if check_pool_already_registered(
        populated_metaregistry, crypto_registry_pool, crypto_registry_handler
    ):
        pytest.skip("crypto registry pool already registered")

    actual_output = crypto_registry.get_gauges(crypto_registry_pool)
    metaregistry_output = populated_metaregistry.get_gauges(crypto_registry_pool)
    assert actual_output == metaregistry_output


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    crypto_factory_handler,
    gauge_controller,
    liquidity_gauge,
):

    if check_pool_already_registered(
        populated_metaregistry, crypto_factory_pool, crypto_factory_handler
    ):
        pytest.skip()

    actual_output = _get_factory_gauge(
        crypto_factory, crypto_factory_pool, gauge_controller, liquidity_gauge
    )
    metaregistry_output = populated_metaregistry.get_gauges(crypto_factory_pool)
    assert actual_output == metaregistry_output
