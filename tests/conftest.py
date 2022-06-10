import pytest
from brownie import (
    CryptoFactoryHandler,
    CryptoRegistryHandler,
    MetaRegistry,
    StableFactoryHandler,
    StableRegistryHandler,
    MetaAtomicSynthSwap,
)

from .abis import crypto_factory, crypto_registry, stable_factory, stable_registry
from .utils.constants import ADDRESS_PROVIDER
from brownie_tokens import MintableForkToken


def pytest_addoption(parser):
    parser.addoption(
        "--pools",
        type=int,
        action="store",
        default=0,
        help="Only syncs up to the specified number of pools on each registry",
    )


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


@pytest.fixture(scope="session")
def max_pools(request):
    return request.config.getoption("--pools")


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def metaregistry(owner):
    yield MetaRegistry.deploy(owner, ADDRESS_PROVIDER, {"from": owner})


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(owner, metaregistry):
    handler = StableRegistryHandler.deploy(metaregistry, 0, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(0, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(
    owner, metaregistry, stable_registry_handler
):  # ensure registry fixtures exec order
    handler = StableFactoryHandler.deploy(metaregistry, 3, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(3, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(owner, metaregistry, stable_factory_handler):
    handler = CryptoRegistryHandler.deploy(metaregistry, 5, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(5, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(owner, metaregistry, crypto_registry_handler):
    handler = CryptoFactoryHandler.deploy(metaregistry, 6, ADDRESS_PROVIDER, {"from": owner})
    metaregistry.add_registry_by_address_provider_id(6, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module")
def registries():
    yield [
        stable_registry(),
        stable_factory(),
        crypto_registry(),
        crypto_factory(),
    ]


# synths
@pytest.fixture(scope="module")
def sUSD():
    yield MintableForkToken("0x57ab1ec28d129707052df4df418d58a2d46d5f51")


@pytest.fixture(scope="module")
def sBTC():
    yield MintableForkToken("0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6")


@pytest.fixture(scope="module")
def sETH():
    yield MintableForkToken("0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb")


@pytest.fixture(scope="module")
def sEUR():
    yield MintableForkToken("0xD71eCFF9342A5Ced620049e616c5035F1dB98620")


@pytest.fixture(scope="module")
def sLINK():
    yield MintableForkToken("0xbBC455cb4F1B9e4bFC4B73970d360c8f032EfEE6")


# swappable coins
@pytest.fixture(scope="module")
def DAI():
    yield MintableForkToken("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture(scope="module")
def USDT():
    yield MintableForkToken("0xdAC17F958D2ee523a2206206994597C13D831ec7")


@pytest.fixture(scope="module")
def WBTC():
    yield MintableForkToken("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")


@pytest.fixture(scope="module")
def LINK():
    yield MintableForkToken("0x514910771AF9Ca656af840dff83E8264EcF986CA")


# curve pools
@pytest.fixture(scope="module")
def curve_susd(Contract):
    yield Contract("0xA5407eAE9Ba41422680e2e00537571bcC53efBfD")


@pytest.fixture(scope="module")
def curve_slink(Contract):
    yield Contract("0xF178C0b5Bb7e7aBF4e12A4838C7b7c5bA2C623c0")


@pytest.fixture(scope="module")
def curve_sbtc(Contract):
    yield Contract("0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714")


@pytest.fixture(scope="module")
def curve_seth(Contract):
    yield Contract("0xc5424b857f758e906013f3555dad202e4bdb4567")


@pytest.fixture(scope="module")
def curve_seur(Contract):
    yield Contract("0x0Ce6a5fF5217e38315f87032CF90686C96627CAA")


@pytest.fixture(scope="module")
def tracking_code():
    # from synthetix affiliate program:
    yield "0x534e582e4c494e4b000000000000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def atomic_swap(alice, metaregistry, tracking_code):
    yield MetaAtomicSynthSwap.deploy(tracking_code, metaregistry, {"from": alice})


@pytest.fixture(scope="module")
def add_atomic_swap_synths(
    alice,
    atomic_swap,
    sUSD,
    sBTC,
    sETH,
    sEUR,
    sLINK,
    curve_susd,
    curve_sbtc,
    curve_seth,
    curve_seur,
    curve_slink,
):
    atomic_swap.add_synth(sUSD, curve_susd, {"from": alice})
    atomic_swap.add_synth(sBTC, curve_sbtc, {"from": alice})
    atomic_swap.add_synth(sETH, curve_seth, {"from": alice})
    atomic_swap.add_synth(sEUR, curve_seur, {"from": alice})
    atomic_swap.add_synth(sLINK, curve_slink, {"from": alice})
