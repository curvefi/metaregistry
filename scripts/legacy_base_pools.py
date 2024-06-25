# pool
# lp_token
# n_coins
# is_legacy
# is_lending
# is_v2

base_pools = {
    "arbitrum": [
        [
            "0x7f90122BF0700F9E7e1F688fe926940E8839F353",  # 2pool
            "0x7f90122BF0700F9E7e1F688fe926940E8839F353",
            2,
            False,
            False,
            False,
        ],
        [
            "0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb",  # wbtc/renbtc
            "0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb",
            2,
            False,
            False,
            False,
        ],
        [
            "0xC9B8a3FDECB9D5b218d02555a8Baf332E5B740d5",  # fraxbp
            "0xC9B8a3FDECB9D5b218d02555a8Baf332E5B740d5",
            2,
            False,
            False,
            False,
        ],
    ],
    "optimism": [
        [
            "0x1337BedC9D22ecbe766dF105c9623922A27963EC",  # 3pool
            "0x1337BedC9D22ecbe766dF105c9623922A27963EC",
            3,
            False,
            False,
            False,
        ],
        [
            "0x29A3d66B30Bc4AD674A4FDAF27578B64f6afbFe7",  # fraxbp
            "0x29A3d66B30Bc4AD674A4FDAF27578B64f6afbFe7",
            2,
            False,
            False,
            False,
        ],
    ],
    "polygon": [
        [
            "0xC2d95EEF97Ec6C17551d45e77B590dc1F9117C67",  # aave btc
            "0xf8a57c1d3b9629b77b6726a042ca48990A84Fb49",
            2,
            False,
            True,  # aave atokens
            False,
        ],
        [
            "0x445FE580eF8d70FF569aB36e80c647af338db351",  # aave 3pool
            "0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171",
            3,
            False,
            True,  # aave atokens
            False,
        ],
    ],
    "fantom": [
        [
            "0x27E611FD27b276ACbd5Ffd632E5eAEBEC9761E40",  # dai <> usdc
            "0x27E611FD27b276ACbd5Ffd632E5eAEBEC9761E40",
            2,
            False,
            False,
            False,
        ],
        [
            "0x3eF6A01A0f81D6046290f3e2A8c5b843e738E604",  # renbtc
            "0x5B5CFE992AdAC0C9D48E05854B2d91C73a003858",
            2,
            False,
            False,
            False,
        ],
        [
            "0x0fa949783947Bf6c1b171DB13AEACBB488845B3f",  # geist 3pool
            "0xD02a30d33153877BC20e5721ee53DeDEE0422B2F",
            3,
            False,
            True,
            False,
        ],
    ],
    "gnosis": [
        [
            "0x7f90122BF0700F9E7e1F688fe926940E8839F353",  # x3pool
            "0x1337BedC9D22ecbe766dF105c9623922A27963EC",
            3,
            False,
            False,
            False,
        ],
    ],
    "avalanche": [
        [
            "0x7f90122BF0700F9E7e1F688fe926940E8839F353",  # av3pool
            "0x1337BedC9D22ecbe766dF105c9623922A27963EC",
            3,
            False,
            True,
            False,
        ],
        [
            "0x16a7DA911A4DD1d83F3fF066fE28F3C792C50d90",  # aave renbtc/wbtc
            "0xC2b1DF84112619D190193E48148000e3990Bf627",
            2,
            False,
            True,
            False,
        ],
    ],
}
