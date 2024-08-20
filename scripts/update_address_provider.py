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


FIDDY_DEPLOYER = "0x2d12D0907A388811e3AA855A550F959501d303EE"
ADDRESS_PROVIDER = (
    "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"  # gets replaced for zksync
)
to_update = {
    "ethereum": {
        2: '0x16C6521Dff6baB339122a0FE25a9116693265353',
        4: '0xD16d5eC345Dd86Fb63C6a9C43c517210F1027914',
    },
    "optimism": {
        2: '0x0DCDED3545D565bA3B19E683431381007245d983',
    },
    "gnosis": {
        2: '0x0DCDED3545D565bA3B19E683431381007245d983',
    },
    "polygon": {
        2: '0x0DCDED3545D565bA3B19E683431381007245d983',
    },
    "fantom": {
        2: '0x0DCDED3545D565bA3B19E683431381007245d983',
    },
    "kava": {
        2: '0x0DCDED3545D565bA3B19E683431381007245d983',
    },
    "arbitrum": {
        2: '0x2191718CD32d02B8E60BAdFFeA33E4B5DD9A0A0D',
    },
    "avalanche": {
        2: '0x0DCDED3545D565bA3B19E683431381007245d983',
    },
    "base": {
        2: '0x4f37A9d177470499A2dD084621020b023fcffc1F',
    },
    "bsc": {
        2: '0xA72C85C258A81761433B4e8da60505Fe3Dd551CC',
    },
    "fraxtal": {
        2: '0x9f2Fa7709B30c75047980a0d70A106728f0Ef2db',
    },
    "xlayer": {
        2: '0xBFab8ebc836E1c4D81837798FC076D219C9a1855',
    },
    "mantle": {
        2: '0x4f37A9d177470499A2dD084621020b023fcffc1F',
    },
    "zksync": {
        2: '0x7C915390e109CA66934f1eB285854375D1B127FA',
    },
}


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
    
    console.log(f"For network: {network}")

    # set up address provider
    network_update = to_update[network]
    if not network_update:
        return
    
    updating = False
    for key, value in network_update.items():
        current_value = address_provider.get_address(key)
        if not current_value == value:
            updating = True
            console.log(f"Updating id {key} from {current_value} to {value}.")
            address_provider.update_address(key, value)

    if updating:
        console.log("Done!")
    else:
        console.log("Already updated!")


if __name__ == "__main__":
    
    fork = False
    
    for network in to_update.keys():

        url = ""

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
