"""
Print the missing functions from the registry.
"""
import json

import boa
from rich.console import Console
from rich.table import Table
from sortedcontainers import SortedDict
from vyper.compiler.output import build_abi_output

CELL_VALUES = {True: "[green]✓[/green]", False: "[red]✖[/red]"}


def get_view_functions(abi: list[dict]) -> set[str]:
    """
    Get the view functions from an ABI.
    :param abi: the ABI to get the view functions from
    """
    return {d["name"] for d in abi if d.get("stateMutability") == "view"}


def get_functions_from_abi_json(contract_name: str) -> set[str]:
    """
    Get the view functions from an ABI JSON file.
    :param contract_name: the name of the contract
    :return: the view functions from the ABI JSON file
    """
    with open(f"contracts/interfaces/{contract_name}.json") as f:
        abi = json.load(f)
    return get_view_functions(abi)


def get_functions_from_source(name: str) -> set[str]:
    """
    Get the view functions from a Vyper source file.
    :param name: the name of the source file
    :return: the view functions from the source file
    """
    deployer = boa.load_partial(f"contracts/{name}.vy")
    meta_functions = get_view_functions(
        abi=build_abi_output(deployer.compiler_data)
    )
    return meta_functions


def main() -> None:
    """
    Calculate the missing functions from the registry and print them in a table.
    """
    registry_functions = SortedDict(
        [
            ("MetaRegistry", get_functions_from_source("MetaRegistry")),
            ("CryptoFactory", get_functions_from_abi_json("CryptoFactory")),
            ("CryptoRegistry", get_functions_from_abi_json("CryptoRegistry")),
            ("StableFactory", get_functions_from_abi_json("StableFactory")),
            ("StableRegistry", get_functions_from_abi_json("StableRegistry")),
        ]
    )
    table = compare_contracts(registry_functions)
    return Console().print(table)


def compare_contracts(contract_functions: dict[str, set[str]]) -> Table:
    """
    Create a table with the missing functions.
    :param contract_functions: A dictionary with the contract name as key and a set of the
    view functions as value
    :return: the table with the missing functions
    """
    table = Table(
        "Function Name",
        *contract_functions,
        title="Comparison between the contract view functions",
    )
    for function_name in sorted(set.union(*contract_functions.values())):
        table.add_row(
            function_name,
            *[
                CELL_VALUES[function_name in functions]
                for functions in contract_functions.values()
            ],
        )
    return table


if __name__ == "__main__":
    main()
