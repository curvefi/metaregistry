"""
Sets up the metaregistry.

Usage for fork mode:
    scripts/setup_metaregistry.py
    requires the RPC_ETHEREUM environment variable to be set
Usage for prod mode:
    scripts/setup_metaregistry.py --prod
    requires the URL and ACCOUNT environment variables to be set
"""
import sys

import boa
from rich.console import Console as RichConsole

from scripts.deployment_utils import get_deployed_contract, setup_environment
from scripts.utils.constants import (
    ADDRESS_PROVIDER,
    BASE_POOLS,
    CRYPTO_REGISTRY_POOLS,
)

RICH_CONSOLE = RichConsole(file=sys.stdout)

# TODO: Metaregistry and Base Pool Registry no longer have a dependency AddressProvider's admin.
# Adjust the code accordingly:


def main():
    """
    This script sets up the metaregistry. It does the following:
    1. Adds base pools to base pool registry.
    2. Adds crypto pools to crypto registry.
    3. Adds registry handlers to metaregistry.
    4. Adds metaregistry to address provider.
    """

    setup_environment(RICH_CONSOLE)
    account = boa.env.eoa

    # admin only: only admin of ADDRESSPROVIDER's proxy admin can do the following:
    address_provider = get_deployed_contract(
        "AddressProvider", ADDRESS_PROVIDER
    )
    address_provider_admin = address_provider.admin()
    proxy_admin = get_deployed_contract("ProxyAdmin", address_provider_admin)

    # deployed contracts:
    base_pool_registry = get_deployed_contract(
        "BasePoolRegistry", "0xDE3eAD9B2145bBA2EB74007e58ED07308716B725"
    )
    crypto_registry = get_deployed_contract(
        "CryptoRegistryV1", "0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0"
    )
    stable_registry_handler = get_deployed_contract(
        "StableRegistryHandler", "0x46a8a9CF4Fc8e99EC3A14558ACABC1D93A27de68"
    )
    stable_factory_handler = get_deployed_contract(
        "StableFactoryHandler", "0x127db66E7F0b16470Bec194d0f496F9Fa065d0A9"
    )
    crypto_registry_handler = get_deployed_contract(
        "CryptoRegistryHandler", "0x5f493fEE8D67D3AE3bA730827B34126CFcA0ae94"
    )
    crypto_factory_handler = get_deployed_contract(
        "CryptoFactoryHandler", "0xC4F389020002396143B863F6325aA6ae481D19CE"
    )
    metaregistry = get_deployed_contract(
        "MetaRegistry", "0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC"
    )
    registry_handlers = [
        stable_registry_handler,
        stable_factory_handler,
        crypto_registry_handler,
        crypto_factory_handler,
    ]

    # set up the metaregistry:

    total_gas_used = (
        0  # gets total gas used for setting up. should be about 5mil gas.
    )

    # populate base pool registry:
    base_pool_index = 0
    for _, data in BASE_POOLS.items():
        # check if base pool already exists in the registry:
        entry_at_index = base_pool_registry.base_pool_list(
            base_pool_index
        ).lower()
        if entry_at_index == data["pool"].lower():
            base_pool_index += 1
            continue

        # set up tx calldata for proxy admin:
        call_data = base_pool_registry.add_base_pool.as_transaction(
            data["pool"],
            data["lp_token"],
            data["num_coins"],
            data["is_legacy"],
            data["is_lending"],
            data["is_v2"],
            sender=address_provider_admin,
        ).data

        # add base_pool to registry:
        tx = proxy_admin.execute(base_pool_registry, call_data, sender=account)
        total_gas_used += tx.gas_used

        # check if deployment is correct:
        assert (
            base_pool_registry.base_pool_list(base_pool_index).lower()
            == data["pool"].lower()
        )
        RICH_CONSOLE.log(
            f"Added base pool [blue]{data['pool']} to base pool registry. "
            f"Gas used: [green]{tx.gas_used}"
        )
        base_pool_index += 1

    # populate crypto registry:
    crypto_pool_index = 0
    for _, pool in CRYPTO_REGISTRY_POOLS.items():
        # check if base pool already exists in the registry:
        entry_at_index = crypto_registry.pool_list(crypto_pool_index).lower()
        if entry_at_index == pool["pool"].lower():
            crypto_pool_index += 1
            continue

        # set up tx calldata for proxy admin:
        call_data = crypto_registry.add_pool.as_transaction(
            pool["pool"],
            pool["lp_token"],
            pool["gauge"],
            pool["zap"],
            pool["num_coins"],
            pool["name"],
            pool["base_pool"],
            pool["has_positive_rebasing_tokens"],
            sender=address_provider_admin,
        ).data

        # add pool to registry:
        tx = proxy_admin.execute(crypto_registry, call_data, sender=account)
        total_gas_used += tx.gas_used

        # check if deployment is correct:
        assert (
            crypto_registry.pool_list(crypto_pool_index).lower()
            == pool["pool"].lower()
        )
        RICH_CONSOLE.log(
            f"Added pool [blue]{pool['pool']} to crypto registry. "
            f"Gas used: [green]{tx.gas_used}"
        )
        crypto_pool_index += 1

    # populate metaregistry:
    registry_handler_index = 0
    for registry_handler in registry_handlers:
        # check if base pool already exists in the registry:
        entry_at_index = metaregistry.get_registry(
            registry_handler_index
        ).lower()
        if entry_at_index == registry_handler.address.lower():
            registry_handler_index += 1
            continue

        # set up tx calldata for proxy admin:
        call_data = metaregistry.add_registry_handler.as_transaction(
            registry_handler.address, sender=address_provider_admin
        ).data

        # add registry handler to metaregistry:
        tx = proxy_admin.execute(metaregistry, call_data, sender=account)
        total_gas_used += tx.gas_used

        # check if deployment is correct:
        assert (
            metaregistry.get_registry(registry_handler_index).lower()
            == registry_handler.address.lower()
        )
        RICH_CONSOLE.log(
            f"Added registry handler [blue]{registry_handler.address} to metaregistry. "
            f"Gas used: [green]{tx.gas_used}"
        )
        registry_handler_index += 1

    # add metaregistry to address provider:
    max_id = address_provider.max_id()
    RICH_CONSOLE.log(
        f"Max id: [yellow]{max_id}, entry: [blue]{address_provider.get_address(max_id)}."
    )
    metaregistry_description = "Metaregistry"
    call_data = address_provider.add_new_id.as_transaction(
        metaregistry.address,
        metaregistry_description,
        sender=address_provider_admin,
    ).data
    tx = proxy_admin.execute(
        address_provider.address, call_data, sender=account
    )
    total_gas_used += tx.gas_used

    # check if adding metaregistry was done properly:
    new_max_id = address_provider.max_id()
    assert new_max_id > max_id
    assert (
        address_provider.get_address(new_max_id).lower()
        == metaregistry.address.lower()
    )
    RICH_CONSOLE.log(
        f"Added Metaregistry [blue]{metaregistry.address} to AddressProvider. "
        f"Gas used: [green]{tx.gas_used}"
    )
    RICH_CONSOLE.log(
        f"Deployment complete! Total gas used: [green]{total_gas_used}"
    )

    # test metaregistry. get a list of pools that have shibainu <> frax:
    print(
        metaregistry.find_pools_for_coins(
            "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
            "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        )
    )


if __name__ == "__main__":
    main()
