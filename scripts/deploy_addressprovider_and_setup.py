# flake8 no-qa E402
# Contract deployed at: 0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98
# Deployed at: Ethereum, Arbitrum, Optimism, Base, Bsc, Polygon,
#              Fantom, Gnosis, Aurora, Celo, Mantle,
#              Linea, Polygon zkEVM, Scroll, Fraxtal, Avalanche, Kava

import os

import boa
from boa.network import NetworkEnv
from eth_account import Account
from eth_utils import keccak
from rich.console import Console as RichConsole

# import sys
# sys.path.append("./")
from scripts.address_provider_constants import (
    ADDRESS_PROVIDER_MAPPING,
    addresses,
)

FIDDY_DEPLOYER = "0x2d12D0907A388811e3AA855A550F959501d303EE"


def fetch_url(network):
    return os.getenv("DRPC_URL") % (network, os.getenv("DRPC_KEY"))


def get_create2_deployment_address(deployment_bytecode, salt, create2deployer):
    return create2deployer.computeAddress(salt, keccak(deployment_bytecode))


def deploy_via_create2_factory(deployment_bytecode, salt, create2deployer):
    create2deployer.deploy(0, salt, deployment_bytecode)


def main(network, fork, url=""):
    """
    Deploy the AddressProvider to the network.
    """

    console = RichConsole()
    if not url:
        url = fetch_url(network)

    if not fork:
        # Prodmode
        console.log("Running script in prod mode...")
        boa.set_env(NetworkEnv(url))
        boa.env.add_account(Account.from_key(os.environ["FIDDYDEPLOYER"]))

    else:
        # Forkmode
        console.log("Simulation Mode. Writing to mainnet-fork.")
        boa.env.fork(url=url)
        boa.env.eoa = FIDDY_DEPLOYER

    CREATE2DEPLOYER = boa.load_abi("abi/create2deployer.json").at(
        "0x13b0D85CcB8bf860b6b79AF3029fCA081AE9beF2"
    )

    console.log("Deploying AddressProviderNG ...")
    address_provider_obj = boa.load_partial("contracts/AddressProviderNG.vy")
    codehash = keccak(address_provider_obj.compiler_data.bytecode)
    salt = keccak(42069)
    deployment_address = CREATE2DEPLOYER.computeAddress(salt, codehash)
    CREATE2DEPLOYER.deploy(
        0, salt, address_provider_obj.compiler_data.bytecode
    )
    address_provider = address_provider_obj.at(deployment_address)

    # set up address provider
    ids = []
    addresses_for_id = []
    descriptions = []
    for id in addresses[network].keys():
        address = addresses[network][id]
        description = ADDRESS_PROVIDER_MAPPING[id]

        ids.append(id)
        addresses_for_id.append(address)
        descriptions.append(description)

        if len(ids) > 20:
            raise

    console.log("Adding new ids ...")
    address_provider.add_new_ids(ids, addresses_for_id, descriptions)


if __name__ == "__main__":
    network = "xlayer"
    fork = False

    main(network, fork, url="https://xlayerrpc.okx.com")
