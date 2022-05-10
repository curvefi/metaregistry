from brownie import Contract


def init_contract(_addr: str) -> Contract:

    try:
        return Contract(_addr)
    except:
        return Contract.from_explorer(_addr)
