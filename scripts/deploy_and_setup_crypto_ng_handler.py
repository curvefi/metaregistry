# flake8: noqa

import os
import sys

import boa
from boa.network import NetworkEnv
from eth_account import Account
from rich import console as rich_console

sys.path.append("./")
from scripts.deploy_addressprovider_and_setup import fetch_url
from scripts.utils.constants import FIDDY_DEPLOYER


def main(network: str = "ethereum", fork: bool = True):
    console = rich_console.Console()

    if not fork:
        # Prodmode
        console.log("Running script in prod mode...")
        boa.set_env(NetworkEnv(fetch_url(network)))
        boa.env.add_account(Account.from_key(os.environ["FIDDYDEPLOYER"]))

    else:
        # Forkmode
        console.log("Simulation Mode. Writing to mainnet-fork.")
        boa.env.fork(url=fetch_url(network))
        boa.env.eoa = FIDDY_DEPLOYER

    # deploy handlers:
    registry = boa.load(
        "contracts/registry_handlers/ng/CurveTwocryptoFactoryHandler.vy",
        "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
    )
    registry = boa.load(
        "contracts/registry_handlers/ng/CurveTricryptoFactoryHandler.vy",
        "0x0c0e5f2fF0ff18a3be9b835635039256dC4B4963",
    )
    console.log(f"Deployed Factory Handlers.")


if __name__ == "__main__":
    network = "ethereum"
    fork = False

    main(network, fork)
