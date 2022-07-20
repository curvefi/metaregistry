from typing import Callable

import ape
import pytest

# ---- Factories ----


@pytest.fixture(scope="module")
def curve_pool() -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return ape.project.CurvePool.at(_pool)

    return _initialise


@pytest.fixture(scope="module")
def curve_pool_v2() -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return ape.project.CurvePoolV2.at(_pool)

    return _initialise


@pytest.fixture(scope="module")
def liquidity_gauge() -> Callable:
    def _initialise(_gauge: str) -> ape.Contract:
        return ape.project.LiquidityGauge.at(_gauge)

    return _initialise
