import os

import boa
from eth_account import Account
from rich.console import Console as RichConsole

# import sys
# sys.path.append("./")

FIDDY_DEPLOYER = ""
ADDRESS_PROVIDER = "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"


def fetch_url(network):
    return os.getenv("DRPC_URL") % (network, os.getenv("DRPC_KEY"))


def main(network, fork, url=""):
    """
    Deploy the AddressProvider to the network.
    """

    console = RichConsole()
    if not url:
        url = fetch_url(network)

    console.log(f"Network: {network}")

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
    metaregistry_address = address_provider.get_address(7)

    if "ethereum" not in network:
        metaregistry = boa.load_partial("contracts/MetaregistryL2.vy").at(
            metaregistry_address
        )
    else:
        metaregistry = boa.load_partial("contracts/Metaregistry.vy").at(
            metaregistry_address
        )

    # set up twocrypto ng factory handler
    console.log("Deploy Replacement Twocrypto Factory Handler ...")
    twocrypto_ng_factory = address_provider.get_address(13)
    twocrypto_ng_factory_handler = boa.load(
        "contracts/registry_handlers/ng/CurveTwocryptoFactoryHandler.vy",
        twocrypto_ng_factory,
    )

    # Update registry handler in the metaregistry
    if "ethereum" not in network:
        twocrypto_index = metaregistry.registry_length() - 2
    else:
        twocrypto_index = metaregistry.registry_length() - 1

    console.log("Replace TwocryptoFactoryHandler in Metaregistry ...")
    metaregistry.update_registry_handler(
        twocrypto_index, twocrypto_ng_factory_handler.address
    )

    # add metaregistry to address provider
    console.log("TwocryptoFactoryHandler in Metaregistry replaced.")


if __name__ == "__main__":
    # not deployed:
    # aurora

    fork = False
    url = ""
    network = ""

    main(network, fork, url=url)
