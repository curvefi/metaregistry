import ape
import pytest

EXCEPTIONS = {
    # eth: ankreth pool returns [18, 0] when it should return:
    "0xA96A65c051bF88B4095Ee1f2451C2A9d43F53Ae2": [18, 18],
    # compound pools. ctokens are 8 decimals. underlying is dai usdc:
    "0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56": [18, 6],
    # cream-yearn cytokens are 8 decimals, whereas underlying is
    # dai usdc usdt:
    "0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF": [18, 6, 6],
    # usdt pool has cDAI, cUSDC and USDT (which is [8, 8, 6]):
    "0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C": [18, 6, 6],
}


def _test_underlying_decimals_getter(metaregistry, registry, pool):

    metaregistry_output = metaregistry.get_underlying_decimals(pool)
    assert metaregistry_output[1] != 0  # there has to be a second coin!

    pool_is_metapool = metaregistry.is_meta(pool)
    if pool in EXCEPTIONS:
        actual_output = EXCEPTIONS[pool]
    elif pool_is_metapool:
        underlying_coins = metaregistry.get_underlying_coins(pool)
        actual_output = []
        for i in range(len(underlying_coins)):

            if underlying_coins[i] == ape.utils.ZERO_ADDRESS:
                actual_output.append(0)
                continue

            try:
                token_contract = VyperContract(underlying_coins[i])
                actual_output.append(token_contract.decimals())
            except ape.exceptions.ChainError:
                pytest.skip("Unverified contract. Skipping test.")
            except ape.exceptions.SignatureError:
                if (
                    underlying_coins[i]
                    == "0x6810e776880C02933D47DB1b9fc05908e5386b96"
                ):
                    actual_output.append(18)  # Gnosis Token
                else:
                    pytest.skip(
                        "Unable to get decimals due to SignatureError. Skipping test."
                    )
            except AttributeError:
                view_methods = [
                    method.name
                    for method in token_contract.contract_type.view_methods
                ]
                if "decimals" not in view_methods:
                    pytest.skip(
                        f"no decimals() view method on {token_contract.address}"
                    )

        assert actual_output[2] != 0  # there has to be a third coin!
    else:
        actual_output = list(registry.get_decimals(pool))

    for idx, decimals in enumerate(actual_output):
        assert decimals == metaregistry_output[idx]


def test_stable_registry_pools(
    populated_metaregistry, stable_registry_pool, stable_registry
):
    _test_underlying_decimals_getter(
        populated_metaregistry, stable_registry, stable_registry_pool
    )


def test_stable_factory_pools(
    populated_metaregistry, stable_factory_pool, stable_factory
):
    _test_underlying_decimals_getter(
        populated_metaregistry, stable_factory, stable_factory_pool
    )


def test_crypto_registry_pools(
    populated_metaregistry, crypto_registry_pool, crypto_registry
):
    _test_underlying_decimals_getter(
        populated_metaregistry, crypto_registry, crypto_registry_pool
    )


def test_crypto_factory_pools(
    populated_metaregistry, crypto_factory_pool, crypto_factory
):
    _test_underlying_decimals_getter(
        populated_metaregistry, crypto_factory, crypto_factory_pool
    )
