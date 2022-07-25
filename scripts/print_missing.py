import ape
from tabulate import tabulate

MISSING = "\033[33m✖\033[0m"
PRESENT = "\033[32m✓\033[0m"


def main():
    def get_non_indexed_view_functions(registry_selectors, registry_abi, fn_index):
        view_fns = {d["name"] for d in registry_abi if d.get("stateMutability") == "view"}
        non_indexed_fns = dict(registry_selectors.items() - fn_index.items())
        return {
            k: registry_selectors[k]
            for k, v in non_indexed_fns.items()
            if registry_selectors[k] in view_fns
        }

    function_index = get_non_indexed_view_functions(
        ape.project.MetaRegistry.selectors, ape.project.MetaRegistry.abi, {}
    )
    registry_coverage = [[PRESENT] * len(function_index)]
    registry_names = [f"{a}{b}" for a in ["Crypto", "Stable"] for b in ["Factory", "Registry"]]

    for registry_name in registry_names:
        registry = getattr(interface, registry_name)
        non_indexed_view_fns = get_non_indexed_view_functions(
            registry.selectors, registry.abi, function_index
        )
        function_index.update(non_indexed_view_fns)
        registry_coverage.append(
            [PRESENT if fn in registry.selectors else MISSING for fn in function_index.keys()]
        )

    registry_coverage = [
        coverage + [MISSING] * (len(function_index) - len(coverage))
        for coverage in registry_coverage
    ]
    res = sorted(zip(function_index.values(), *registry_coverage))
    print(tabulate(res, headers=["Functions", "MetaRegistry"] + registry_names))
