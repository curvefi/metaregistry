import pytest
from eth_account import Account
from eth_account.hdaccount import HDPath
from eth_account.hdaccount.mnemonic import Mnemonic
from eth_account.signers.local import LocalAccount

from tests.utils import get_deployed_contract


@pytest.fixture(scope="session")
def seed() -> bytes:
    return Mnemonic.to_seed("test")


@pytest.fixture(scope="session")
def accounts(seed) -> list[LocalAccount]:
    """
    Generate 10 dev accounts from a seed.
    Based on ape's `generate_test_accounts` method:
     https://github.com/ApeWorX/ape/blob/9d4b66786/src/ape/utils/testing.py#L28
    TODO: replace by boa.env.generate_address()?
    """

    def generate_account(
        index: int, hd_path_format="m/44'/60'/0'/{}"
    ) -> LocalAccount:
        hd_path = HDPath(hd_path_format.format(index))
        private_key = f"0x{hd_path.derive(seed).hex()}"
        return Account.from_key(private_key)

    return [generate_account(index) for index in range(10)]


@pytest.fixture(scope="session")
def alice_address(accounts):
    return accounts[0].address


@pytest.fixture(scope="session")
def unauthorised_address(accounts):
    return accounts[1].address


@pytest.fixture(scope="session")
def random_address(accounts):
    return accounts[2].address


@pytest.fixture(scope="module")
def owner(accounts):
    address_provider = get_deployed_contract(
        "AddressProvider", "0x0000000022D53366457F9d5E68Ec105046FC4383"
    )
    return address_provider.admin()
