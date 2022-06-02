import pytest

from ...utils.constants import (
    ALUSD_METAPOOL,
    METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    MIM_METAPOOL,
    STETH_POOL,
    STETH_POOL_LPTOKEN,
    TRICRYPTO_POOL,
    TRICRYPTO_POOL_LP_TOKEN,
    TRIPOOL,
    TRIPOOL_LPTOKEN,
)


@pytest.fixture(scope="module", autouse=True)
def base_sync_setup(
    metaregistry_mock,
    stable_factory,
    euro_pool,
    toke_pool,
    stable_registry,
    crypto_registry,
    crypto_factory,
    alice,
    owner,
):

    stable_registry.add_pool_without_underlying(
        TRIPOOL,
        3,
        TRIPOOL_LPTOKEN,
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        394770,
        0,
        False,
        False,
        "3pool",
    )

    stable_registry.add_metapool(
        ALUSD_METAPOOL,
        2,
        ALUSD_METAPOOL,
        4626,
        "alusd",
        TRIPOOL,
    )

    stable_registry.add_metapool(
        MIM_METAPOOL,
        2,
        MIM_METAPOOL,
        4626,
        "mim",
        TRIPOOL,
    )

    stable_registry.add_pool_without_underlying(
        STETH_POOL,
        2,
        STETH_POOL_LPTOKEN,
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        4626,
        0,
        False,
        False,
        "steth",
    )

    total_pools = stable_registry.pool_count()
    metaregistry_mock.sync_registry(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, total_pools, {"from": owner}
    )

    metaregistry_mock.sync_registry(
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX, total_pools, {"from": owner}
    )

    crypto_registry.add_pool(
        TRICRYPTO_POOL,
        3,
        TRICRYPTO_POOL_LP_TOKEN,
        "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168",
        "0x3993d34e7e99Abf6B6f367309975d1360222D446",
        1181702,
        "tricrypto2",
    )

    metaregistry_mock.sync_registry(METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX, 1, {"from": owner})

    metaregistry_mock.sync_registry(METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX, 1, {"from": owner})
