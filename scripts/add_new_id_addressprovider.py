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

import sys
sys.path.append("./")

from scripts.address_provider_constants import (
    ADDRESS_PROVIDER_MAPPING,
    addresses,
)

FIDDY_DEPLOYER = "0x2d12D0907A388811e3AA855A550F959501d303EE"
ADDRESS_PROVIDER = (
    "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"  # gets replaced for zksync
)


def fetch_url(network):
    return os.getenv("DRPC_URL") % (network, os.getenv("DRPC_KEY"))


def main(network, fork, url):
    """
    Deploy the AddressProvider to the network.
    """

    console = RichConsole()

    if network == "zksync":
        if not fork:
            boa_zksync.set_zksync_env(url)
            console.log("Prodmode on zksync Era ...")
        else:
            boa_zksync.set_zksync_fork(url)
            console.log("Forkmode on zksync Era ...")

        boa.env.set_eoa(Account.from_key(os.environ["FIDDYDEPLOYER"]))

    else:
        if fork:
            boa.env.fork(url)
            console.log("Forkmode ...")
            boa.env.eoa = FIDDY_DEPLOYER  # set eoa address here
        else:
            console.log("Prodmode ...")
            boa.set_env(NetworkEnv(url))
            boa.env.add_account(Account.from_key(os.environ["FIDDYDEPLOYER"]))

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

        if not address:
            continue

        if (
            existing_id[0].lower()
            == "0x0000000000000000000000000000000000000000"
        ):
            console.log(f"New id {id} at {address} for {description}.")
            ids.append(id)
            addresses_for_id.append(address)
            descriptions.append(description)

        elif existing_id[0].lower() != address.lower():
            console.log(f"Updating id {id} for {description} with {address}.")
            address_provider.update_id(id, address, description)

        if len(ids) > 20:
            raise

    if len(ids) > 0:
        console.log("Adding new IDs to the Address Provider.")
        address_provider.add_new_ids(ids, addresses_for_id, descriptions)

    console.log("Done!")


if __name__ == "__main__":
    network = "zksync"
    url = ""
    fork = False

    if network == "zksync":
        import boa_zksync

        url = "https://mainnet.era.zksync.io"
        ADDRESS_PROVIDER = "0x3934a3bB913E4a44316a89f5a83876B9C63e4F31"
    elif network == "fraxtal":
        network_url = "https://rpc.frax.com"
    elif network == "kava":
        network_url = "https://rpc.ankr.com/kava_evm"
    else:
        network_url = fetch_url(network)

    main(network, fork, url)
