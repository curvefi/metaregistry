import boa
import pytest
from eth_account.signers.local import LocalAccount

from scripts.constants import ADDRESS_PROVIDER
from scripts.deployment_utils import get_deployed_contract


@pytest.fixture(scope="session")
def accounts() -> list[LocalAccount]:
    """
    Generate 10 dev accounts from a seed.
    """
    return [boa.env.generate_address(f"{i}") for i in range(10)]


@pytest.fixture(scope="session")
def alice_address(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def unauthorised_address(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
def random_address(accounts):
    return accounts[2]


@pytest.fixture(scope="module")
def owner(accounts):
    address_provider = get_deployed_contract(
        "AddressProvider", ADDRESS_PROVIDER
    )
    return address_provider.admin()
