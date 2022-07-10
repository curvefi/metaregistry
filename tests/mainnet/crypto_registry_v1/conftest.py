from crypt import crypt
import pytest
import brownie

from tests.abis import address_provider
from tests.utils.constants import ETH_DECIMALS


@pytest.fixture(scope="session")
def owner():
    yield address_provider().admin()


@pytest.fixture(scope="module")
def address_provider():
    yield address_provider()


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_v1(CryptoRegistryV1, address_provider, owner):
    crypto_registry = CryptoRegistryV1.deploy(address_provider, {"from": owner})
    assert address_provider.set_address(5, crypto_registry, {"from": owner})
    yield crypto_registry


# ---- basepool fixtures ----


@pytest.fixture(scope="module")
def basepool_token_a(owner):
    yield brownie.ERC20.deploy("BasePool Token A", "BPTA", 6, {"from": owner})


@pytest.fixture(scope="module")
def basepool_token_b(owner):
    yield brownie.ERC20.deploy("BasePool Token B", "BPTB", 18, {"from": owner})


@pytest.fixture(scope="module")
def basepool_token(CurveTokenV5, owner):
    yield CurveTokenV5.deploy("BasePool LP Token", "2BP", {"from": owner})


@pytest.fixture(scope="module")
def basepool(BasePool2Coin, basepool_token_a, basepool_token_b, basepool_token, owner):
    yield BasePool2Coin.deploy(
        owner,
        [basepool_token_a, basepool_token_b],
        basepool_token,
        1000000,
        10000,
        5000,
        {"from": owner},
    )


# ---- cryptopool fixtures ----


@pytest.fixture(scope="module")
def mock_cryptoeth_lp_token(CurveTokenV5, owner):
    yield CurveTokenV5.deploy("Crypto/ETH LP Token", "crv2CryptoETH", {"from": owner})


@pytest.fixture(scope="module")
def mock_cryptobp_lp_token(CurveTokenV5, owner):
    yield CurveTokenV5.deploy("Crypto/BP LP Token", "crv2CryptoBP", {"from": owner})


@pytest.fixture(scope="module")
def mock_coin_a(owner):
    yield brownie.ERC20.deploy("Mock coin A", "MCA", {"from": owner})


@pytest.fixture(scope="module")
def mock_coin_b(owner):
    yield brownie.ERC20.deploy("Mock coin B", "MCB", {"from": owner})


@pytest.fixture(scope="module")
def mock_cryptoeth_pool(CryptoSwap2ETH, mock_cryptoeth_lp_token, mock_coin_a, owner):

    source = CryptoSwap2ETH._build["source"]
    source = source.replace(
        "0x0000000000000000000000000000000000000001", mock_cryptoeth_lp_token.address
    )
    source = source.replace("0x0000000000000000000000000000000000000010", mock_coin_a.address)
    source = source.replace("0x0000000000000000000000000000000000000011", brownie.ETH_ADDRESS)
    source = source.replace("1,#0", str(10 ** (18 - mock_coin_a.decimals())) + ",")
    source = source.replace("1,#1", str(10 ** (18 - ETH_DECIMALS)) + ",")

    deployer = brownie.compile_source(source, vyper_version="0.3.1")

    # values taken from curve-crypto-contract/blob/master/scripts/deploy_*.py
    # we dont really care about the nitty gritty here.
    yield deployer.deploy(
        owner,  # owner
        owner,  # admin_fee_receiver
        5000 * 2**2 * 10000,  # A
        int(1e-4 * 1e18),  # gamma
        int(5e-4 * 1e10),  # mid_fee
        int(45e-4 * 1e10),  # out_fee
        10**10,  # allowed_extra_profit
        int(5e-3 * 1e18),  # fee_gamma
        int(0.55e-5 * 1e18),  # adjustment_step ?
        5 * 10**9,  # admin_fee
        600,  # ma_half_time
        [10, 10],  # price
        {"from": owner},
    )


@pytest.fixture(scope="module")
def mock_crypto_basepool_pair(CryptoSwap2, mock_cryptobp_lp_token, mock_coin_a, owner):

    source = CryptoSwap2._build["source"]
    source = source.replace(
        "0x0000000000000000000000000000000000000001", mock_cryptobp_lp_token.address
    )
    source = source.replace("0x0000000000000000000000000000000000000010", mock_coin_a.address)
    source = source.replace("0x0000000000000000000000000000000000000011", basepool_token)
    source = source.replace("1,#0", str(10 ** (18 - mock_coin_a.decimals())) + ",")
    source = source.replace("1,#1", str(10 ** (18 - basepool_token.decimals())) + ",")

    deployer = brownie.compile_source(source, vyper_version="0.3.3")

    # values taken from curve-crypto-contract/blob/master/scripts/deploy_*.py
    # we dont really care about the nitty gritty here.
    yield deployer.deploy(
        owner,  # owner
        owner,  # admin_fee_receiver
        5000 * 2**2 * 10000,  # A
        int(1e-4 * 1e18),  # gamma
        int(5e-4 * 1e10),  # mid_fee
        int(45e-4 * 1e10),  # out_fee
        10**10,  # allowed_extra_profit
        int(5e-3 * 1e18),  # fee_gamma
        int(0.55e-5 * 1e18),  # adjustment_step ?
        5 * 10**9,  # admin_fee
        600,  # ma_half_time
        [10, 10],  # price
        {"from": owner},
    )


@pytest.fixture(scope="module")
def zap(ZapTwo, mock_crypto_basepool_pair, basepool, owner):
    yield ZapTwo.deploy(mock_crypto_basepool_pair, basepool, {"from": owner})


# ---- Add pools and basepools ----


@pytest.fixture(scope="module")
def registry_with_cryptoeth_pool(
    crypto_registry_v1, mock_cryptoeth_pool, mock_cryptoeth_lp_token, owner
):
    crypto_registry_v1.add_pool(
        mock_cryptoeth_pool,  # _pool
        mock_cryptoeth_lp_token,  # _lp_token
        brownie.ZERO_ADDRESS,  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "Mock CryptoETH Pool",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )
    yield crypto_registry_v1


@pytest.fixture(scope="module")
def registry_with_basepool(
    crypto_registry_v1, basepool, basepool_token, basepool_token_a, basepool_token_b, owner
):
    crypto_registry_v1.add_base_pool(
        basepool,
        basepool_token,
        [basepool_token_a, basepool_token_b],
        "Mock BasePool",
        {"from": owner},
    )
    yield crypto_registry_v1


@pytest.fixture(scope="module")
def registry_with_cryptoeth_pool(
    registry_with_basepool, mock_crypto_basepool_pair, mock_cryptobp_lp_token, zap, basepool, owner
):
    registry_with_basepool.add_pool(
        mock_crypto_basepool_pair,  # _pool
        mock_cryptobp_lp_token,  # _lp_token
        brownie.ZERO_ADDRESS,  # _gauge
        zap,  # _zap
        "Mock CryptoBP Pool",  # _name
        basepool,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )
    yield crypto_registry_v1


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass
