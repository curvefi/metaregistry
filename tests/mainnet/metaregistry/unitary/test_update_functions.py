import brownie

from tests.utils.constants import DAI, METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, TRIPOOL


def test_update_address_provider_not_to_address_zero(metaregistry, owner, fn_isolation):
    with brownie.reverts():
        tx = metaregistry.update_address_provider(brownie.ZERO_ADDRESS, {"from": owner})
        tx.revert_msg == "dev: not to zero"


def test_update_address_provider(fn_isolation, metaregistry, owner):
    metaregistry.update_address_provider(TRIPOOL, {"from": owner})
    assert metaregistry.address_provider() == TRIPOOL


def test_update_registry_handler_invalid_registry(fn_isolation, metaregistry, owner):
    with brownie.reverts():
        metaregistry.update_registry_handler(10, TRIPOOL, {"from": owner})


def test_update_registry_handler(fn_isolation, metaregistry, owner):
    metaregistry.update_registry_handler(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, TRIPOOL, {"from": owner}
    )
    assert metaregistry.get_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX)[2] == TRIPOOL


def test_update_single_registry(fn_isolation, metaregistry, owner):
    metaregistry.update_single_registry(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
        TRIPOOL,
        3,
        TRIPOOL,
        "tripool",
        True,
        {"from": owner},
    )
    assert metaregistry.get_registry(METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX) == (
        TRIPOOL,
        3,
        TRIPOOL,
        "tripool",
        True,
    )


def test_switch_registry_active_status_invalid_registry(fn_isolation, metaregistry, owner):
    with brownie.reverts():
        metaregistry.switch_registry_active_status(10, {"from": owner})


def test_switch_registry_active_status(fn_isolation, metaregistry, owner):
    metaregistry.switch_registry_active_status(
        METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX, {"from": owner}
    )
    with brownie.reverts("no registry"):
        metaregistry.get_coins(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_n_coins(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_n_underlying_coins(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_underlying_coins(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.is_registered(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_decimals(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_underlying_decimals(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_balances(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_underlying_balances(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_lp_token(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_gauges(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.is_meta(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_pool_name(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_fees(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_admin_balances(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_pool_asset_type(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_pool_params(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_base_pool(TRIPOOL)
    with brownie.reverts("no registry"):
        metaregistry.get_coin_indices(TRIPOOL, DAI, DAI)
