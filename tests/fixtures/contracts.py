import pytest


@pytest.fixture(scope="module")
def address_provider_contract(accounts):
    address_provider = ape.project.AddressProvider.at(
        "0x0000000022D53366457F9d5E68Ec105046FC4383"
    )
    return accounts[address_provider.admin()]
