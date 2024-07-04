# AddressProvider deployed on zksync at: 0x54A5a69e17Aa6eB89d77aa3828E38C9Eb4fF263D

import os

import boa
import boa_zksync
from eth_account import Account

zksync_rpc = "https://mainnet.era.zksync.io"

boa_zksync.set_zksync_env(zksync_rpc)


def main():
    boa.env.add_account(
        Account.from_key(os.environ["FIDDYDEPLOYER"]), force_eoa=True
    )
    boa.load("contracts/AddressProviderNG.vy")


if __name__ == "__main__":
    main()
