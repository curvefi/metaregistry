from typing import Callable

import pytest
from boa.vyper.contract import VyperContract

from scripts.deployment_utils import get_deployed_contract

# ---- Factories ----


@pytest.fixture(scope="module")
def curve_pool() -> Callable:
    def _initialise(_pool: str) -> VyperContract:
        return get_deployed_contract("CurvePool", _pool)

    return _initialise


@pytest.fixture(scope="module")
def curve_pool_v2() -> Callable:
    def _initialise(_pool: str) -> VyperContract:
        return get_deployed_contract("CurvePoolV2", _pool)

    return _initialise


@pytest.fixture(scope="module")
def liquidity_gauge() -> Callable:
    def _initialise(_gauge: str) -> VyperContract:
        return get_deployed_contract("LiquidityGauge", _gauge)

    return _initialise
