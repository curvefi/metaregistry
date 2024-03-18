import boa
import pytest


@pytest.fixture(scope="session")
def erc20_deployer():
    return boa.load_partial("contracts/mocks/ERC20.vy")


@pytest.fixture(scope="session")
def erc4626_deployer():
    return boa.load_partial("contracts/mocks/ERC4626.vy")


@pytest.fixture()
def usdc(erc20_deployer):
    return erc20_deployer.deploy("USDC", "USDC", 6)


@pytest.fixture()
def usdt(erc20_deployer):
    return erc20_deployer.deploy("USDT", "USDT", 6)


@pytest.fixture()
def crvusd(erc20_deployer):
    return erc20_deployer.deploy("crvUSD", "crvUSD", 18)


@pytest.fixture()
def sdai(erc4626):
    return erc4626_deployer.deploy("sDAI", "sDAI", 18, 1056565529321686702)


@pytest.fixture()
def base_pool_coins(usdc, usdt, crvusd):
    return [usdc, usdt, crvusd]


@pytest.fixture()
def tricrypto_ng_pool_coins(crvusd, wbtc, weth):
    return [crvusd, wbtc, weth]


@pytest.fixture()
def twocrypto_ng_pool_coins(crvusd, weth):
    return [crvusd, weth]


@pytest.fixture()
def weth(erc20_deployer):
    return erc20_deployer.deploy("WETH", "WETH", 18)


@pytest.fixture()
def wbtc(erc20_deployer):
    return erc20_deployer.deploy("WBTC", "WBTC", 8)
