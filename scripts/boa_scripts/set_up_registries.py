# flake8: noqa

import os
import sys
from dataclasses import dataclass
from typing import List

import boa
import deployment_utils as deploy_utils
from boa.network import NetworkEnv
from deploy_infra import deployments
from eth_account import Account
from eth_typing import Address
from eth_utils import to_checksum_address
from rich.console import Console as RichConsole

logger = RichConsole(file=sys.stdout)


def deploy_factory_handler():
    pass


def set_up_registries(
    network: str, url: str, account: str, fork: bool = False
):
    """
    Set up registries for the Curve StableSwapNG factory.
    :param network: Network to deploy to.
    :param url: URL to connect to.
    :param account: Account to use.
    :param fork: Whether to deploy to a fork (test) network.
    """

    logger.log(f"Connecting to {network} ...")
    if fork:
        boa.env.fork(url)
        boa.env.eoa = deploy_utils.FIDDYDEPLOYER
        logger.log("Forkmode")
    else:
        logger.log("Prodmode")
        boa.set_env(NetworkEnv(url))
        boa.env.eoa = Account.from_key(os.environ[account])

    data = next(
        (
            data
            for _network, data in deploy_utils.curve_dao_network_settings.items()
            if _network in network
        ),
        None,
    )

    owner = data.dao_ownership_contract
    fee_receiver = data.fee_receiver_address
    address_provider = Contract(data.address_provider)
    assert owner, f"Curve's DAO contracts may not be on {network}."
    assert fee_receiver, f"Curve's DAO contracts may not be on {network}."

    # -------------------------- Register into AddressProvider --------------------------

    max_id = address_provider.max_id()
    description = "Curve StableSwapNG"
    boss = Contract(address_provider.admin())

    # check if account can handle boss:
    account_is_boss_handler = any(
        account.address.lower() == boss.admins(i).lower() for i in range(2)
    )
    assert account_is_boss_handler  # only authorised accounts can write to address provider  # noqa: E501

    is_new_deployment = not any(
        address_provider.get_id_info(i).description is description
        for i in range(max_id + 1)
    )

    if is_new_deployment:
        logger.info(
            f"Adding a new registry provider entry at id: {max_id + 1}"
        )

        # we're adding a new id
        with accounts.use_sender(account) as account:
            boss.execute(
                address_provider.address,
                address_provider.add_new_id.encode_input(factory, description),
                gas_limit=400000,
                **deploy_utils._get_tx_params(),
            )

    else:
        assert address_provider.get_id_info(index).description == description

        logger.info(
            f"Updating existing registry provider entry at id: {index}"
        )

        # we're updating an existing id with the same description:
        with accounts.use_sender(account) as account:
            boss.execute(
                address_provider.address,
                address_provider.set_address.encode_input(index, factory),
                gas_limit=200000,
                **deploy_utils._get_tx_params(),
            )

    assert address_provider.get_id_info(index).addr.lower() == factory.lower()

    logger.info("AddressProvider integration complete!")

    # -------------------------- Set up metaregistry --------------------------

    metaregistry_address = deploy_utils.curve_dao_network_settings[
        network
    ].metaregistry_address
    base_pool_registry_address = deploy_utils.curve_dao_network_settings[
        network
    ].base_pool_registry_address

    if metaregistry_address:
        metaregistry = Contract(metaregistry_address)
        boss = Contract(metaregistry.owner())

        # set up metaregistry integration:
        logger.info("Integrate into Metaregistry ...")
        logger.info(
            "Deploying Factory handler to integrate it to the metaregistry:"
        )
        factory_handler = account.deploy(
            project.CurveStableSwapFactoryNGHandler,
            factory.address,
            base_pool_registry_address,
            **deploy_utils._get_tx_params(),
        )

        boss.execute(
            metaregistry.address,
            metaregistry.add_registry_handler.encode_input(factory_handler),
            **deploy_utils._get_tx_params(),
        )

        logger.info("Metaregistry integration complete!")


def main():
    set_up_registries(
        "ethereum:mainnet",
        os.environ["RPC_ETHEREUM"],
        "FIDDYDEPLOYER",
        fork=False,
    )


if __name__ == "__main__":
    main()
