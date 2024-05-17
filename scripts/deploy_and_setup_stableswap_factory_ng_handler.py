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

    # deploy basepool registry:
    registry = boa.load(
        "contracts/registry_handlers/ng/CurveStableSwapFactoryNGHandler.vy",
        "0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf",  # stableswap factory ng
    )
    console.log(
        f"Deployed Curve Stableswap Factory Handler to {registry.address}"
    )


if __name__ == "__main__":
    network = "ethereum"
    fork = False

    main(network, fork)
