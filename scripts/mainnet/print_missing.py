from brownie import MetaRegistry, interface


def main():
    meta_selectors = set(MetaRegistry.selectors)
    print(meta_selectors)

    for registry_name in [f"{a}{b}" for a in ["Crypto", "Stable"] for b in ["Factory", "Registry"]]:
        registry = getattr(interface, registry_name)
        print(registry_name, "*" * len(registry_name), sep="\n")

        view_fns = {d["name"] for d in registry.abi if d.get("stateMutability") == "view"}
        missing_fns = {registry.selectors[k] for k in (set(registry.selectors) - meta_selectors)}

        print("\n".join(sorted(missing_fns & view_fns)), "\n")
