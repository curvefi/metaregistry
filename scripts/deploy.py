import click
from ape import project
from ape.cli import NetworkBoundCommand, account_option, network_option
from eth_abi import encode

ADDRESS_PROVIDER = "0x0000000022D53366457F9d5E68Ec105046FC4383"
STABLE_REGISTRY_ADDRESS = "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5"
STABLE_FACTORY_ADDRESS = "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
CRYPTO_REGISTRY_ADDRESS = ""  # left blank because a new one gets deployed
CRYPTO_FACTORY_ADDRESS = "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99"


@click.group(short_help="Deploy the project")
def cli():
    pass


@cli.command(cls=NetworkBoundCommand)
@network_option()
@account_option()
def main(network, account):

    # deploy basepool registry:
    base_pool_registry = account.deploy(project.BasePoolRegistry)

    # deploy crypto registry:
    print(
        "Crypto Registry constructor arguments: ",
        encode(["address", "address"], [ADDRESS_PROVIDER, base_pool_registry]),
    )
    crypto_registry = account.deploy(
        project.CryptoRegistryV1,
        ADDRESS_PROVIDER,
        base_pool_registry,
    )

    # deploy stable registry handler:
    print(
        "Stable Registry Handler constructor arguments: ",
        encode(["address"], [STABLE_REGISTRY_ADDRESS]).hex(),
    )
    account.deploy(project.StableRegistryHandler, STABLE_REGISTRY_ADDRESS)

    # deploy stable factory handler:
    print(
        "Stable Factory Handler constructor arguments: ",
        encode(["address", "address"], [STABLE_FACTORY_ADDRESS, base_pool_registry]).hex(),
    )
    account.deploy(project.StableFactoryHandler, STABLE_FACTORY_ADDRESS, base_pool_registry)

    # deploy crypto registry handler:
    print(
        "Crypto Registry Handler constructor arguments: ",
        encode(["address"], [crypto_registry]).hex(),
    )
    account.deploy(project.CryptoRegistryHandler, crypto_registry)

    # deploy crypto factory handler:
    print(
        "Crypto Factory Handler constructor arguments: ",
        encode(["address", "address"], [CRYPTO_FACTORY_ADDRESS, base_pool_registry]).hex(),
    )
    account.deploy(project.CryptoFactoryHandler, CRYPTO_FACTORY_ADDRESS, base_pool_registry)

    # deploy metaregistry:
    print("MetaRegistry constructor arguments: ", encode(["address"], [ADDRESS_PROVIDER]).hex())
    account.deploy(project.MetaRegistry, ADDRESS_PROVIDER)
