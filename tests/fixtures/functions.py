from typing import Callable

import ape
import pytest

# ---- Factories ----


@pytest.fixture(scope="module")
def curve_pool(project) -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return project.CurvePool.at(_pool)

    return _initialise


@pytest.fixture(scope="module")
def curve_pool_v2(project) -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return project.CurvePoolV2.at(_pool)

    return _initialise


@pytest.fixture(scope="module")
def liquidity_gauge(project) -> Callable:
    def _initialise(_gauge: str) -> ape.Contract:
        return project.LiquidityGauge.at(_gauge)

    return _initialise
