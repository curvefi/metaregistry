import json
from os import path
from typing import Union

import boa
from boa.vyper.contract import VyperContract
from eth_account.signers.local import LocalAccount

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
BASE_DIR = path.join(path.dirname(path.abspath(__file__)), "..")


def get_contract_pools(contract_name: str, address: str) -> list[str]:
    """
    Retrieves the list of pools from a deployed contract with the given address.
    :param contract_name: The name of the contract to load.
    :param address: The address of the deployed contract.
    """
    registry = get_deployed_contract(contract_name, address)
    return [registry.pool_list(i) for i in range(registry.pool_count())]


def get_deployed_contract(contract_name: str, address: str) -> VyperContract:
    """
    Loads a contract and retrieves a deployed instance of it with the given address.
    TODO: Refactor calls to use fixtures instead of re-loading multiple times.
    :param contract_name: The name of the contract ABI to load.
    :param address: The address of the deployed contract.
    """
    file_name = path.join(
        BASE_DIR, f"contracts/interfaces/{contract_name}.json"
    )
    return boa.load_abi(file_name).at(address)


def deploy_contract(
    contract: str,
    *args,
    sender: Union[LocalAccount, str],
    directory: str = ".",
    **kwargs,
) -> VyperContract:
    file_name = path.join(
        BASE_DIR, f"contracts/mainnet/{directory}/{contract}.vy"
    )
    with boa.env.sender(sender):
        return boa.load(file_name, *args, **kwargs)


def get_deployed_token_contract(address: str) -> VyperContract:
    """
    Gets the LP token contract at the given address. This uses a subset of the ERC20 ABI.
    :param address: The address of the LP token contract.
    """
    abi = json.dumps(
        [
            {
                "name": "name",
                "constant": True,
                "inputs": [],
                "outputs": [{"name": "", "type": "string"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "decimals",
                "constant": True,
                "inputs": [],
                "outputs": [{"name": "", "type": "uint8"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function",
            },
            {
                "name": "totalSupply",
                "inputs": [],
                "outputs": [{"type": "uint256", "name": ""}],
                "stateMutability": "view",
                "type": "function",
                "gas": 2531,
            },
            {
                "name": "balanceOf",
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "account",
                        "type": "address",
                    }
                ],
                "outputs": [
                    {"internalType": "uint256", "name": "", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function",
            },
        ]
    )
    return boa.loads_abi(abi).at(address)
