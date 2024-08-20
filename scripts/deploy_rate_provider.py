# flake8: noqa

import os
import sys

import boa
from boa.network import NetworkEnv
from eth_account import Account
from rich import console as rich_console

sys.path.append("./")
from scripts.deploy_addressprovider_and_setup import fetch_url
from scripts.legacy_base_pools import base_pools as BASE_POOLS
from scripts.utils.constants import FIDDY_DEPLOYER

console = rich_console.Console()

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ADDRESS_PROVIDER = (
    "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"  # gets replaced for zksync
)


def main(network, fork, url):
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

    address_provider = boa.load_partial("contracts/AddressProviderNG.vy").at(
        ADDRESS_PROVIDER
    )

    console.log("Deploying rate provider ...")
    rate_provider = boa.load(
        "contracts/RateProvider.vy", address_provider.address
    )

    console.log("Adding rate provider to address provider")
    if address_provider.get_address(18) == ZERO_ADDRESS:
        address_provider.add_new_id(
            18, rate_provider.address, "Spot Rate Provider"
        )
    elif address_provider.get_address(18) != rate_provider.address:
        address_provider.update_address(18, rate_provider.address)


if __name__ == "__main__":
    network = "zksync"
    url = ""
    fork = False

    if network == "zksync":
        import boa_zksync

        network_url = "https://mainnet.era.zksync.io"
        ADDRESS_PROVIDER = "0x3934a3bB913E4a44316a89f5a83876B9C63e4F31"
    elif network == "fraxtal":
        network_url = "https://rpc.frax.com"
    elif network == "kava":
        network_url = "https://rpc.ankr.com/kava_evm"
    elif network == "xlayer":
        network_url = "https://xlayerrpc.okx.com"
    elif network == "mantle":
        network_url = "https://rpc.mantle.xyz"
    else:
        network_url = fetch_url(network)

    main(network, fork, network_url)
