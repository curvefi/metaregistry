import sys

import boa
from rich.console import Console as RichConsole

from scripts.deployment_utils import get_deployed_contract, setup_environment
from scripts.utils.constants import ADDRESS_PROVIDER, ZERO_ADDRESS

RICH_CONSOLE = RichConsole(file=sys.stdout)
CRYPTO_REGISTRY_HANDLER = "0x5f493fEE8D67D3AE3bA730827B34126CFcA0ae94"
CRYPTO_REGISTRY_HANDLER_ID = 2
OLD_CRYPTO_REGISTRY_HANDLER = "0x22ceb131d3170f9f2FeA6b4b1dE1B45fcfC86E56"
CRYPTO_REGISTRY = "0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0"
METAREGISTRY = "0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC"


def main() -> None:
    """
    Change the registry handler of the metaregistry to the new crypto registry handler.
    :param txparams: txparams argument for the proxy admin.
    """
    txparams = (
        {"from": "0xbabe61887f1de2713c6f97e567623453d3C79f67"}
        if setup_environment(RICH_CONSOLE)
        else {"from": boa.env.eoa, "required_confs": 5}
    )

    # admin only: only admin of ADDRESSPROVIDER's proxy admin can do the following:
    address_provider = get_deployed_contract(
        "AddressProvider", ADDRESS_PROVIDER
    )
    address_provider_admin = address_provider.admin()
    proxy_admin = get_deployed_contract("ProxyAdmin", address_provider_admin)
    metaregistry = get_deployed_contract("MetaRegistry", METAREGISTRY)

    assert (
        metaregistry.get_registry(CRYPTO_REGISTRY_HANDLER_ID)
        == OLD_CRYPTO_REGISTRY_HANDLER
    )
    num_pools = metaregistry.pool_count()
    num_registries = metaregistry.registry_length()
    crypto_registry = get_deployed_contract("CryptoRegistry", CRYPTO_REGISTRY)
    num_pools_in_crypto_registry = crypto_registry.pool_count()

    call_data = metaregistry.update_registry_handler.encode_input(
        CRYPTO_REGISTRY_HANDLER_ID,
        CRYPTO_REGISTRY_HANDLER,
    )
    proxy_admin.execute(metaregistry.address, call_data, txparams)

    assert (
        metaregistry.pool_count() == num_pools + num_pools_in_crypto_registry
    )
    assert metaregistry.registry_length() == num_registries
    gauge = metaregistry.get_gauge(
        "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46"
    )
    assert gauge != ZERO_ADDRESS


if __name__ == "__main__":
    main()
