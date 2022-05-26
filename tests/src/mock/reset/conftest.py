import pytest

from ...utils import deploy_stable_factory_pool
from ...utils.constants import (
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    agEUR,
    sEUR,
)


@pytest.fixture(scope="module", autouse=True)
def base_sync_setup(
    metaregistry_mock,
    stable_factory,
    two_coin_plain_pool_implementation,
    stable_registry,
    alice,
    owner,
):

    stable_registry.add_pool_without_underlying(
        "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
        3,
        "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        394770,
        0,
        False,
        False,
        "3pool",
    )

    stable_registry.add_metapool(
        "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c",
        2,
        "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c",
        4626,
        "alusd",
        "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
    )

    stable_registry.add_metapool(
        "0x5a6A4D54456819380173272A5E8E9B9904BdF41B",
        2,
        "0x5a6A4D54456819380173272A5E8E9B9904BdF41B",
        4626,
        "mim",
        "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
    )

    stable_registry.add_pool_without_underlying(
        "0xF9440930043eb3997fc70e1339dBb11F341de7A8",
        2,
        "0x53a901d48795C58f485cBB38df08FA96a24669D5",
        "0x00000000000000000000000000000000000000000000000000000000e6aa216c",
        4626,
        256,
        True,
        False,
        "reth",
    )

    total_pools = stable_registry.pool_count()
    metaregistry_mock.sync_registry(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, total_pools, {"from": owner}
    )

    deploy_stable_factory_pool(
        stable_factory, two_coin_plain_pool_implementation, sEUR, agEUR, owner
    )
    total_pools = stable_factory.pool_count()
    metaregistry_mock.sync_registry(
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX, total_pools, {"from": owner}
    )
