# flake8: noqa

import os
import sys

import boa
from boa.network import NetworkEnv
from eth_account import Account
from rich import console as rich_console

sys.path.append("./")
from scripts.deploy_addressprovider_and_setup import fetch_url
from scripts.utils.constants import BASE_POOLS, FIDDY_DEPLOYER


def main(network: str = "ethereum", fork: bool = True):
    """
    Deploy the contracts to the network.
    It does the following:
    1. deploys the base pool registry
    2. deploys the crypto registry
    3. deploys the stable registry handler
    4. deploys the stable factory handler
    5. deploys the crypto registry handler
    6. deploys the crypto factory handler
    7. deploys the metaregistry
    """
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
        "contracts/mainnet/registries/BasePoolRegistryNG.vy",
        "0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf",  # stableswap factory ng
    )
    console.log(f"Deployed base pool registry to {registry.address}")

    for _, data in BASE_POOLS.items():
        registry.add_custom_base_pool(
            data["pool"],
            data["lp_token"],
            data["num_coins"],
            data["is_legacy"],
            data["is_lending"],
            data["is_v2"],
        )

        console.log(
            f"Added base pool [blue]{data['pool']} to base pool registry."
        )

    breakpoint()


if __name__ == "__main__":
    network = "ethereum"
    fork = True

    main(network, fork)
