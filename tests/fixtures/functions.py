from typing import Callable

import pytest
from boa.vyper.contract import VyperContract

from tests.utils import get_deployed_contract


# ---- Factories ----


@pytest.fixture(scope="module")
def curve_pool(project) -> Callable:
    def _initialise(_pool: str) -> VyperContract:
        return get_deployed_contract('CurvePool', _pool)

    return _initialise


@pytest.fixture(scope="module")
def curve_pool_v2(project) -> Callable:
    def _initialise(_pool: str) -> VyperContract:
        return get_deployed_contract('CurvePoolV2', _pool)

    return _initialise


@pytest.fixture(scope="module")
def liquidity_gauge(project) -> Callable:
    def _initialise(_gauge: str) -> VyperContract:
        return get_deployed_contract('LiquidityGauge', _gauge)

    return _initialise
