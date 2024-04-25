# flake8 no-qa E402
# Contract deployed at: 0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98
# Deployed at: Ethereum, Arbitrum, Optimism, Base, Bsc, Polygon,
#              Fantom, Gnosis, Aurora, Celo, Mantle,
#              Linea, Polygon zkEVM, Scroll, Fraxtal, Avalanche, Kava

import os

import boa
from boa.network import NetworkEnv
from eth_account import Account
from rich.console import Console as RichConsole

# sys.path.append("./")
from scripts.address_provider_constants import (
    ADDRESS_PROVIDER_MAPPING,
    addresses,
)

# import sys


FIDDY_DEPLOYER = "0x2d12D0907A388811e3AA855A550F959501d303EE"
ADDRESS_PROVIDER = "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"


def fetch_url(network):
    return os.getenv("DRPC_URL") % (network, os.getenv("DRPC_KEY"))


def main(network, fork):
    """
    Deploy the AddressProvider to the network.
    """

    console = RichConsole()
    if network == "fraxtal":
        network_url = "https://rpc.frax.com"
    elif network == "kava":
        network_url = "https://rpc.ankr.com/kava_evm"
    else:
        network_url = fetch_url(network)

    if not fork:
        # Prodmode
        console.log("Running script in prod mode...")
        boa.set_env(NetworkEnv(network_url))
        boa.env.add_account(Account.from_key(os.environ["FIDDYDEPLOYER"]))

    else:
        # Forkmode
        console.log("Simulation Mode. Writing to mainnet-fork.")
        boa.env.fork(url=network_url)
        boa.env.eoa = FIDDY_DEPLOYER

    address_provider_obj = boa.load_partial("contracts/AddressProviderNG.vy")
    address_provider = address_provider_obj.at(ADDRESS_PROVIDER)

    # set up address provider
    ids = []
    addresses_for_id = []
    descriptions = []
    for id in addresses[network].keys():
        address = addresses[network][id]
        description = ADDRESS_PROVIDER_MAPPING[id]
        existing_id = address_provider.get_id_info(id)
        if existing_id[0].lower() != address.lower():
            console.log(f"Adding {address} for {description} to id: {id} ...")
            ids.append(id)
            addresses_for_id.append(address)
            descriptions.append(description)

        if len(ids) > 20:
            raise

    address_provider.add_new_ids(ids, addresses_for_id, descriptions)


if __name__ == "__main__":
    network = "mantle"
    fork = False

    main(network, fork)
