from typing import Callable
import ape
import pytest


@pytest.fixture(scope="module")
def curve_pool() -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return ape.project.interfaces_folder.CurvePool.at(_pool)

    return _initialise


@pytest.fixture(scope="module")
def curve_pool_v2() -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return ape.project.interfaces_folder.CurvePoolV2.at(_pool)

    return _initialise


@pytest.fixture(scope="module")
def liquidity_gauge() -> Callable:
    def _initialise(_gauge: str) -> ape.Contract:
        return ape.project.interfaces_folder.LiquidityGauge.at(_gauge)

    return _initialise


@pytest.fixture(scope="module", autouse=True)
def registry_pool_index_iterator(registries, handlers):

    pool_count = [registry.pool_count() for registry in registries]
    registry_indices = range(len(registries))

    iterable = []
    for registry_id in registry_indices:

        registry = registries[registry_id]
        registry_handler = handlers[registry_id]

        for pool_index in range(pool_count[registry_id]):

            pool = registry.pool_list(pool_index)
            iterable.append((registry_id, registry_handler, registry, pool))

    return iterable
