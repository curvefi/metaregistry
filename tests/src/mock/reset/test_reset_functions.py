import brownie
from brownie import ZERO_ADDRESS

from ...utils.constants import (
    DAI,
    ETH,
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
    agEUR,
    alUSD,
    sEUR,
    stETH,
)


def test_reset_registry_wrong_index(fn_isolation, metaregistry_mock, alice, owner):
    with brownie.reverts():
        tx = metaregistry_mock.reset_registry(10, {"from": owner})
        tx.revert_msg == "dev: unknown registry"


def test_reset_registry(fn_isolation, metaregistry_mock, owner):
    # reth registry pool
    assert metaregistry_mock.find_pool_for_coins(ETH, stETH, 0) != ZERO_ADDRESS
    # alusd registry metapool
    assert metaregistry_mock.find_pool_for_coins(alUSD, DAI, 0) != ZERO_ADDRESS
    # ageur factory pool
    assert metaregistry_mock.find_pool_for_coins(sEUR, agEUR, 0) != ZERO_ADDRESS

    metaregistry_mock.reset_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX)

    assert metaregistry_mock.find_pool_for_coins(sEUR, agEUR, 0) != ZERO_ADDRESS
    assert metaregistry_mock.find_pool_for_coins(ETH, stETH, 0) == ZERO_ADDRESS
    assert metaregistry_mock.find_pool_for_coins(alUSD, DAI, 0) == ZERO_ADDRESS

    metaregistry_mock.reset_registry(METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX)

    assert metaregistry_mock.find_pool_for_coins(sEUR, agEUR, 0) == ZERO_ADDRESS
