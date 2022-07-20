import ape
import pytest


@pytest.fixture(scope="module")
def base_pools():

    tripool = {
        "pool": "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
        "lp_token": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
        "num_coins": 3,
        "is_legacy": False,
        "is_lending": False,
        "is_v2": False,
    }

    fraxusdc = {
        "pool": "0xdcef968d416a41cdac0ed8702fac8128a64241a2",
        "lp_token": "0x3175df0976dfa876431c2e9ee6bc45b65d3473cc",
        "num_coins": 2,
        "is_legacy": False,
        "is_lending": False,
        "is_v2": False,
    }

    sbtc = {
        "pool": "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714",
        "lp_token": "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
        "num_coins": 3,
        "is_legacy": True,
        "is_lending": False,
        "is_v2": False,
    }

    return {"tripool": tripool, "fraxusdc": fraxusdc, "sbtc": sbtc}


@pytest.fixture(scope="module")
def crypto_registry_pools(base_pools):

    tricrypto2 = {
        "pool": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",
        "lp_token": "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
        "gauge": "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168",
        "zap": "0x3993d34e7e99Abf6B6f367309975d1360222D446",
        "num_coins": 3,
        "name": "tricrypto2",
        "base_pool": ape.utils.ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    }

    eurt3crv = {
        "pool": "0x9838eccc42659fa8aa7daf2ad134b53984c9427b",
        "lp_token": "0x3b6831c0077a1e44ed0a21841c3bc4dc11bce833",
        "gauge": "0x4Fd86Ce7Ecea88F7E0aA78DC12625996Fb3a04bC",
        "zap": "0x5D0F47B32fDd343BfA74cE221808e2abE4A53827",
        "num_coins": 2,
        "name": "eurtusd",
        "base_pool": base_pools["tripool"]["pool"],
        "has_positive_rebasing_tokens": False,
    }

    eursusdc = {
        "pool": "0x98a7F18d4E56Cfe84E3D081B40001B3d5bD3eB8B",
        "lp_token": "0x3D229E1B4faab62F621eF2F6A610961f7BD7b23B",
        "gauge": "0x65CA7Dc5CB661fC58De57B1E1aF404649a27AD35",
        "zap": ape.utils.ZERO_ADDRESS,
        "num_coins": 2,
        "name": "eursusd",
        "base_pool": ape.utils.ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    }

    crveth = {
        "pool": "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511",
        "lp_token": "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d",
        "gauge": "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6",
        "zap": ape.utils.ZERO_ADDRESS,
        "num_coins": 2,
        "name": "crveth",
        "base_pool": ape.utils.ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    }

    cvxeth = {
        "pool": "0xB576491F1E6e5E62f1d8F26062Ee822B40B0E0d4",
        "lp_token": "0x3A283D9c08E8b55966afb64C515f5143cf907611",
        "gauge": "0x7E1444BA99dcdFfE8fBdb42C02F0005D14f13BE1",
        "zap": ape.utils.ZERO_ADDRESS,
        "num_coins": 2,
        "name": "cvxeth",
        "base_pool": ape.utils.ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    }

    xaut3crv = {
        "pool": "0xAdCFcf9894335dC340f6Cd182aFA45999F45Fc44",
        "lp_token": "0x8484673cA7BfF40F82B041916881aeA15ee84834",
        "gauge": "0x1B3E14157ED33F60668f2103bCd5Db39a1573E5B",
        "zap": "0xc5FA220347375ac4f91f9E4A4AAb362F22801504",
        "num_coins": 2,
        "name": "xaut3crv",
        "base_pool": base_pools["tripool"]["pool"],
        "has_positive_rebasing_tokens": False,
    }

    spelleth = {
        "pool": "0x98638FAcf9a3865cd033F36548713183f6996122",
        "lp_token": "0x8282BD15dcA2EA2bDf24163E8f2781B30C43A2ef",
        "gauge": "0x08380a4999Be1a958E2abbA07968d703C7A3027C",
        "zap": ape.utils.ZERO_ADDRESS,
        "num_coins": 2,
        "name": "spelleth",
        "base_pool": ape.utils.ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    }

    teth = {
        "pool": "0x752eBeb79963cf0732E9c0fec72a49FD1DEfAEAC",
        "lp_token": "0xCb08717451aaE9EF950a2524E33B6DCaBA60147B",
        "gauge": "0x6070fBD4E608ee5391189E7205d70cc4A274c017",
        "zap": ape.utils.ZERO_ADDRESS,
        "num_coins": 2,
        "name": "teth",
        "base_pool": ape.utils.ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    }

    return {
        "tricrypto2": tricrypto2,
        "eurt3crv": eurt3crv,
        "eursusdc": eursusdc,
        "crveth": crveth,
        "cvxeth": cvxeth,
        "xaut3crv": xaut3crv,
        "spelleth": spelleth,
        "teth": teth,
    }


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
def crypto_token_implementation():
    return "0xdc892358d55d5ae1ec47a531130d62151eba36e5"


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
