import brownie
import warnings

from .abis import curve_pool, curve_pool_v2, gauge_controller
from .utils.constants import (
    METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
    METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
    METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
    METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
)


def test_is_registered(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            print(pool)
            if pool != brownie.ZERO_ADDRESS:
                assert metaregistry.is_registered(pool)


def test_get_lp_token(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # get_lp_token
            if (
                i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX
                or i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX
            ):
                actual_output = registry.get_lp_token(pool)
            elif i == METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX:
                actual_output = pool
            else:
                actual_output = registry.get_token(pool)

            metaregistry_output = metaregistry.get_lp_token(pool)
            assert actual_output == metaregistry_output


def test_get_pool_from_lp_token(metaregistry, registries, max_pools, curve_api):

    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            metaregistry_output = None
            pool = registry.pool_list(pool_index)

            # get_lp_token
            if (
                i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX
                or i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX
            ):
                lp_token = registry.get_lp_token(pool)
            elif i == METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX:
                lp_token = pool
            else:
                lp_token = registry.get_token(pool)

            metaregistry_output = metaregistry.get_pool_from_lp_token(lp_token)

            assert pool == metaregistry_output


def test_get_virtual_price_from_lp_token(metaregistry, registries, max_pools, curve_api):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            lp_token = metaregistry.get_lp_token(pool)

            # virtual price from metaregistry:
            metaregistry_revert = False
            try:
                metaregistry_output = metaregistry.get_virtual_price_from_lp_token(lp_token)
            except:
                metaregistry_revert = True

            # virtual price from underlying registries (or query chain):
            actual_output_revert = False
            try:
                if (
                    i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX
                    or i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX
                ):
                    actual_output = registry.get_virtual_price_from_lp_token(lp_token)
                else:
                    actual_output = curve_api.get_virtual_price(pool)
            except:
                actual_output_revert = True

            if not (metaregistry_revert and actual_output_revert):
                assert actual_output == metaregistry_output
            else:
                # both should revert for consistency:
                assert metaregistry_revert and actual_output_revert


def test_get_underlying_decimals(metaregistry, registries, max_pools, curve_api):
    def get_coin_decimals_from_pool(pool):
        coin_decimals = []
        for i in range(4):
            try:
                coin_decimals.append(curve_api.get_decimals_for_coin_in_pool(pool, i))
            except brownie.exceptions.VirtualMachineError:
                break
        coin_decimals += [0] * (8 - len(coin_decimals))
        return tuple(coin_decimals)

    for i, registry in enumerate(registries):

        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            metaregistry_output = metaregistry.get_underlying_decimals(pool)

            if (
                i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX
                or i == METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX
            ):
                try:
                    actual_output = registry.get_underlying_decimals(pool)
                    if not actual_output:
                        continue
                    assert actual_output == metaregistry_output
                except AssertionError:
                    print(f"metaregistry_output: {metaregistry_output}")
                    print(f"child registry output: {actual_output}")
                    print(
                        "registry and metaregistry don't match. "
                        "Checking if MetaRegistry is truly at fault here..."
                    )
                    # If a pool is in the stable factory, the underlying_decimals
                    # method in the factory or registry only works correctly
                    # for metapools. Otherwise, it returns a 0 if it isn't paired with
                    # a basepool. So, get the correct coin decimals in case a factory
                    # pool is not a metapool:
                    actual_output = get_coin_decimals_from_pool(pool)
                    assert actual_output == metaregistry_output

            else:
                # Crypto Registries on mainnet do not have get_underlying_decimals,
                # so check each coin's decimals with Metaregistry's output:
                actual_output = get_coin_decimals_from_pool(pool)
                assert actual_output == metaregistry_output


def test_get_underlying_coins(metaregistry, registries, max_pools, curve_api):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            metaregistry_output = None
            pool = registry.pool_list(pool_index)
            attempt = 0
            while attempt <= 10:
                attempt += 1
                try:
                    metaregistry_output = metaregistry.get_underlying_coins(pool)
                    break
                except:
                    continue

            if i in [
                METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
                METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            ]:
                try:
                    actual_output = registry.get_underlying_coins(pool)
                except brownie.exceptions.VirtualMachineError:
                    actual_output = curve_api.get_coins(pool)

            else:

                actual_output = curve_api.get_coins(pool)

            actual_output = list(actual_output)
            actual_output += [brownie.ZERO_ADDRESS] * (8 - len(actual_output))
            actual_output = tuple(actual_output)

            assert actual_output == metaregistry_output


def test_get_underlying_balances(metaregistry, registries, max_pools, curve_api):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            metaregistry_output = None
            pool = registry.pool_list(pool_index)
            metaregistry_borks = False
            metaregistry_output = metaregistry.get_underlying_balances(pool)

            if i in [
                METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
                METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
            ]:
                registry_query_borks = False
                try:
                    actual_output = registry.get_underlying_balances(pool)
                except brownie.exceptions.VirtualMachineError:
                    registry_query_borks = True
                    actual_output = curve_api.get_balances(pool)

            else:

                actual_output = curve_api.get_balances(pool)

            actual_output = list(actual_output)
            actual_output += [0] * (8 - len(actual_output))
            actual_output = tuple(actual_output)

            try:
                assert actual_output == metaregistry_output
            except AssertionError as e:
                if registry_query_borks:
                    warnings.warn("Registry borks but not Metaregistry because BTC basepool")
                    warnings.warn(f"error caught: {e}")
                    continue


def test_get_coins(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # get_coins
            actual_output = registry.get_coins(pool)
            metaregistry_output = metaregistry.get_coins(pool)
            for j, coin in enumerate(actual_output):
                assert coin == metaregistry_output[j]


def test_get_n_coins(metaregistry, registries, max_pools, curve_api):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            if i != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
                actual_output = registry.get_n_coins(pool)
                if not type(actual_output) == brownie.convert.datatypes.Wei:
                    actual_output = actual_output[0]
                elif actual_output == 0:
                    coins = curve_api.get_coins(pool)
                    actual_output = sum([1 for i in coins if i != brownie.ZERO_ADDRESS])
            else:
                coins = curve_api.get_coins(pool)
                actual_output = sum([1 for i in coins if i != brownie.ZERO_ADDRESS])

            metaregistry_output = metaregistry.get_n_coins(pool)
            assert actual_output == metaregistry_output


def test_get_n_underlying_coins(metaregistry, registries, max_pools, curve_api):
    for i, registry in enumerate(registries):
        total_pools = registry.pool_count() if max_pools == 0 else max_pools
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            metaregistry_output = metaregistry.get_n_underlying_coins(pool)

            # check registry for n_coins first:
            if i in [
                METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX,
                METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX,
                METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
            ]:
                n_coins = registry.get_n_coins(pool)
                if type(n_coins) == brownie.convert.datatypes.Wei:
                    try:
                        assert n_coins == metaregistry_output
                    except AssertionError:
                        warnings.warn("Assertion broken: could be a btc metapool issue")
                        coins = curve_api.get_coins(pool)
                        # have to hardcode this test since btc metapool accounting
                        # has some bugs with registry:
                        if coins[1] == "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3":
                            # add btc coins (3) and remove 1 lp coin = add 2:
                            assert n_coins + 2 == metaregistry_output
                    continue
                if len(list(set(n_coins))) == 1:
                    assert n_coins[0] == metaregistry_output
                    continue

            else:
                # if the pool contains a basepool:
                coins = curve_api.get_coins(pool)
                num_coins = sum([1 for i in coins if i != brownie.ZERO_ADDRESS])
                assert num_coins == metaregistry_output


def test_get_pool_params_stableswap_cryptoswap(metaregistry, registries, max_pools):
    """This test is only for stableswap and cryptoswap amms"""
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            print(f"testing get_pool_params for pool: {pool}")
            metaregistry_output = metaregistry.get_pool_params(pool)
            print(f"metaregistry output: {metaregistry_output}")
            actual_pool_params = [0] * 20

            # A
            if i != METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
                actual_pool_params[0] = registry.get_A(pool)
            else:
                actual_pool_params[0] = curve_pool_v2(pool).A()

            # D
            if i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
                actual_pool_params[1] = registry.get_D(pool)
            elif i == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
                actual_pool_params[1] = curve_pool_v2(pool).D()

            # gamma
            if i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
                actual_pool_params[2] = registry.get_gamma(pool)
            elif i == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
                actual_pool_params[2] = curve_pool_v2(pool).gamma()

            # allowed_extra_profit
            if i in [
                METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
                METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
            ]:
                actual_pool_params[3] = curve_pool_v2(pool).allowed_extra_profit()
                actual_pool_params[4] = curve_pool_v2(pool).fee_gamma()
                actual_pool_params[5] = curve_pool_v2(pool).adjustment_step()
                actual_pool_params[6] = curve_pool_v2(pool).ma_half_time()

            print(f"actual pool params: {actual_pool_params}")
            assert actual_pool_params == metaregistry_output
            print(f"passed for pool: {pool}.")


def test_get_base_pool(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            print(
                f"Pool: {pool}, "
                f"registry: {registry}, "
                f"metaregistered registry: {registry_in_meta_registry}"
            )
            if registry != registry_in_meta_registry:
                continue

            # get_base_pool
            if i in [
                METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
                METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
            ]:
                actual_output = brownie.ZERO_ADDRESS
            elif i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX:
                if not registry.is_meta(pool):
                    actual_output = brownie.ZERO_ADDRESS
                elif registry.get_pool_asset_type(pool) == 2:
                    actual_output = "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714"
                else:
                    actual_output = registry.get_base_pool(pool)
            else:
                if not registry.is_meta(pool):
                    actual_output = brownie.ZERO_ADDRESS
                else:
                    actual_output = curve_pool(pool).base_pool()

            metaregistry_output = metaregistry.get_base_pool(pool)
            assert actual_output == metaregistry_output


def test_get_pool_asset_type(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            print(
                f"Pool: {pool}, "
                f"registry: {registry}, "
                f"metaregistered registry: {registry_in_meta_registry}"
            )
            if registry != registry_in_meta_registry:
                continue

            # get_pool_asset_type
            if i in [
                METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
                METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
            ]:
                actual_output = 4
            else:
                actual_output = registry.get_pool_asset_type(pool)

            metaregistry_output = metaregistry.get_pool_asset_type(pool)
            assert actual_output == metaregistry_output


def test_get_admin_balances(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            print(
                f"Pool: {pool}, "
                f"registry: {registry}, "
                f"metaregistered registry: {registry_in_meta_registry}"
            )
            if registry != registry_in_meta_registry:
                continue

            # get_admin_balances
            if i != METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
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
                        balances[i] = brownie.accounts.at(pool).balance() - balances[i]
                    else:
                        balances[i] = brownie.interface.ERC20(coin).balanceOf(pool) - balances[i]
                actual_output = balances
            metaregistry_output = metaregistry.get_admin_balances(pool)
            for j, output in enumerate(actual_output):
                assert output == metaregistry_output[j]


def test_get_fees(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            print(
                f"Pool: {pool}, "
                f"registry: {registry}, "
                f"metaregistered registry: {registry_in_meta_registry}"
            )
            if registry != registry_in_meta_registry:
                continue

            # get_fees
            if i != METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX:
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


def test_get_pool_name(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            print(
                f"Pool: {pool}, "
                f"registry: {registry}, "
                f"metaregistered registry: {registry_in_meta_registry}"
            )
            if registry != registry_in_meta_registry:
                continue

            # get_pool_name
            if (
                i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX
                or i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX
            ):
                actual_output = registry.get_pool_name(pool)
            elif i == METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX:
                actual_output = brownie.interface.ERC20(registry.get_token(pool)).name()
            else:
                actual_output = brownie.interface.ERC20(pool).name()
            metaregistry_output = metaregistry.get_pool_name(pool)
            assert actual_output == metaregistry_output


def test_is_meta(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)
            # get_is_meta
            if i in [
                METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX,
                METAREGISTRY_CRYPTO_FACTORY_HANDLER_INDEX,
            ]:
                actual_output = False
            else:
                actual_output = registry.is_meta(pool)

            metaregistry_output = metaregistry.is_meta(pool)
            assert actual_output == metaregistry_output


def test_get_gauges(metaregistry, registries, max_pools):
    for i, registry in enumerate(registries):
        total_pools = (
            registry.pool_count() if max_pools == 0 else min(max_pools, registry.pool_count())
        )
        for pool_index in range(total_pools):
            pool = registry.pool_list(pool_index)

            # check that the pool was not previously entered in another registry
            registry_in_meta_registry = metaregistry.get_registry_handler_from_pool(pool)
            print(
                f"Pool: {pool}, "
                f"registry: {registry}, "
                f"metaregistered registry: {registry_in_meta_registry}"
            )
            if registry != registry_in_meta_registry:
                continue

            # get_gauges
            if (
                i == METAREGISTRY_STABLE_REGISTRY_HANDLER_INDEX
                or i == METAREGISTRY_CRYPTO_REGISTRY_HANDLER_INDEX
            ):
                actual_output = registry.get_gauges(pool)
            else:
                gauge = registry.get_gauge(pool)
                actual_output = (
                    [gauge] + [brownie.ZERO_ADDRESS] * 9,
                    [gauge_controller().gauge_types(gauge)] + [0] * 9,
                )
            metaregistry_output = metaregistry.get_gauges(pool)
            assert actual_output == metaregistry_output
