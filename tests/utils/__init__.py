from brownie import ZERO_ADDRESS
from .constants import *


def deploy_stable_factory_pool(
    stable_factory, two_coin_plain_pool_implementation, coin_a, coin_b, owner
):
    tx = stable_factory.set_plain_implementations(
        2,
        [
            two_coin_plain_pool_implementation,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        {"from": owner},
    )

    handle = f"{coin_a[2:6]}-{coin_b[2:6]}"
    tx = stable_factory.deploy_plain_pool(
        f"2pool-{handle}",
        handle,
        [
            coin_a,
            coin_b,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
        ],
        10000,
        4000000,
        0,
        0,
        {"from": owner},
    )
    return tx.new_contracts[0]
