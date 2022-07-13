from re import A
import brownie
import pytest

from tests.abis import address_provider, crypto_factory, stable_factory, stable_registry
from tests.utils.constants import DAI, TRIPOOL, TRIPOOL_LPTOKEN, USDC, USDT


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
def owner():
    yield address_provider().admin()


@pytest.fixture(scope="module")
def base_pool_registry(BasePoolRegistry, owner):
    registry = BasePoolRegistry.deploy(address_provider().address, {"from": owner})

    # add 3pool
    tx = registry.add_base_pool(
        TRIPOOL,
        TRIPOOL_LPTOKEN,
        {"from": owner},
    )

    # add fraxusdc pool
    tx = registry.add_base_pool(
        "0xdcef968d416a41cdac0ed8702fac8128a64241a2",
        "0x3175df0976dfa876431c2e9ee6bc45b65d3473cc",
        {"from": owner},
    )

    # add sbtc pool
    tx = registry.add_base_pool(
        "0x7fc77b5c7614e1533320ea6ddc2eb61fa00a9714",
        "0x075b1bb99792c9e1041ba13afef80c91a1e70fb3",
        {"from": owner},
    )

    assert (
        registry.get_base_pool_for_lp_token("0x075b1bb99792c9e1041ba13afef80c91a1e70fb3")
        != brownie.ZERO_ADDRESS
    )

    yield registry


@pytest.fixture(scope="module")
def crypto_registry_v1(CryptoRegistryV1, base_pool_registry, owner):
    yield CryptoRegistryV1.deploy(address_provider().address, base_pool_registry, {"from": owner})


@pytest.fixture(scope="module")
def crypto_registry_updated(crypto_registry_v1, owner):

    # add tricrypto2
    crypto_registry_v1.add_pool(
        "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",  # _pool
        "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",  # _lp_token
        "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168",  # _gauge
        "0x3993d34e7e99Abf6B6f367309975d1360222D446",  # _zap
        "tricrypto2",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add EURT3CRV pool
    crypto_registry_v1.add_pool(
        "0x9838eccc42659fa8aa7daf2ad134b53984c9427b",  # _pool
        "0x3b6831c0077a1e44ed0a21841c3bc4dc11bce833",  # _lp_token
        "0x4Fd86Ce7Ecea88F7E0aA78DC12625996Fb3a04bC",  # _gauge
        "0x5D0F47B32fDd343BfA74cE221808e2abE4A53827",  # _zap
        "eurtusd",  # _name
        TRIPOOL,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add EURSUSDC pool
    crypto_registry_v1.add_pool(
        "0x98a7F18d4E56Cfe84E3D081B40001B3d5bD3eB8B",  # _pool
        "0x3D229E1B4faab62F621eF2F6A610961f7BD7b23B",  # _lp_token
        "0x65CA7Dc5CB661fC58De57B1E1aF404649a27AD35",  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "eursusd",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add crveth pool
    crypto_registry_v1.add_pool(
        "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511",  # _pool
        "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d",  # _lp_token
        "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6",  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "crveth",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add cvxeth pool
    crypto_registry_v1.add_pool(
        "0xB576491F1E6e5E62f1d8F26062Ee822B40B0E0d4",  # _pool
        "0x3A283D9c08E8b55966afb64C515f5143cf907611",  # _lp_token
        "0x7E1444BA99dcdFfE8fBdb42C02F0005D14f13BE1",  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "cvxeth",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add xaut3crv pool
    crypto_registry_v1.add_pool(
        "0xAdCFcf9894335dC340f6Cd182aFA45999F45Fc44",  # _pool
        "0x8484673cA7BfF40F82B041916881aeA15ee84834",  # _lp_token
        "0x1B3E14157ED33F60668f2103bCd5Db39a1573E5B",  # _gauge
        "0xc5FA220347375ac4f91f9E4A4AAb362F22801504",  # _zap
        "xaut3crv",  # _name
        TRIPOOL,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add spelleth pool
    crypto_registry_v1.add_pool(
        "0x98638FAcf9a3865cd033F36548713183f6996122",  # _pool
        "0x8282BD15dcA2EA2bDf24163E8f2781B30C43A2ef",  # _lp_token
        "0x08380a4999Be1a958E2abbA07968d703C7A3027C",  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "spelleth",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    # add teth pool
    crypto_registry_v1.add_pool(
        "0x752eBeb79963cf0732E9c0fec72a49FD1DEfAEAC",  # _pool
        "0xCb08717451aaE9EF950a2524E33B6DCaBA60147B",  # _lp_token
        "0x6070fBD4E608ee5391189E7205d70cc4A274c017",  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "teth",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
        {"from": owner},
    )

    yield crypto_registry_v1


@pytest.fixture(scope="module", autouse=True)
def address_provider_updated(crypto_registry_v1, owner):
    _address_provider = address_provider()
    _address_provider.set_address(5, crypto_registry_v1, {"from": owner})
    yield _address_provider


@pytest.fixture(scope="module")
def metaregistry(MetaRegistry, address_provider_updated, owner):
    yield MetaRegistry.deploy(address_provider_updated, {"from": owner})


@pytest.fixture(scope="module", autouse=True)
def stable_registry_handler(StableRegistryHandler, owner, metaregistry, address_provider_updated):
    handler = StableRegistryHandler.deploy(
        metaregistry, address_provider_updated, 0, {"from": owner}
    )
    metaregistry.add_registry_by_address_provider_id(0, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def stable_factory_handler(
    StableFactoryHandler, owner, metaregistry, address_provider_updated, stable_registry_handler
):  # ensure registry fixtures exec order
    handler = StableFactoryHandler.deploy(
        metaregistry, address_provider_updated, 3, {"from": owner}
    )
    metaregistry.add_registry_by_address_provider_id(3, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_registry_handler(
    CryptoRegistryHandler, owner, metaregistry, address_provider_updated, stable_factory_handler
):
    handler = CryptoRegistryHandler.deploy(
        metaregistry, address_provider_updated, 5, {"from": owner}
    )
    metaregistry.add_registry_by_address_provider_id(5, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module", autouse=True)
def crypto_factory_handler(
    CryptoFactoryHandler,
    owner,
    metaregistry,
    address_provider_updated,
    base_pool_registry,
    crypto_registry_handler,
):
    handler = CryptoFactoryHandler.deploy(
        metaregistry, address_provider_updated, 6, base_pool_registry, {"from": owner}
    )
    metaregistry.add_registry_by_address_provider_id(6, handler, {"from": owner})
    yield handler


@pytest.fixture(scope="module")
def registries(crypto_registry_v1):
    yield [
        stable_registry(),
        stable_factory(),
        crypto_registry_v1,
        crypto_factory(),
    ]


@pytest.fixture(scope="module")
def handlers(
    stable_registry_handler, stable_factory_handler, crypto_registry_handler, crypto_factory_handler
):
    yield [
        stable_registry_handler,
        stable_factory_handler,
        crypto_registry_handler,
        crypto_factory_handler,
    ]


@pytest.fixture(scope="module", autouse=True)
def registry_pool_index_iterator(registries, handlers):

    pool_count = [registry.pool_count() for registry in registries]
    registry_indices = range(len(registries))

    iterable = []
    for registry_id in registry_indices:

        registry = registries[registry_id]
        registry_handler = handlers[registry_id]

        for pool_index in range(pool_count[registry_id]):

            pool = registry.pool_list(pool_index)
            iterable.append((registry_id, registry_handler, registry, pool))

    return iterable
