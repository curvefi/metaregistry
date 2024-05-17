"""
Deploy the Crypto Registry Handler contract
Requires the Crypto Registry contract to be deployed first.

Usage for fork mode:
    scripts/deploy_crypto_registry_handler.py
    requires the RPC_ETHEREUM environment variable to be set
Usage for prod mode:
    scripts/deploy_crypto_registry_handler.py --prod
    requires the URL and ACCOUNT environment variables to be set
"""
import boa
from rich import Console as RichConsole

from scripts.deployment_utils import setup_environment

CRYPTO_REGISTRY_ADDRESS = "0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0"


def main():
    console = RichConsole()
    console.log("Deploying Crypto Registry Handler contract...")
    setup_environment(console)
    boa.load("contracts/registry_handlers/CryptoRegistryHandler.vy")


if __name__ == "__main__":
    main()
