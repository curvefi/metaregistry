"""
Deploy the contracts to the network.
Usage for fork mode:
    scripts/deploy.py
    requires the RPC_ETHEREUM environment variable to be set
Usage for prod mode:
    scripts/deploy.py --prod
    requires the URL and ACCOUNT environment variables to be set
"""
import boa
from eth_abi import encode
from rich import Console as RichConsole

from scripts.deployment_utils import setup_environment
from scripts.utils.constants import (
    ADDRESS_PROVIDER,
    CRYPTO_FACTORY_ADDRESS,
    STABLE_FACTORY_ADDRESS,
    STABLE_REGISTRY_ADDRESS,
)


def main():
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
    console = RichConsole()
    setup_environment(console)

    # deploy basepool registry:
    base_pool_registry = boa.load("contracts/registries/BasePoolRegistry.vy")

    # deploy crypto registry:
    console.log(
        "Crypto Registry constructor arguments: ",
        encode(["address", "address"], [ADDRESS_PROVIDER, base_pool_registry]),
    )
    crypto_registry = boa.load(
        "contracts/registries/CryptoRegistryV1.vy",
        ADDRESS_PROVIDER,
        base_pool_registry,
    )

    # deploy stable registry handler:
    console.log(
        "Stable Registry Handler constructor arguments: ",
        encode(["address"], [STABLE_REGISTRY_ADDRESS]).hex(),
    )
    boa.load(
        "contracts/registry_handlers/StableRegistryHandler.vy",
        STABLE_REGISTRY_ADDRESS,
    )

    # deploy stable factory handler:
    console.log(
        "Stable Factory Handler constructor arguments: ",
        encode(
            ["address", "address"],
            [STABLE_FACTORY_ADDRESS, base_pool_registry],
        ).hex(),
    )
    boa.load(
        "contracts/registry_handlers/StableFactoryHandler.vy",
        STABLE_FACTORY_ADDRESS,
        base_pool_registry,
    )

    # deploy crypto registry handler:
    console.log(
        "Crypto Registry Handler constructor arguments: ",
        encode(["address"], [crypto_registry]).hex(),
    )
    boa.load(
        "contracts/registry_handlers/CryptoRegistryHandler.vy",
        crypto_registry,
    )

    # deploy crypto factory handler:
    console.log(
        "Crypto Factory Handler constructor arguments: ",
        encode(
            ["address", "address"],
            [CRYPTO_FACTORY_ADDRESS, base_pool_registry],
        ).hex(),
    )
    boa.load(
        "contracts/registry_handlers/CryptoFactoryHandler.vy",
        CRYPTO_FACTORY_ADDRESS,
        base_pool_registry,
    )

    # deploy metaregistry:
    console.log(
        "MetaRegistry constructor arguments: ",
        encode(["address"], [ADDRESS_PROVIDER]).hex(),
    )
    boa.load("contracts/MetaRegistry.vy", ADDRESS_PROVIDER)


if __name__ == "__main__":
    main()
