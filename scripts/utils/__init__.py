import sys
from os import environ, path

import boa
from boa.network import NetworkEnv
from eth_account import Account
from eth_utils import keccak
from rich.console import Console as RichConsole

from scripts.utils.constants import BASE_DIR, FIDDY_DEPLOYER


def get_create2_deployment_address(
    compiled_bytecode,
    abi_encoded_ctor,
    salt,
    create2deployer,
    blueprint=False,
    blueprint_preamble=b"\xFE\x71\x00",
):
    deployment_bytecode = compiled_bytecode + abi_encoded_ctor
    if blueprint:
        # Add blueprint preamble to disable calling the contract:
        blueprint_bytecode = blueprint_preamble + deployment_bytecode
        # Add code for blueprint deployment:
        len_blueprint_bytecode = len(blueprint_bytecode).to_bytes(2, "big")
        deployment_bytecode = (
            b"\x61"
            + len_blueprint_bytecode
            + b"\x3d\x81\x60\x0a\x3d\x39\xf3"
            + blueprint_bytecode
        )

    return (
        create2deployer.computeAddress(salt, keccak(deployment_bytecode)),
        deployment_bytecode,
    )


def deploy_via_create2_factory(deployment_bytecode, salt, create2deployer):
    create2deployer.deploy(0, salt, deployment_bytecode)


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


def get_deployed_contract(contract_name: str, address: str):
    """
    Loads a contract and retrieves a deployed instance of it with the given address.
    :param contract_name: The name of the contract ABI to load.
    :param address: The address of the deployed contract.
    """
    file_name = path.join(
        BASE_DIR, f"contracts/interfaces/{contract_name}.json"
    )
    return boa.load_abi(file_name).at(address)
