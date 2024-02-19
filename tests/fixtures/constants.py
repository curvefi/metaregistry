import pytest

from scripts.utils.constants import BASE_POOLS, CRYPTO_REGISTRY_POOLS


@pytest.fixture(scope="module")
def base_pools():
    return BASE_POOLS


@pytest.fixture(scope="module")
def crypto_registry_pools(base_pools):
    return CRYPTO_REGISTRY_POOLS


@pytest.fixture(scope="module")
def max_coins():
    return 8


# ---- contract addresses ----


@pytest.fixture(scope="module")
def crypto_pool_implementation():
    return "0xa85461afc2deec01bda23b5cd267d51f765fba10"


@pytest.fixture(scope="module")
def crypto_token_implementation():
    return "0xc08550a4cc5333f40e593ecc4c4724808085d304"


@pytest.fixture(scope="module")
def admin_fee_receiver():
    return "0xeCb456EA5365865EbAb8a2661B0c503410e9B347"


@pytest.fixture(scope="module")
def tokens():
    return {
        "eth": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "dai": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "usdc": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "usdt": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "renbtc": "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "sbtc": "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",
        "eurt": "0xC581b735A1688071A1746c968e0798D642EDE491",
    }


@pytest.fixture(scope="module")
def lp_tokens():
    return {
        "cvxFXSFXS-f": "0xF3A43307DcAFa93275993862Aae628fCB50dC768",
        "bveCVX-CVX-f": "0x04c90C198b2eFF55716079bc06d7CCc4aa4d7512",
    }
