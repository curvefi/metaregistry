from typing import Callable

import ape
import pytest

# ---- Factories ----


@pytest.fixture(scope="module")
def curve_pool(CurvePool) -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return CurvePool(_pool)

    return _initialise


@pytest.fixture(scope="module")
def curve_pool_v2(CurvePoolV2) -> Callable:
    def _initialise(_pool: str) -> ape.Contract:
        return CurvePoolV2(_pool)

    return _initialise


@pytest.fixture(scope="module")
def liquidity_gauge(LiquidityGauge) -> Callable:
    def _initialise(_gauge: str) -> ape.Contract:
        return LiquidityGauge(_gauge)

    return _initialise
