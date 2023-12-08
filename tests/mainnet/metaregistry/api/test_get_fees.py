import boa
import pytest


def _check_dissimilar_length_array_elements_are_equal(output_a, output_b):
    for i in range(min(len(output_a), len(output_b))):
        assert output_a[i] == output_b[i]


def test_stable_registry_pools(
    populated_metaregistry,
    stable_registry_pool,
    stable_registry,
):
    actual_output = stable_registry.get_fees(stable_registry_pool)
    metaregistry_output = populated_metaregistry.get_fees(stable_registry_pool)
    _check_dissimilar_length_array_elements_are_equal(
        actual_output, metaregistry_output
    )


def test_stable_factory_pools(
    populated_metaregistry,
    stable_factory_pool,
    stable_factory,
):
    actual_output = stable_factory.get_fees(stable_factory_pool)
    metaregistry_output = populated_metaregistry.get_fees(stable_factory_pool)
    _check_dissimilar_length_array_elements_are_equal(
        actual_output, metaregistry_output
    )


def test_crypto_registry_pools(
    populated_metaregistry,
    crypto_registry_pool,
    crypto_registry,
    curve_pool_v2,
):
    if sum(crypto_registry.get_balances(crypto_registry_pool)) == 0:
        with boa.reverts():
            curve_pool_v2(crypto_registry_pool).fee()
        pytest.skip(
            f"crypto factory pool {crypto_registry_pool} is empty and factory pools tend to "
            "revert for `fee()` since calcs are needed and they can't be done "
            "for an empty pool"
        )

    actual_output = crypto_registry.get_fees(crypto_registry_pool)
    metaregistry_output = populated_metaregistry.get_fees(crypto_registry_pool)
    _check_dissimilar_length_array_elements_are_equal(
        actual_output, metaregistry_output
    )


def test_crypto_factory_pools(
    populated_metaregistry,
    crypto_factory_pool,
    crypto_factory,
    curve_pool_v2,
):
    if sum(crypto_factory.get_balances(crypto_factory_pool)) == 0:
        with boa.reverts():
            curve_pool_v2(crypto_factory_pool).fee()
        pytest.skip(
            f"crypto factory pool {crypto_factory_pool} is empty and factory pools tend to "
            "revert for `fee()` since calcs are needed and they can't be done "
            "for an empty pool"
        )

    curve_contract = curve_pool_v2(crypto_factory_pool)
    actual_output = [
        curve_contract.fee(),
        curve_contract.admin_fee(),
        curve_contract.mid_fee(),
        curve_contract.out_fee(),
    ]
    metaregistry_output = populated_metaregistry.get_fees(crypto_factory_pool)
    _check_dissimilar_length_array_elements_are_equal(
        actual_output, metaregistry_output
    )
