import pytest


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
def owner(address_provider, accounts):
    return accounts[address_provider.admin()]
