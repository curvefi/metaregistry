import sys
from os import environ

import boa
from boa.network import NetworkEnv
from eth_account import Account
from rich.console import Console as RichConsole

FIDDYDEPLOYER = "0x2d12D0907A388811e3AA855A550F959501d303EE"


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
    boa.env.eoa = FIDDYDEPLOYER
    return False
