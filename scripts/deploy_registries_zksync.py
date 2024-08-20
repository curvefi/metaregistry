# flake8: noqa

import os
import sys

import boa
import yaml
from boa.network import NetworkEnv
from eth.constants import ZERO_ADDRESS
from eth_account import Account
from rich import console as rich_console

sys.path.append("./")
from scripts.address_provider_constants import (
    ADDRESS_PROVIDER_MAPPING,
    addresses,
)
from scripts.deploy_addressprovider_and_setup import fetch_url
from scripts.legacy_base_pools import base_pools as BASE_POOLS
from scripts.utils.constants import FIDDY_DEPLOYER

console = rich_console.Console()

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# if -1: no gauge type known just yet
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
    "zksync": -1,
}


def check_contract_deployed(network, designation):
    with open("./deployments.yaml", "r") as file:
        deployments = yaml.safe_load(file)

    if deployments is None:
        deployments = {}

    if network in deployments and deployments[network].get(designation):
        contract_address = deployments[network][designation]
        console.log(
            f"{designation} deployed already at {network}: {contract_address}"
        )
        return contract_address

    return ZERO_ADDRESS


def store_deployed_contract(network, designation, deployment_address):
    with open("./deployments.yaml", "r") as file:
        deployments = yaml.safe_load(file)

    if deployments is None:
        deployments = {}

    if not network in deployments.keys():
        deployments[network] = {}

    deployments[network][designation] = str(deployment_address)
    with open("./deployments.yaml", "w") as file:
        yaml.dump(deployments, file)


def deploy_and_cache_contracts(
    network, designation, contract_file, args, fork=False
):
    contract_address = check_contract_deployed(network, designation)
    if contract_address and contract_address != ZERO_ADDRESS:
        return boa.load_partial(contract_file).at(contract_address)

    deployed_contract = boa.load(contract_file, *args)
    if not fork:
        store_deployed_contract(
            network, designation, deployed_contract.address
        )

    return deployed_contract


def deploy_base_pool_registry(network, fork):
    # deploy base pool registry (even if there are no legacy base pools):
    console.log("Deploying base pool registry ...")
    base_pools = []
    if network in BASE_POOLS.keys():
        base_pools = BASE_POOLS[network]

    base_pools_registry = deploy_and_cache_contracts(
        network,
        "BasePoolRegistry",
        "contracts/registries/BasePoolRegistry.vy",
        [],
        fork,
    )

    # will add new base pools if registry does not have it:
    if not len(base_pools) == base_pools_registry.base_pool_count():
        console.log("Adding base pools to the base pool registry ...")
        added_base_pools = [
            base_pools_registry.base_pool_list(i)
            for i in range(len(base_pools))
        ]
        for base_pool in base_pools:
            if not base_pool[0] in added_base_pools:
                base_pools_registry.add_base_pool(*base_pool)

    return base_pools_registry


def legacy_deployment(address_provider, metaregistry, registry_list):
    # deploy stableswap registry and factory handlers
    stableswap_custom_pool_registry = address_provider.get_address(0)
    if stableswap_custom_pool_registry != ZERO_ADDRESS:
        console.log(
            "Adding stableswap custom pool registry to the Metaregistry ..."
        )
        registry_handler = deploy_and_cache_contracts(
            network,
            "StableRegistryHandler",
            "contracts/registry_handlers/StableRegistryHandler.vy",
            [stableswap_custom_pool_registry],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    stableswap_factory = address_provider.get_address(3)
    if stableswap_factory != ZERO_ADDRESS:
        # we need the base pools registry for legacy deployments
        base_pools_registry = deploy_base_pool_registry(network, fork)

        console.log("Adding stableswap factory to the Metaregistry ...")
        registry_handler = deploy_and_cache_contracts(
            network,
            "StableFactoryHandler",
            "contracts/registry_handlers/StableFactoryHandler.vy",
            [stableswap_factory, base_pools_registry.address],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    # deploy cryptoswap registry and factory handlers
    cryptoswap_custom_pool_registry = address_provider.get_address(5)
    if cryptoswap_custom_pool_registry != ZERO_ADDRESS:
        console.log(
            "Adding cryptoswap custom pool registry to the Metaregistry ..."
        )
        registry_handler = deploy_and_cache_contracts(
            network,
            "CryptoRegistryHandler",
            "contracts/registry_handlers/CryptoRegistryHandler.vy",
            [cryptoswap_custom_pool_registry],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    cryptoswap_factory = address_provider.get_address(6)
    if cryptoswap_factory != ZERO_ADDRESS:
        console.log("Adding cryptoswap factory to the Metaregistry ...")
        registry_handler = deploy_and_cache_contracts(
            network,
            "CryptoFactoryHandler",
            "contracts/registry_handlers/CryptoFactoryHandler.vy",
            [cryptoswap_factory, base_pools_registry.address],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)


def ng_deployment(address_provider, metaregistry, registry_list):
    # set up tricrypto ng factory handler
    tricrypto_ng_factory = address_provider.get_address(11)
    if tricrypto_ng_factory != ZERO_ADDRESS:
        console.log("Adding Tricrypto Factory NG Handler ...")
        registry_handler = deploy_and_cache_contracts(
            network,
            "TricryptoFactoryNGHandler",
            "contracts/registry_handlers/ng/CurveTricryptoFactoryHandler.vy",
            [tricrypto_ng_factory],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    # set up stableswap ng factory handler
    stableswap_ng_factory = address_provider.get_address(12)
    if stableswap_ng_factory != ZERO_ADDRESS:
        console.log("Adding Stableswap Factory NG Handler ...")
        registry_handler = deploy_and_cache_contracts(
            network,
            "StableswapFactoryNGHandler",
            "contracts/registry_handlers/ng/CurveStableSwapFactoryNGHandler.vy",
            [stableswap_ng_factory],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    # set up twocrypto ng factory handler
    twocrypto_ng_factory = address_provider.get_address(13)
    if twocrypto_ng_factory != ZERO_ADDRESS:
        console.log("Adding Twocrypto Factory NG Handler ...")
        registry_handler = deploy_and_cache_contracts(
            network,
            "TwocryptoFactoryNGHandler",
            "contracts/registry_handlers/ng/CurveTwocryptoFactoryHandler.vy",
            [twocrypto_ng_factory],
            fork,
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)


def main(network, fork, url):
    if network == "zksync":
        import boa_zksync

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

    # deploy address provider:
    address_provider = deploy_and_cache_contracts(
        network,
        "AddressProvider",
        "contracts/AddressProviderNG.vy",
        [],
        fork,
    )

    # deploy rate provider:
    rate_provider = deploy_and_cache_contracts(
        network,
        "RateProvider",
        "contracts/RateProvider.vy",
        [address_provider.address],
        fork,
    )

    console.log("Adding rate provider to address provider")
    if address_provider.get_address(18) == ZERO_ADDRESS:
        address_provider.add_new_id(
            18, rate_provider.address, "Spot Rate Provider"
        )
    elif address_provider.get_address(18) != rate_provider.address:
        address_provider.update_address(18, rate_provider.address)

    # set up address provider:
    ids = []
    addresses_for_id = []
    descriptions = []
    for id in addresses[network].keys():
        address = addresses[network][id]
        description = ADDRESS_PROVIDER_MAPPING[id]
        existing_id = address_provider.get_id_info(id)

        if not address:
            continue

        if (
            existing_id[0].lower()
            == "0x0000000000000000000000000000000000000000"
        ):
            console.log(f"New id {id} at {address} for {description}.")
            ids.append(id)
            addresses_for_id.append(address)
            descriptions.append(description)

        elif existing_id[0].lower() != address.lower():
            console.log(f"Updating id {id} for {description} with {address}.")
            address_provider.update_id(id, address, description)

        if len(ids) > 20:
            raise

    if len(ids) > 0:
        console.log("Adding new IDs to the Address Provider.")
        address_provider.add_new_ids(ids, addresses_for_id, descriptions)

    # metaregistry deployment:
    metaregistry_address = address_provider.get_address(7)

    # deploy metaregistry or fetch if it doesnt exist:
    console.log("Deploying Metaregistry ...")
    gauge_factory = address_provider.get_address(20)  # 20 is for Gauge Factory
    gauge_type = GAUGE_TYPE[network]

    deploy_mregistry = metaregistry_address == ZERO_ADDRESS

    if deploy_mregistry:
        metaregistry = deploy_and_cache_contracts(
            network,
            "Metaregistry",
            "contracts/MetaRegistryL2.vy",
            [gauge_factory, gauge_type],
            fork,
        )

        # Add Metaregistry to AddressProvider
        console.log("Add Metaregistry to AddressProvider ...")
        address_provider.add_new_id(7, metaregistry.address, "Metaregistry")
    else:
        metaregistry = boa.load_partial("contracts/MetaRegistryL2.vy").at(
            metaregistry_address
        )

    registry_list = [
        metaregistry.get_registry(i)
        for i in range(metaregistry.registry_length())
    ]

    # legacy registry handlers deployment:
    legacy_deployment(address_provider, metaregistry, registry_list)

    # ng registry handlers deployment:
    ng_deployment(address_provider, metaregistry, registry_list)

    console.log(
        f"Deployment and integration of the Metaregistry on {network} completed."
    )


if __name__ == "__main__":
    network = "zksync"
    url = {
        "zksync": "https://mainnet.era.zksync.io",
        "fraxtal": "https://rpc.frax.com",
        "kava": "https://rpc.ankr.com/kava_evm",
    }.get(network) or fetch_url(network)
    fork = False
    main(network, fork, url)
