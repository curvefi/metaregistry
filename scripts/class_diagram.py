"""
Generates a mermaid class diagram with the contract selectors and
 the dependencies between contracts.
Usage:
    python scripts/class_diagram.py [glob_pattern] (--internal) (--members)

Unfortunately, rich doesn't support images in the terminal yet, so you'll have to
copy the source or link to the image and paste it in your browser.
"""
import sys
from base64 import b64encode
from dataclasses import dataclass
from glob import glob
from pathlib import Path

import boa
from vyper import ast


@dataclass
class ContractDependencies:
    """
    Describes the information extracted from each vyper contract in order to generate
    the class diagram.
    """

    # the name of the contract (file)
    contract: str
    # a dict of the interface name to a list of the selectors where it's used
    interfaces: dict[str, set[str]]
    functions: list[str]
    variables: list[str]


def get_function_descriptor(node: ast.FunctionDef) -> str:
    """Returns a string describing the function signature."""
    args_descriptor = ", ".join(a.node_source_code for a in node.args.args)
    return f"({node.returns} {node.name} {args_descriptor})"


def parse_contract(filename: str) -> ContractDependencies:
    """
    The interfaces used in a contract and a list of the slots where it's used.
    :param filename: The path to the Vyper source code.
    :return: a list of the interface names used in the contract
    """
    module = boa.load_partial(filename).compiler_data.vyper_module
    interfaces = module.get_children(ast.InterfaceDef)
    return ContractDependencies(
        contract=Path(filename).stem,
        interfaces={
            i.name: {
                node.get_ancestor(ast.FunctionDef).name
                for node in module.get_descendants(ast.Call)
                if getattr(node.func, "id", None) == i.name
            }
            for i in interfaces
        },
        functions=sorted(
            {
                get_function_descriptor(node)
                for node in module.get_children(ast.FunctionDef)
            }
        ),
        variables=sorted(
            {
                node.node_source_code.replace("(", " ").replace(")", "")
                for node in module.get_children(ast.VariableDecl)
            }
        ),
    )


def main(pattern: str, internal=True, members=True) -> None:
    """
    Generates a mermaid graph of the dependencies between contracts.
    Prints the graph and a link to the image via the Mermaid Live Editor.
    :param pattern: a glob pattern to match the contracts
    :param internal: whether to include internal dependencies
    :param members: whether to include the members of each contract
    """
    contracts = [
        parse_contract(filename) for filename in glob(pattern, recursive=True)
    ]
    names = {c.contract for c in contracts}

    classes = (
        [
            line
            for contract in contracts
            for line in [f"  class {contract.contract} {{"]
            + contract.variables
            + contract.functions
            + ["  }"]
        ]
        if members
        else []
    )

    connections = [
        f"  {contract.contract} --> {interface}: "
        f"{', '.join(selectors) if 0 < len(selectors) < 3 else f'{len(selectors)} selectors'}"
        for contract in contracts
        for interface, selectors in contract.interfaces.items()
        if not internal or interface in names
    ]

    graph = "\n".join(["classDiagram"] + classes + connections)

    print(graph)
    print(
        f"https://mermaid.ink/img/{b64encode(graph.encode()).decode('ascii')}"
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    main(
        pattern=args[0] if args else "contracts/**/*.vy",
        internal="--internal" in args,
        members="--members" in args,
    )
