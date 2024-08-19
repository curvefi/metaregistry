# AddressProvider deployed on zksync at: 0x3934a3bB913E4a44316a89f5a83876B9C63e4F31

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
