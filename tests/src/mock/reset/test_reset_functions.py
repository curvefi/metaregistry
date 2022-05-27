import brownie
from brownie import ZERO_ADDRESS

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


def test_reset_registry_wrong_index(fn_isolation, metaregistry_mock, alice, owner):
    with brownie.reverts():
        tx = metaregistry_mock.reset_registry(10, {"from": owner})
        tx.revert_msg == "dev: unknown registry"


def test_reset_registry(
    fn_isolation, metaregistry_mock, crypto_factory, euro_pool, toke_pool, owner
):
    # stable registry pools
    assert metaregistry_mock.pool_to_registry(ALUSD_METAPOOL)[0] > 0
    assert metaregistry_mock.pool_to_registry(STETH_POOL)[0] > 0
    assert metaregistry_mock.pool_to_registry(TRIPOOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(TRIPOOL_LPTOKEN) != ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(MIM_METAPOOL) != ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(STETH_POOL_LPTOKEN) != ZERO_ADDRESS
    # stable factory pool
    assert metaregistry_mock.pool_to_registry(euro_pool)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(euro_pool) != ZERO_ADDRESS
    # crypto factroy
    assert metaregistry_mock.pool_to_registry(toke_pool)[0] > 0
    # crypto registry
    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) != ZERO_ADDRESS

    metaregistry_mock.reset_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, {"from": owner})

    assert metaregistry_mock.pool_to_registry(ALUSD_METAPOOL)[0] == 0
    assert metaregistry_mock.pool_to_registry(STETH_POOL)[0] == 0
    assert metaregistry_mock.pool_to_registry(TRIPOOL)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(TRIPOOL_LPTOKEN) == ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(MIM_METAPOOL) == ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(STETH_POOL_LPTOKEN) == ZERO_ADDRESS

    assert metaregistry_mock.pool_to_registry(euro_pool)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(euro_pool) != ZERO_ADDRESS

    assert metaregistry_mock.pool_to_registry(toke_pool)[0] > 0

    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) != ZERO_ADDRESS

    metaregistry_mock.reset_registry(METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX, {"from": owner})

    assert metaregistry_mock.pool_to_registry(euro_pool)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(euro_pool) == ZERO_ADDRESS

    metaregistry_mock.reset_registry(METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX, {"from": owner})

    assert metaregistry_mock.pool_to_registry(toke_pool)[0] == 0

    metaregistry_mock.reset_registry(METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX, {"from": owner})
    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) == ZERO_ADDRESS


def test_reset(fn_isolation, metaregistry_mock, crypto_factory, euro_pool, toke_pool, owner):
    # stable registry pools
    assert metaregistry_mock.pool_to_registry(ALUSD_METAPOOL)[0] > 0
    assert metaregistry_mock.pool_to_registry(STETH_POOL)[0] > 0
    assert metaregistry_mock.pool_to_registry(TRIPOOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(TRIPOOL_LPTOKEN) != ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(MIM_METAPOOL) != ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(STETH_POOL_LPTOKEN) != ZERO_ADDRESS
    # stable factory pool
    assert metaregistry_mock.pool_to_registry(euro_pool)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(euro_pool) != ZERO_ADDRESS
    # crypto factroy
    assert metaregistry_mock.pool_to_registry(toke_pool)[0] > 0
    # crypto registry
    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) != ZERO_ADDRESS

    metaregistry_mock.reset({"from": owner})

    assert metaregistry_mock.pool_to_registry(ALUSD_METAPOOL)[0] == 0
    assert metaregistry_mock.pool_to_registry(STETH_POOL)[0] == 0
    assert metaregistry_mock.pool_to_registry(TRIPOOL)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(TRIPOOL_LPTOKEN) == ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(MIM_METAPOOL) == ZERO_ADDRESS
    assert metaregistry_mock.get_pool_from_lp_token(STETH_POOL_LPTOKEN) == ZERO_ADDRESS
    assert metaregistry_mock.pool_to_registry(euro_pool)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(euro_pool) == ZERO_ADDRESS
    assert metaregistry_mock.pool_to_registry(toke_pool)[0] == 0
    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) == ZERO_ADDRESS


def test_remove_pool(fn_isolation, metaregistry_mock, crypto_factory, euro_pool, toke_pool, owner):
    # stable registry pools
    assert metaregistry_mock.pool_to_registry(ALUSD_METAPOOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(ALUSD_METAPOOL) != ZERO_ADDRESS
    # stable factory pool
    assert metaregistry_mock.pool_to_registry(euro_pool)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(euro_pool) != ZERO_ADDRESS
    # crypto factroy
    assert metaregistry_mock.pool_to_registry(toke_pool)[0] > 0
    # crypto registry
    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] > 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) != ZERO_ADDRESS

    metaregistry_mock.remove_pool(ALUSD_METAPOOL, {"from": owner})

    assert metaregistry_mock.pool_to_registry(ALUSD_METAPOOL)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(ALUSD_METAPOOL) == ZERO_ADDRESS

    # can't remove factory pools
    with brownie.reverts():
        metaregistry_mock.remove_pool(euro_pool, {"from": owner})

    with brownie.reverts():
        metaregistry_mock.remove_pool(toke_pool, {"from": owner})

    metaregistry_mock.remove_pool(TRICRYPTO_POOL, {"from": owner})

    assert metaregistry_mock.pool_to_registry(TRICRYPTO_POOL)[0] == 0
    assert metaregistry_mock.get_pool_from_lp_token(TRICRYPTO_POOL_LP_TOKEN) == ZERO_ADDRESS
