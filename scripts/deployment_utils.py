import sys
from os import environ, path

import boa
from boa.network import NetworkEnv
from boa.vyper.contract import VyperContract
from eth_account import Account
from rich.console import Console as RichConsole

from scripts.constants import BASE_DIR, FIDDY_DEPLOYER


def setup_environment(console: RichConsole):
    """
    Sets up the environment for deployment scripts.
    Requires the following environment variables:
        For forks (default):
        - RPC_ETHEREUM: URL to fork from.
        For prod (script called with --prod argument):
        - URL: URL to connect to.
        - ACCOUNT: Private key of account to use.

    :param console: RichConsole instance to log to.
    :return: Whether the environment is in prod mode.
    """
    if "--prod" in sys.argv:
        console.log("Running script in prod mode...")
        boa.set_env(NetworkEnv(environ["URL"]))
        boa.env.add_account(Account.from_key(environ["ACCOUNT"]))
        return True

    console.log("Simulation Mode. Writing to mainnet-fork.")
    boa.env.fork(url=environ["RPC_ETHEREUM"])
    boa.env.eoa = FIDDY_DEPLOYER
    return False


def get_deployed_contract(contract_name: str, address: str) -> VyperContract:
    """
    Loads a contract and retrieves a deployed instance of it with the given address.
    :param contract_name: The name of the contract ABI to load.
    :param address: The address of the deployed contract.
    """
    file_name = path.join(
        BASE_DIR, f"contracts/interfaces/{contract_name}.json"
    )
    return boa.load_abi(file_name).at(address)
