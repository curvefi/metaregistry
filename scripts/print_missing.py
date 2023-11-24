import json

import boa
from rich.console import Console
from rich.table import Table
from vyper.compiler.output import build_abi_output

MISSING = "[red]✖[/red]"
PRESENT = "[green]✓[/green]"
META_NAME = "MetaRegistry"


def get_view_functions(abi: list[dict]) -> set[str]:
    """
    Get the view functions from an ABI.
    :param abi: the ABI to get the view functions from
    """
    return {d["name"] for d in abi if d.get("stateMutability") == "view"}


def main() -> None:
    """
    Calculate the missing functions from the registry and print them in a table.
    """
    console = Console()
    metaregistry = boa.load_partial(f"contracts/mainnet/{META_NAME}.vy")
    meta_functions = get_view_functions(
        abi=build_abi_output(metaregistry.compiler_data)
    )
    registry_names = [
        "CryptoFactory",
        "CryptoRegistry",
        "StableFactory",
        "StableRegistry",
    ]

    registry_functions = {META_NAME: meta_functions}
    for registry_name in registry_names:
        with open(f"contracts/interfaces/{registry_name}.json") as f:
            registry_abi = json.load(f)
        registry_functions[registry_name] = get_view_functions(registry_abi)

    table = create_table(registry_functions)
    return console.print(table)


def create_table(registry_functions: dict[str, set[str]]) -> Table:
    """
    Create a table with the missing functions.
    :param registry_functions: the functions from the registries
    :return: the table with the missing functions
    """
    table = Table(title="Missing Functions")
    all_functions = set.union(*registry_functions.values())
    registries = [META_NAME] + sorted(
        registry_name
        for registry_name in registry_functions
        if registry_name != META_NAME
    )
    table.add_column("Function Name")
    for registry_name in registries:
        table.add_column(registry_name)
    for function_name in sorted(all_functions):
        cells = [
            PRESENT
            if function_name in registry_functions[registry_name]
            else MISSING
            for registry_name in registries
        ]
        table.add_row(function_name, *cells)
    return table


if __name__ == "__main__":
    main()
