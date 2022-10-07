import sys

import click
from ape import accounts, project
from ape.cli import NetworkBoundCommand, account_option, network_option
from ape.utils import ZERO_ADDRESS
from rich.console import Console as RichConsole

RICH_CONSOLE = RichConsole(file=sys.stdout)

ADDRESS_PROVIDER = "0x0000000022D53366457F9d5E68Ec105046FC4383"
BASE_POOLS = {
    "tripool": {
        "pool": "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
        "lp_token": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
        "num_coins": 3,
        "is_legacy": False,
        "is_lending": False,
        "is_v2": False,
    },
    "fraxusdc": {
        "pool": "0xdcef968d416a41cdac0ed8702fac8128a64241a2",
        "lp_token": "0x3175df0976dfa876431c2e9ee6bc45b65d3473cc",
        "num_coins": 2,
        "is_legacy": False,
        "is_lending": False,
        "is_v2": False,
    },
    "sbtc": {
        "pool": "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714",
        "lp_token": "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
        "num_coins": 3,
        "is_legacy": True,
        "is_lending": False,
        "is_v2": False,
    },
}
CRYPTO_REGISTRY_POOLS = {
    "tricrypto2": {
        "pool": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",
        "lp_token": "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
        "gauge": "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168",
        "zap": "0x3993d34e7e99Abf6B6f367309975d1360222D446",
        "num_coins": 3,
        "name": "tricrypto2",
        "base_pool": ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    },
    "eurt3crv": {
        "pool": "0x9838eccc42659fa8aa7daf2ad134b53984c9427b",
        "lp_token": "0x3b6831c0077a1e44ed0a21841c3bc4dc11bce833",
        "gauge": "0x4Fd86Ce7Ecea88F7E0aA78DC12625996Fb3a04bC",
        "zap": "0x5D0F47B32fDd343BfA74cE221808e2abE4A53827",
        "num_coins": 2,
        "name": "eurtusd",
        "base_pool": BASE_POOLS["tripool"]["pool"],
        "has_positive_rebasing_tokens": False,
    },
    "eursusdc": {
        "pool": "0x98a7F18d4E56Cfe84E3D081B40001B3d5bD3eB8B",
        "lp_token": "0x3D229E1B4faab62F621eF2F6A610961f7BD7b23B",
        "gauge": "0x65CA7Dc5CB661fC58De57B1E1aF404649a27AD35",
        "zap": ZERO_ADDRESS,
        "num_coins": 2,
        "name": "eursusd",
        "base_pool": ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    },
    "crveth": {
        "pool": "0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511",
        "lp_token": "0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d",
        "gauge": "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6",
        "zap": ZERO_ADDRESS,
        "num_coins": 2,
        "name": "crveth",
        "base_pool": ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    },
    "cvxeth": {
        "pool": "0xB576491F1E6e5E62f1d8F26062Ee822B40B0E0d4",
        "lp_token": "0x3A283D9c08E8b55966afb64C515f5143cf907611",
        "gauge": "0x7E1444BA99dcdFfE8fBdb42C02F0005D14f13BE1",
        "zap": ZERO_ADDRESS,
        "num_coins": 2,
        "name": "cvxeth",
        "base_pool": ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    },
    "xaut3crv": {
        "pool": "0xAdCFcf9894335dC340f6Cd182aFA45999F45Fc44",
        "lp_token": "0x8484673cA7BfF40F82B041916881aeA15ee84834",
        "gauge": "0x1B3E14157ED33F60668f2103bCd5Db39a1573E5B",
        "zap": "0xc5FA220347375ac4f91f9E4A4AAb362F22801504",
        "num_coins": 2,
        "name": "xaut3crv",
        "base_pool": BASE_POOLS["tripool"]["pool"],
        "has_positive_rebasing_tokens": False,
    },
    "spelleth": {
        "pool": "0x98638FAcf9a3865cd033F36548713183f6996122",
        "lp_token": "0x8282BD15dcA2EA2bDf24163E8f2781B30C43A2ef",
        "gauge": "0x08380a4999Be1a958E2abbA07968d703C7A3027C",
        "zap": ZERO_ADDRESS,
        "num_coins": 2,
        "name": "spelleth",
        "base_pool": ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    },
    "teth": {
        "pool": "0x752eBeb79963cf0732E9c0fec72a49FD1DEfAEAC",
        "lp_token": "0xCb08717451aaE9EF950a2524E33B6DCaBA60147B",
        "gauge": "0x6070fBD4E608ee5391189E7205d70cc4A274c017",
        "zap": ZERO_ADDRESS,
        "num_coins": 2,
        "name": "teth",
        "base_pool": ZERO_ADDRESS,
        "has_positive_rebasing_tokens": False,
    },
    "eurocusd": {
        "pool": "0xE84f5b1582BA325fDf9cE6B0c1F087ccfC924e54",
        "lp_token": "0x70fc957eb90e37af82acdbd12675699797745f68",
        "gauge": "0x4329c8F09725c0e3b6884C1daB1771bcE17934F9",
        "zap": "0xd446a98f88e1d053d1f64986e3ed083bb1ab7e5a",
        "num_coins": 2,
        "name": "eurocusd",
        "base_pool": BASE_POOLS["tripool"]["pool"],
        "has_positive_rebasing_tokens": False,
    },
}


@click.group(short_help="Deploy the project")
def cli():
    pass


@cli.command(cls=NetworkBoundCommand)
@network_option()
@account_option()
@click.option("--simulate", "-s", type=bool, default=True, help="Simulate deployment")
def main(network, account, simulate):

    total_gas_used = 0

    # admin only: only admin of ADDRESSPROVIDER's proxy admin can do the following:
    address_provider = project.AddressProvider.at(ADDRESS_PROVIDER)
    address_provider_admin = address_provider.admin()
    proxy_admin = project.ProxyAdmin.at(address_provider_admin)

    if simulate:
        account = accounts[proxy_admin.admins(1)]

    # deploy basepool registry:
    base_pool_registry = project.BasePoolRegistry.at("0x425b6511Bc83033545b882bd64F5a6D8F5De3544")

    # populate base pool registry:
    base_pool_index = 0
    for _, data in BASE_POOLS.items():
        call_data = base_pool_registry.add_base_pool.as_transaction(
            data["pool"],
            data["lp_token"],
            data["num_coins"],
            data["is_legacy"],
            data["is_lending"],
            data["is_v2"],
            sender=address_provider_admin,
        ).data

        # add base_pool to registry:
        tx = proxy_admin.execute(base_pool_registry, call_data, sender=account)
        total_gas_used += tx.gas_used

        # check if deployment is correct:
        assert base_pool_registry.base_pool_list(base_pool_index).lower() == data["pool"].lower()
        RICH_CONSOLE.log(
            f"Added base pool [blue]{data['pool']} to base pool registry. "
            f"Gas used: [green]{tx.gas_used}"
        )
        base_pool_index += 1

    crypto_registry = project.CryptoRegistryV1.at("0xAe917125d629DC0AbF8702793D1E911728DE0455")

    # populate crypto registry:
    crypto_pool_index = 0
    for _, pool in CRYPTO_REGISTRY_POOLS.items():
        call_data = crypto_registry.add_pool.as_transaction(
            pool["pool"],
            pool["lp_token"],
            pool["gauge"],
            pool["zap"],
            pool["num_coins"],
            pool["name"],
            pool["base_pool"],
            pool["has_positive_rebasing_tokens"],
            sender=address_provider_admin,
        ).data

        # add pool to registry:
        tx = proxy_admin.execute(crypto_registry, call_data, sender=account)
        total_gas_used += tx.gas_used

        # check if deployment is correct:
        assert crypto_registry.pool_list(crypto_pool_index).lower() == pool["pool"].lower()
        RICH_CONSOLE.log(
            f"Added pool [blue]{pool['pool']} to crypto registry. "
            f"Gas used: [green]{tx.gas_used}"
        )
        crypto_pool_index += 1

    # registry handlers:
    stable_registry_handler = project.StableRegistryHandler.at(
        "0x46a8a9CF4Fc8e99EC3A14558ACABC1D93A27de68"
    )
    stable_factory_handler = project.StableFactoryHandler.at(
        "0xF9b71067A1Bb1258F2155359e8B22090612870FF"
    )
    crypto_registry_handler = project.CryptoRegistryHandler.at(
        "0xAB09Bd46eBb782da7a61F336b9376BcB3D35B2e4"
    )
    crypto_factory_handler = project.CryptoFactoryHandler.at(
        "0x23544454b2b6cdb62ddd4f402c23e7bd0e50656c"
    )

    registry_handlers = [
        stable_registry_handler,
        stable_factory_handler,
        crypto_registry_handler,
        crypto_factory_handler,
    ]

    # metaregistry:
    metaregistry = project.MetaRegistry.at("0x8764ADd5e7008ac9a1F44f2664930e8c8fdDc095")

    # populate metaregistry:
    registry_handler_index = 0
    for registry_handler in registry_handlers:
        call_data = metaregistry.add_registry_handler.as_transaction(
            registry_handler.address, sender=address_provider_admin
        ).data

        # add registry handler to metaregistry:
        tx = proxy_admin.execute(metaregistry, call_data, sender=account)
        total_gas_used += tx.gas_used

        # check if deployment is correct:
        assert (
            metaregistry.get_registry(registry_handler_index).lower()
            == registry_handler.address.lower()
        )
        RICH_CONSOLE.log(
            f"Added registry handler [blue]{registry_handler.address} to metaregistry. "
            f"Gas used: [green]{tx.gas_used}"
        )
        registry_handler_index += 1

    # add metaregistry to address provider:
    max_id = address_provider.max_id()
    metaregistry_description = "Metaregistry"
    call_data = address_provider.add_new_id.as_transaction(
        metaregistry.address, metaregistry_description, sender=address_provider_admin
    ).data
    tx = proxy_admin.execute(address_provider.address, call_data, sender=account)
    total_gas_used += tx.gas_used

    # check if adding metaregistry was done properly:
    new_max_id = address_provider.max_id()
    assert new_max_id > max_id
    assert address_provider.get_address(new_max_id).lower() == metaregistry.address.lower()
    RICH_CONSOLE.log(
        f"Added Metaregistry [blue]{metaregistry.address} to AddressProvider. "
        f"Gas used: [green]{tx.gas_used}"
    )
    RICH_CONSOLE.log(f"Deployment complete! Total gas used: [green]{total_gas_used}")
