from ctypes import create_unicode_buffer
import ape
import pytest
from tests.mainnet.metaregistry.api.utils import check_pool_already_registered


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry, stable_registry_handler
):

    if check_pool_already_registered(
        populated_metaregistry, stable_registry_pool, stable_registry_handler
    ):
        pytest.skip()

    actual_output = stable_registry.get_fees(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_fees(stable_registry_pool)

    assert actual_output == metaregistry_output


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory, stable_factory_handler
):

    if check_pool_already_registered(
        populated_metaregistry, stable_factory_pool, stable_factory_handler
    ):
        pytest.skip()

    actual_output = stable_factory.get_fees(stable_factory_pool)
    metaregistry_output = populated_metaregistry.get_fees(stable_factory_pool)

    assert actual_output == metaregistry_output


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    crypto_registry,
    crypto_registry_handler,
    curve_pool_v2,
):

    if sum(crypto_registry.get_balances(crypto_registry_pool)) == 0:
        with ape.reverts():
            curve_pool_v2(crypto_registry_pool).fee()
        pytest.skip(
            f"crypto factory pool {crypto_registry_pool} is empty and factory pools tend to "
            "revert for `fee()` since calcs are needed and they can't be done "
            "for an empty pool"
        )

    if check_pool_already_registered(
        populated_metaregistry, crypto_registry_pool, crypto_registry_handler
    ):
        pytest.skip("crypto registry pool already registered")

    actual_output = crypto_registry.get_fees(crypto_registry_pool)
    metaregistry_output = populated_metaregistry.get_fees(crypto_registry_pool)
    for j, output in enumerate(actual_output):
        assert output == metaregistry_output[j]


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    crypto_factory_handler,
    curve_pool_v2,
):

    if sum(crypto_factory.get_balances(crypto_factory_pool)) == 0:
        with ape.reverts():
            curve_pool_v2(crypto_factory_pool).fee()
        pytest.skip(
            f"crypto factory pool {crypto_factory_pool} is empty and factory pools tend to "
            "revert for `fee()` since calcs are needed and they can't be done "
            "for an empty pool"
        )

    if check_pool_already_registered(
        populated_metaregistry, crypto_factory_pool, crypto_factory_handler
    ):
        pytest.skip("crypto factory pool already registered")

    curve_contract = curve_pool_v2(crypto_factory_pool)
    actual_output = [
        curve_contract.fee(),
        curve_contract.admin_fee(),
        curve_contract.mid_fee(),
        curve_contract.out_fee(),
    ]
    metaregistry_output = populated_metaregistry.get_fees(crypto_factory_pool)
    for j, output in enumerate(actual_output):
        assert output == metaregistry_output[j]
