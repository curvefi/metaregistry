from collections import namedtuple

import pytest
from eth_account import Account
from eth_account.hdaccount import HDPath
from eth_account.hdaccount.mnemonic import Mnemonic
from ethpm_types import HexBytes

GeneratedDevAccount = namedtuple("GeneratedDevAccount", ("address", "private_key"))


@pytest.fixture(scope="session")
def seed() -> bytes:
    return Mnemonic.to_seed("test")

@pytest.fixture(scope="session")
def accounts(seed) -> list[GeneratedDevAccount]:
    """
    Generate 10 dev accounts from a seed.
    Based on ape's `generate_test_accounts` method:
     https://github.com/ApeWorX/ape/blob/9d4b66786/src/ape/utils/testing.py#L28
    """
    def generate_account(index: int, hd_path_format="m/44'/60'/0'/{}") -> GeneratedDevAccount:
        hd_path = HDPath(hd_path_format.format(index))
        private_key = HexBytes(hd_path.derive(seed)).hex()
        address = Account.from_key(private_key).address
        return GeneratedDevAccount(address, private_key)

    return [generate_account(index) for index in range(10)]

@pytest.fixture(scope="session")
def alice(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def unauthorised_account(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
def random_address(accounts):
    return accounts[2]


@pytest.fixture(scope="module")
def owner(accounts):
    address_provider = ape.project.AddressProvider.at(
        "0x0000000022D53366457F9d5E68Ec105046FC4383"
    )
    return accounts[address_provider.admin()]
