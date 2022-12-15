import sys

from brownie import (
    AddressProvider,
    CryptoRegistry,
    MetaRegistry,
    ProxyAdmin,
    accounts,
    network,
)
from brownie.network.gas.strategies import GasNowScalingStrategy
from rich.console import Console as RichConsole

RICH_CONSOLE = RichConsole(file=sys.stdout)
ADDRESS_PROVIDER = "0x0000000022D53366457F9d5E68Ec105046FC4383"
CRYPTO_REGISTRY_HANDLER = "0x5f493fEE8D67D3AE3bA730827B34126CFcA0ae94"
CRYPTO_REGISTRY_HANDLER_ID = 2
OLD_CRYPTO_REGISTRY_HANDLER = "0x22ceb131d3170f9f2FeA6b4b1dE1B45fcfC86E56"
CRYPTO_REGISTRY = "0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


if network.show_active() == "mainnet":
    RICH_CONSOLE.log("Writing on mainnet")
    accounts.load("babe")
    txparams = {"from": accounts[0], "required_confs": 5}
    try:
        network.gas_price(GasNowScalingStrategy("slow", "fast"))
    except ConnectionError:
        pass

else:
    RICH_CONSOLE.log("Simulation Mode. Writing to mainnet-fork.")
    txparams = {
        "from": accounts.at(
            "0xbabe61887f1de2713c6f97e567623453d3C79f67", force=True
        )
    }


def main():

    # admin only: only admin of ADDRESSPROVIDER's proxy admin can do the following:
    address_provider = AddressProvider.at(ADDRESS_PROVIDER)
    address_provider_admin = address_provider.admin()
    proxy_admin = ProxyAdmin.at(address_provider_admin)

    metaregistry = MetaRegistry.at(
        "0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC"
    )

    assert (
        metaregistry.get_registry(CRYPTO_REGISTRY_HANDLER_ID)
        == OLD_CRYPTO_REGISTRY_HANDLER
    )
    num_pools = metaregistry.pool_count()
    num_registries = metaregistry.registry_length()
    num_pools_in_crypto_registry = CryptoRegistry.at(
        CRYPTO_REGISTRY
    ).pool_count()

    call_data = metaregistry.update_registry_handler.encode_input(
        CRYPTO_REGISTRY_HANDLER_ID,
        CRYPTO_REGISTRY_HANDLER,
    )
    proxy_admin.execute(metaregistry.address, call_data, txparams)

    assert (
        metaregistry.pool_count() == num_pools + num_pools_in_crypto_registry
    )
    assert metaregistry.registry_length() == num_registries
    assert (
        metaregistry.get_gauge("0xD51a44d3FaE010294C616388b506AcdA1bfAAE46")
        != ZERO_ADDRESS
    )


if __name__ == "__main__":
    main()
