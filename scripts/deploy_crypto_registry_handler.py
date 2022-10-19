import click
from ape import project
from ape.cli import NetworkBoundCommand, account_option, network_option
from eth_abi import encode


CRYPTO_REGISTRY_ADDRESS = "0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0"

@click.group(short_help="Deploy the registry handler")
def cli():
    pass


@cli.command(cls=NetworkBoundCommand)
@network_option()
@account_option()
def main(network, account):
    
    print(
        "Crypto Registry Handler constructor arguments: ",
        encode(["address"], [CRYPTO_REGISTRY_ADDRESS]).hex(),
    )
    account.deploy(project.CryptoRegistryHandler, CRYPTO_REGISTRY_ADDRESS)
