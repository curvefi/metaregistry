from brownie import interface, accounts
from tests.utils.constants import ADDRESS_ZERO
from tests.abis import (
    curve_pool,
    curve_pool_v2,
    gauge_controller,
)


def test_get_coins(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # get_coins
            actual_output = registry.get_coins(pool)
            metaregistry_output = metaregistry.get_coins(pool)
            for j, coin in enumerate(actual_output):
                assert coin == metaregistry_output[j]


def test_get_pool_params_stableswap_cryptoswap(metaregistry, registries, sync_limit):
    """This test is only for stableswap and cryptoswap amms"""
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            print(f"testing get_pool_params for pool: {pool}")
            metaregistry_output = metaregistry.get_pool_params(pool)
            print(f"metaregistry output: {metaregistry_output}")
            actual_pool_params = [0] * 20

            # A
            if i != 2:
                actual_pool_params[0] = registry.get_A(pool)
            else:
                actual_pool_params[0] = curve_pool_v2(pool).A()

            # D
            if i == 3:
                actual_pool_params[1] = registry.get_D(pool)
            elif i == 2:
                actual_pool_params[1] = curve_pool_v2(pool).D()

            # gamma
            if i == 3:
                actual_pool_params[2] = registry.get_gamma(pool)
            elif i == 2:
                actual_pool_params[2] = curve_pool_v2(pool).gamma()

            # allowed_extra_profit
            if i in [2, 3]:
                actual_pool_params[3] = curve_pool_v2(pool).allowed_extra_profit()
                actual_pool_params[4] = curve_pool_v2(pool).fee_gamma()
                actual_pool_params[5] = curve_pool_v2(pool).adjustment_step()
                actual_pool_params[6] = curve_pool_v2(pool).ma_half_time()

            print(f"actual pool params: {actual_pool_params}")
            assert actual_pool_params == metaregistry_output
            print(f"passed for pool: {pool}.")


def test_get_base_pool(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.pool_to_registry(pool)
            print(
                f"Pool: {pool}, registry: {i}, metaregistered registry: {registry_in_meta_registry}"
            )
            if i + 1 != registry_in_meta_registry:
                continue

            # get_base_pool
            if i >= 2:
                actual_output = ADDRESS_ZERO
            elif i == 0:
                if not registry.is_meta(pool):
                    actual_output = ADDRESS_ZERO
                elif registry.get_pool_asset_type(pool) == 2:
                    actual_output = "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714"
                else:
                    actual_output = registry.get_base_pool(pool)
            else:
                if not registry.is_meta(pool):
                    actual_output = ADDRESS_ZERO
                else:
                    actual_output = curve_pool(pool).base_pool()

            metaregistry_output = metaregistry.get_base_pool(pool)
            assert actual_output == metaregistry_output


def test_get_pool_asset_type(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.pool_to_registry(pool)
            print(
                f"Pool: {pool}, registry: {i}, metaregistered registry: {registry_in_meta_registry}"
            )
            if i + 1 != registry_in_meta_registry:
                continue

            # get_pool_asset_type
            if i >= 2:
                actual_output = 4
            else:
                actual_output = registry.get_pool_asset_type(pool)

            metaregistry_output = metaregistry.get_pool_asset_type(pool)
            assert actual_output == metaregistry_output


def test_get_admin_balances(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.pool_to_registry(pool)
            print(
                f"Pool: {pool}, registry: {i}, metaregistered registry: {registry_in_meta_registry}"
            )
            if i + 1 != registry_in_meta_registry:
                continue

            # get_admin_balances
            if i != 2:
                actual_output = registry.get_admin_balances(pool)
            else:
                balances = registry.get_balances(pool)
                coins = registry.get_coins(pool)
                for k in range(2):
                    coin = coins[k]
                    if (
                        coin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
                        or coin == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
                    ):
                        balances[i] = accounts.at(pool).balance() - balances[i]
                    else:
                        balances[i] = (
                            interface.ERC20(coin).balanceOf(pool) - balances[i]
                        )
                actual_output = balances
            metaregistry_output = metaregistry.get_admin_balances(pool)
            for j, output in enumerate(actual_output):
                assert output == metaregistry_output[j]


def test_get_fees(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.pool_to_registry(pool)
            print(
                f"Pool: {pool}, registry: {i}, metaregistered registry: {registry_in_meta_registry}"
            )
            if i + 1 != registry_in_meta_registry:
                continue

            # get_fees
            if i != 2:
                actual_output = registry.get_fees(pool)
            else:
                curve_contract = curve_pool_v2(pool)
                actual_output = [
                    curve_contract.fee(),
                    curve_contract.admin_fee(),
                    curve_contract.mid_fee(),
                    curve_contract.out_fee(),
                ]
            metaregistry_output = metaregistry.get_fees(pool)
            for j, output in enumerate(actual_output):
                assert output == metaregistry_output[j]


def test_get_pool_name(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.pool_to_registry(pool)
            print(
                f"Pool: {pool}, registry: {i}, metaregistered registry: {registry_in_meta_registry}"
            )
            if i + 1 != registry_in_meta_registry:
                continue

            # get_pool_name
            if i == 1 or i == 3:
                actual_output = registry.get_pool_name(pool)
            elif i == 2:
                actual_output = interface.ERC20(registry.get_token(pool)).name()
            else:
                actual_output = interface.ERC20(pool).name()
            metaregistry_output = metaregistry.get_pool_name(pool)
            assert actual_output == metaregistry_output


def test_is_meta(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            # get_is_meta
            if i >= 2:
                actual_output = False
            else:
                actual_output = registry.is_meta(pool)

            metaregistry_output = metaregistry.is_meta(pool)
            assert actual_output == metaregistry_output


def test_get_gauges(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.pool_to_registry(pool)
            print(
                f"Pool: {pool}, registry: {i}, metaregistered registry: {registry_in_meta_registry}"
            )
            if i + 1 != registry_in_meta_registry:
                continue

            # get_gauges
            if i == 1 or i == 3:
                actual_output = registry.get_gauges(pool)
            else:
                gauge = registry.get_gauge(pool)
                actual_output = (
                    [gauge] + [ADDRESS_ZERO] * 9,
                    [gauge_controller().gauge_types(gauge)] + [0] * 9,
                )
            metaregistry_output = metaregistry.get_gauges(pool)
            assert actual_output == metaregistry_output


def test_get_lp_token(metaregistry, registries, sync_limit):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if sync_limit == 0 else sync_limit
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # get_lp_token
            if i == 1 or i == 3:
                actual_output = registry.get_lp_token(pool)
            elif i == 0:
                actual_output = pool
            else:
                actual_output = registry.get_token(pool)

            metaregistry_output = metaregistry.get_lp_token(pool)
            assert actual_output == metaregistry_output
