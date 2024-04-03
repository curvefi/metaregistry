"""
Sets up the metaregistry.

Usage for fork mode:
    scripts/setup_metaregistry.py
    requires the RPC_ETHEREUM environment variable to be set
Usage for prod mode:
    scripts/setup_metaregistry.py --prod
    requires the URL and ACCOUNT environment variables to be set
"""
import sys

import boa
from rich.console import Console as RichConsole

# This is the layout as of deploying the new addressprovider.
# The key is _id, the value is _description
ADDRESS_PROVIDER_MAPPING = {
    0: "Stableswap Custom Pool Registry",
    1: "PoolInfo Getters",
    2: "Exchange Router",
    3: "Stableswap Metapool Factory",
    4: "Fee Distributor",
    5: "Cryptoswap Custom Pool Registry",
    6: "Twocrypto Factory",
    7: "Metaregistry",
    8: "Stableswap crvUSD Factory",
    9: "",
    10: "",
    11: "TricryptoNG Factory",
    12: "StableswapNG Factory",
    13: "TwocryptoNG Factory",
    14: "Stableswap Calculations Contract",
    15: "Cryptoswap calculations Contract",
    16: "LLAMMA Factory crvUSD",
    17: "LLAMMA Factory OneWayLending",
    18: "Rate Provider",
    # TODO: add DAO-related contracts, CRV token per chain, gauge factories, ...
}

# These are the addresses that will go into the addressprovider for each chain:

addresses = {
    "ethereum": {
        0: "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5",
        1: "0xe64608E223433E8a03a1DaaeFD8Cb638C14B552C",
        2: "0xF0d4c12A5768D806021F80a262B4d39d26C58b8D",
        3: "0xB9fC157394Af804a3578134A6585C0dc9cc990d4",
        4: "0xA464e6DCda8AC41e03616F95f4BC98a13b8922Dc",
        5: "0x8F942C20D02bEfc377D41445793068908E2250D0",
        6: "0xF18056Bbd320E96A48e3Fbf8bC061322531aac99",
        7: "0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC",
        8: "0x4F8846Ae9380B90d2E71D5e3D042dff3E7ebb40d",
        11: "0x0c0e5f2fF0ff18a3be9b835635039256dC4B4963",  # Tricrypto NG
        12: "0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf",  # Stableswap NG
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",  # Twocrypto NG
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
        16: "0xc9332fdcb1c491dcc683bae86fe3cb70360738bc",  # call controllerFactory.amm(id) to get AMM address
        17: "0xeA6876DDE9e3467564acBeE1Ed5bac88783205E0",  # same as (16)
    },
    "arbitrum": {
        0: "0x445FE580eF8d70FF569aB36e80c647af338db351",
        1: "0x78CF256256C8089d68Cde634Cf7cDEFb39286470",
        2: "0xF0d4c12A5768D806021F80a262B4d39d26C58b8D",
        3: "0xb17b674D9c5CB2e441F8e196a2f048A81355d031",
        4: "0xd4F94D0aaa640BBb72b5EEc2D85F6D114D81a88E",
        5: "0x0E9fBb167DF83EdE3240D6a5fa5d40c6C6851e15",
        11: "0xbC0797015fcFc47d9C1856639CaE50D0e69FbEE8",
        12: "0x9AF14D26075f142eb3F292D5065EB3faa646167b",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
        17: "0xcaEC110C784c9DF37240a8Ce096D352A75922DeA",
    },
    "optimism": {
        0: "0xC5cfaDA84E902aD92DD40194f0883ad49639b023",
        1: "0x54e8A25d0Ac0E4945b697C80b8372445FEA17A62",
        2: "0xF0d4c12A5768D806021F80a262B4d39d26C58b8D",
        3: "0x2db0E83599a91b508Ac268a6197b8B14F5e72840",
        4: "0xbF7E49483881C76487b0989CD7d9A8239B20CA41",
        5: "0x7DA64233Fefb352f8F501B357c018158ED8aA455",
        11: "0xc6C09471Ee39C7E30a067952FcC89c8922f9Ab53",
        12: "0x5eeE3091f747E60a045a2E715a4c71e600e31F6E",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "polygon": {
        0: "0x094d12e5b541784701FD8d65F11fc0598FBC6332",
        1: "0x7544Fe3d184b6B55D6B36c3FCA1157eE0Ba30287",
        2: "0xF0d4c12A5768D806021F80a262B4d39d26C58b8D",
        3: "0x722272D36ef0Da72FF51c5A65Db7b870E2e8D4ee",
        4: "0x774D1Dba98cfBD1F2Bc3A1F59c494125e07C48F9",
        5: "0x47bB542B9dE58b970bA50c9dae444DDB4c16751a",
        6: "0xE5De15A9C9bBedb4F5EC13B131E61245f2983A69",
        11: "0xC1b393EfEF38140662b91441C6710Aa704973228",  # Tricrypto NG
        12: "0x1764ee18e8B3ccA4787249Ceb249356192594585",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "base": {
        2: "0xd6681e74eEA20d196c15038C580f721EF2aB6320",
        3: "0x3093f9B57A428F3EB6285a589cb35bEA6e78c336",
        4: "0xe8269B33E47761f552E1a3070119560d5fa8bBD6",
        6: "0x5EF72230578b3e399E6C6F4F6360edF95e83BBfd",
        11: "0xA5961898870943c68037F6848d2D866Ed2016bcB",
        12: "0xd2002373543Ce3527023C75e7518C274A51ce712",
        13: "0xc9Fe0C63Af9A39402e8a5514f9c43Af0322b665F",
        14: "0x5552b631e2aD801fAa129Aacf4B701071cC9D1f7",
        15: "0xEfadDdE5B43917CcC738AdE6962295A0B343f7CE",
    },
    "fraxtal": {
        2: "0x4f37A9d177470499A2dD084621020b023fcffc1F",
        4: "0x8b3EFBEfa6eD222077455d6f0DCdA3bF4f3F57A6",
        11: "0xc9Fe0C63Af9A39402e8a5514f9c43Af0322b665F",
        12: "0xd2002373543Ce3527023C75e7518C274A51ce712",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0x69522fb5337663d3B4dFB0030b881c1A750Adb4f",
    },
    "linea": {
        11: "0xd125E7a0cEddF89c6473412d85835450897be6Dc",
        12: "0x5eeE3091f747E60a045a2E715a4c71e600e31F6E",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
    },
    "mantle": {
        11: "0x0C9D8c7e486e822C29488Ff51BFf0167B4650953",
        12: "0x5eeE3091f747E60a045a2E715a4c71e600e31F6E",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
    },
    "scroll": {
        11: "0xC1b393EfEF38140662b91441C6710Aa704973228",
        12: "0x5eeE3091f747E60a045a2E715a4c71e600e31F6E",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
    },
    "pzkevm": {
        11: "0x76303e4fDcA0AbF28aB3ee42Ce086E6503431F1D",
        12: "0xd2002373543Ce3527023C75e7518C274A51ce712",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
    },
    "bsc": {
        11: "0x38f8D93406fA2d9924DcFcB67dB5B0521Fb20F7D",
        12: "0xd7E72f3615aa65b92A4DBdC211E296a35512988B",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0x0fE38dCC905eC14F6099a83Ac5C93BF2601300CF",
        15: "0xd6681e74eEA20d196c15038C580f721EF2aB6320",
    },
    "gnosis": {
        11: "0xb47988ad49dce8d909c6f9cf7b26caf04e1445c8",
        12: "0xbC0797015fcFc47d9C1856639CaE50D0e69FbEE8",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "fantom": {
        11: "0x9AF14D26075f142eb3F292D5065EB3faa646167b",
        12: "0xe61Fb97Ef6eBFBa12B36Ffd7be785c1F5A2DE66b",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "avax": {
        11: "0x3d6cB2F6DcF47CDd9C13E4e3beAe9af041d8796a",
        12: "0x1764ee18e8B3ccA4787249Ceb249356192594585",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "aurora": {
        11: "0x3d6cB2F6DcF47CDd9C13E4e3beAe9af041d8796a",
        12: "0x5eeE3091f747E60a045a2E715a4c71e600e31F6E",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "celo": {
        11: "0x3d6cB2F6DcF47CDd9C13E4e3beAe9af041d8796a",
        12: "0x1764ee18e8B3ccA4787249Ceb249356192594585",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
    "kava": {
        11: "0x3d6cB2F6DcF47CDd9C13E4e3beAe9af041d8796a",
        12: "0x1764ee18e8B3ccA4787249Ceb249356192594585",
        13: "0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F",
        14: "0xCA8d0747B5573D69653C3aC22242e6341C36e4b4",
        15: "0xA72C85C258A81761433B4e8da60505Fe3Dd551CC",
    },
}
