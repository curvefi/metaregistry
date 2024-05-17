import os
import sys

import boa
from eth_account import Account
from rich.console import Console as RichConsole

sys.path.append("./")

FIDDY_DEPLOYER = ""
ADDRESS_PROVIDER = "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"
GAUGE_TYPE = {
    "arbitrum": 7,
    "optimism": 11,
    "polygon": 2,
    "base": 0,
    "fraxtal": 11,
    "bsc": 12,
    "gnosis": 4,
    "fantom": 1,
    "avalanche": 8,
    "aurora": -1,
    "celo": -1,
    "kava": 9,
    "mantle": -1,
    "linea": -1,
    "scroll": -1,
    "polygon-zkevm": -1,
    "xlayer": -1,
}


def fetch_url(network):
    return os.getenv("DRPC_URL") % (network, os.getenv("DRPC_KEY"))


def main(network, fork, url=""):
    """
    Deploy the AddressProvider to the network.
    """
    assert "ethereum" not in network
    console = RichConsole()
    if not url:
        url = fetch_url(network)

    if not fork:
        # Prodmode
        console.log("Running script in prod mode...")
        boa.set_network_env(url)
        boa.env.add_account(Account.from_key(os.environ["FIDDYDEPLOYER"]))
        boa.env.suppress_debug_tt(True)

    else:
        # Forkmode
        console.log("Simulation Mode. Writing to mainnet-fork.")
        boa.env.fork(url=url)
        boa.env.eoa = FIDDY_DEPLOYER

    address_provider = boa.load_partial("contracts/AddressProviderNG.vy").at(
        ADDRESS_PROVIDER
    )

    # deploy metaregistry
    # console.log("Deploying Metaregistry ...")
    # gauge_factory = address_provider.get_address(20)  # 20 is for Gauge Factory
    # gauge_type = GAUGE_TYPE[network]
    # metaregistry = boa.load("contracts/MetaregistryL2.vy", gauge_factory, gauge_type)
    # console.log(
    #     "Constructor arguments: ",
    #     encode(["address", "int128"], [gauge_factory, gauge_type]).hex(),
    # )

    # xlayer
    metaregistry = boa.load_partial("contracts/MetaregistryL2.vy").at(
        "0x87DD13Dd25a1DBde0E1EdcF5B8Fa6cfff7eABCaD"
    )

    # set up tricrypto ng factory handler
    console.log("Deploy Tricrypto Factory Handler ...")
    tricrypto_ng_factory = address_provider.get_address(11)
    tricrypto_ng_factory_handler = boa.load(
        "contracts/registry_handlers/ng/CurveTricryptoFactoryHandler.vy",
        tricrypto_ng_factory,
    )

    # set up stableswap ng factory handler
    console.log("Deploy Stableswap Factory Handler ...")
    stableswap_ng_factory = address_provider.get_address(12)
    stableswap_ng_factory_handler = boa.load(
        "contracts/registry_handlers/ng/CurveStableSwapFactoryNGHandler.vy",
        stableswap_ng_factory,
    )

    # set up twocrypto ng factory handler
    console.log("Deploy Twocrypto Factory Handler ...")
    twocrypto_ng_factory = address_provider.get_address(13)
    twocrypto_ng_factory_handler = boa.load(
        "contracts/registry_handlers/ng/CurveTwocryptoFactoryHandler.vy",
        twocrypto_ng_factory,
    )

    # Add registry handlers to the metaregistry
    console.log("Add Factory Handlers to Metaregistry ...")
    metaregistry.add_registry_handler(stableswap_ng_factory_handler.address)
    metaregistry.add_registry_handler(twocrypto_ng_factory_handler.address)
    metaregistry.add_registry_handler(tricrypto_ng_factory_handler.address)

    # add metaregistry to address provider
    console.log("Add Metaregistry to AddressProvider ...")
    address_provider.add_new_id(7, metaregistry.address, "Metaregistry")

    console.log("Deployment and integration of the Metaregistry completed.")


if __name__ == "__main__":
    # not deployed:
    # aurora

    network = ""
    fork = False
    url = ""

    if network == "xlayer":
        url = "https://rpc.xlayer.tech"
    elif network == "fraxtal":
        url = "https://rpc.frax.com"

    main(network, fork, url=url)
