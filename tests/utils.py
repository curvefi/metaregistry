from os import path
from typing import Union

import boa
from boa.vyper.contract import VyperContract
from eth_account.signers.local import LocalAccount

BASE_DIR = path.join(path.dirname(path.abspath(__file__)), "..")


def get_contract_pools(contract: str, address: str) -> list[str]:
    """
    Retrieves the list of pools from a deployed contract with the given address.
    :param contract: The name of the contract to load.
    :param address: The address of the deployed contract.
    """
    registry = get_deployed_contract(contract, address)
    return [registry.pool_list(i) for i in range(registry.pool_count())]


def get_deployed_contract(contract_abi: str, address: str) -> VyperContract:
    """
    Loads a contract and retrieves a deployed instance of it with the given address.
    TODO: Refactor calls to use fixtures instead of re-loading multiple times.
    :param contract_abi: The name of the contract to load.
    :param address: The address of the deployed contract.
    """
    file_name = path.join(BASE_DIR, f"contracts/mainnet/abi/{contract_abi}.json")
    return boa.load_abi(file_name).at(address)


def deploy_contract(contract: str, *args, sender: Union[LocalAccount, str], directory: str = ".", **kwargs):
    file_name = path.join(BASE_DIR, f"contracts/mainnet/{directory}/{contract}.vy")
    boa.env.eoa = sender if isinstance(sender, str) else sender.address
    return boa.load(file_name, *args, **kwargs)
