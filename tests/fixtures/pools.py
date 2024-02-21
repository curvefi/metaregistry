import boa
import pytest
from eth.constants import ZERO_ADDRESS


@pytest.fixture()
def stableswap_ng_pool(
    stableswap_ng_deployer, deployer, stableswap_ng_factory, base_pool_coins
):
    pool_size = len(base_pool_coins)
    A = 2000
    fee = 1000000
    method_ids = [b""] * pool_size
    oracles = [ZERO_ADDRESS] * pool_size
    A = 500
    fee = 4000000
    offpeg_fee_multiplier = 20000000000

    with boa.env.prank(deployer):
        ma_exp_time = 866
        implementation_idx = 0
        asset_types = [t.asset_type() for t in base_pool_coins]
        coins = [t.address for t in base_pool_coins]

        pool = stableswap_ng_factory.deploy_plain_pool(
            "ssng",
            "ssng",
            coins,
            A,
            fee,
            offpeg_fee_multiplier,
            ma_exp_time,
            implementation_idx,
            asset_types,
            method_ids,
            oracles,
        )
    return stableswap_ng_deployer.at(pool)


@pytest.fixture()
def base_ng_pool(stableswap_ng_pool):
    return stableswap_ng_pool


@pytest.fixture()
def stableswap_ng_metapool(
    stableswap_ng_factory, stableswap_ng_meta_deployer, base_ng_pool, sdai
):
    A = 2000
    fee = 1000000
    method_id = bytes(b"")
    oracle = ZERO_ADDRESS
    asset_type = 3
    A = 500
    fee = 4000000
    offpeg_fee_multiplier = 20000000000

    pool = stableswap_ng_factory.deploy_metapool(
        base_ng_pool.address,
        "ssngmeta",
        "ssngmeta",
        sdai.address,
        A,
        fee,
        offpeg_fee_multiplier,
        866,
        0,
        asset_type,
        method_id,
        oracle,
    )
    return stableswap_ng_meta_deployer.at(pool)


@pytest.fixture(scope="module")
def tricrypto_ng_pool(
    tricrypto_ng_factory,
    tricrypto_ng_amm_deployer,
    tricrypto_ng_pool_coins,
    deployer,
):
    with boa.env.prank(deployer):
        swap = tricrypto_ng_factory.deploy_pool(
            "Curve.fi crvUSDC-BTC-ETH",
            "tricryptoCRV",
            [coin.address for coin in tricrypto_ng_pool_coins],
            ZERO_ADDRESS,
            0,
            135 * 3**3 * 10000,
            int(7e-5 * 1e18),
            int(4e-4 * 1e10),
            int(4e-3 * 1e10),
            int(0.01 * 1e18),
            2 * 10**12,
            int(0.0015 * 1e18),
            866,
            [47500 * 10**18, 1500 * 10**18],
        )

    return tricrypto_ng_amm_deployer.at(swap)


@pytest.fixture()
def twocrypto_ng_pool(
    twocrypto_ng_factory,
    twocrypto_ng_amm_deployer,
    twocrypto_ng_coins,
    deployer,
):
    with boa.env.prank(deployer):
        swap = twocrypto_ng_factory.deploy_pool(
            "Curve.fi crvUSD<>WETH",
            "crvUSDWETH",
            [coin.address for coin in twocrypto_ng_coins],
            0,
            400000,
            145000000000000,
            26000000,
            45000000,
            230000000000000,
            2000000000000,
            146000000000000,
            866,
            1500 * 10**18,
        )

    return twocrypto_ng_amm_deployer.at(swap)
