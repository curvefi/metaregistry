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
from scripts.deploy_addressprovider_and_setup import fetch_url
from scripts.legacy_base_pools import base_pools as BASE_POOLS
from scripts.utils.constants import FIDDY_DEPLOYER

console = rich_console.Console()

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
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


def check_contract_deployed(network, designation):
    with open("./deployments.yaml", "r") as file:
        deployments = yaml.safe_load(file)

    if deployments is None:
        deployments = {}

    if (
        network in deployments.keys()
        and designation in deployments[network].keys()
    ):
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


def deploy_and_cache_contracts(network, designation, contract_file, args):
    contract_address = check_contract_deployed(network, designation)
    if contract_address != ZERO_ADDRESS:
        return boa.load_partial(contract_file).at(contract_address)

    deployed_contract = boa.load(contract_file, *args)
    store_deployed_contract(network, designation, deployed_contract.address)

    return deployed_contract


def main(network, fork, url, deploy_ng_handlers):
    assert "ethereum" not in network

    if not url:
        url = fetch_url(network)

    if not fork:
        # Prodmode
        console.log("Running script in prod mode...")
        boa.set_env(NetworkEnv(url))
        boa.env.add_account(Account.from_key(os.environ["FIDDYDEPLOYER"]))

    else:
        # Forkmode
        console.log("Simulation Mode. Writing to mainnet-fork.")
        boa.env.fork(url=url)
        boa.env.eoa = FIDDY_DEPLOYER

    address_provider = boa.load_partial("contracts/AddressProviderNG.vy").at(
        ADDRESS_PROVIDER
    )
    metaregistry_address = address_provider.get_address(7)

    # deploy metaregistry
    console.log("Deploying Metaregistry ...")
    gauge_factory = address_provider.get_address(20)  # 20 is for Gauge Factory
    gauge_type = GAUGE_TYPE[network]

    if metaregistry_address == ZERO_ADDRESS:
        metaregistry = deploy_and_cache_contracts(
            network,
            "Metaregistry",
            "contracts/MetaregistryL2.vy",
            [gauge_factory, gauge_type],
        )
        deploy_ng_handlers = True
    else:
        metaregistry = boa.load_partial("contracts/MetaRegistryL2.vy").at(
            metaregistry_address
        )

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
    )

    registry_list = [
        metaregistry.get_registry(i)
        for i in range(metaregistry.registry_length())
    ]

    if not len(base_pools) == base_pools_registry.base_pool_count():
        console.log("Adding base pools to the base pool registry ...")
        added_base_pools = [
            base_pools_registry.base_pool_list(i)
            for i in range(len(base_pools))
        ]
        for base_pool in base_pools:
            if not base_pool[0] in added_base_pools:
                base_pools_registry.add_base_pool(*base_pool)

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
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    stableswap_factory = address_provider.get_address(3)
    if stableswap_factory != ZERO_ADDRESS:
        console.log("Adding stableswap factory to the Metaregistry ...")
        registry_handler = deploy_and_cache_contracts(
            network,
            "StableFactoryHandler",
            "contracts/registry_handlers/StableFactoryHandler.vy",
            [stableswap_factory, base_pools_registry.address],
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
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

    # since we bricked a few contracts:
    if deploy_ng_handlers:
        # set up tricrypto ng factory handler
        console.log("Deploy Tricrypto Factory NG Handler ...")
        tricrypto_ng_factory = address_provider.get_address(11)
        registry_handler = deploy_and_cache_contracts(
            network,
            "TricryptoFactoryNGHandler",
            "contracts/registry_handlers/ng/CurveTricryptoFactoryHandler.vy",
            [tricrypto_ng_factory],
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

        # set up stableswap ng factory handler
        console.log("Deploy Stableswap Factory NG Handler ...")
        stableswap_ng_factory = address_provider.get_address(12)
        registry_handler = deploy_and_cache_contracts(
            network,
            "StableswapFactoryNGHandler",
            "contracts/registry_handlers/ng/CurveStableSwapFactoryNGHandler.vy",
            [stableswap_ng_factory],
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

        # set up twocrypto ng factory handler
        console.log("Deploy Twocrypto Factory NG Handler ...")
        twocrypto_ng_factory = address_provider.get_address(13)
        registry_handler = deploy_and_cache_contracts(
            network,
            "TwocryptoFactoryNGHandler",
            "contracts/registry_handlers/ng/CurveTwocryptoFactoryHandler.vy",
            [twocrypto_ng_factory],
        )
        if registry_handler.address not in registry_list:
            metaregistry.add_registry_handler(registry_handler.address)

        # add metaregistry to address provider
        console.log("Add Metaregistry to AddressProvider ...")
        address_provider.add_new_id(7, metaregistry.address, "Metaregistry")

    console.log(
        f"Deployment and integration of the Metaregistry on {network} completed."
    )


if __name__ == "__main__":
    network = ""
    url = ""
    fork = False
    deploy_ng_handlers = False

    main(network, fork, url, deploy_ng_handlers)
