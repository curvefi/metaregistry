# Curve Metaregistry

The metaregistry is a [Curve Finance](https://curve.exchange/) Pool Registry Aggregator that consolidates different registries used at Curve Finance for a single chain into a single contract.

The current version of the MetaRegistry aggregates of the following four child registries:

Mainnet:

1. Curve Stable Registry: A registry of custom pool implementations deployed by Curve Core.
2. Curve Stable Factory: A permissionless [StableSwap](https://curve.fi/files/stableswap-paper.pdf) pool factory, which also acts as a registry for pools that its users create.
3. Curve Crypto Registry: A registry of custom CryptoSwap pool implementations deployed by Curve Core.
4. Curve Crypto Factory: A permissionless [CryptoSwap](https://curve.fi/files/crypto-pools-paper.pdf) pool factory, which also acts as a registry for pools that its users create.

Each of the child registries are accompanied by a RegistryHandler, which is a contract that wraps around the child registry and enforces the abi implemented in the MetaRegistry. These registry handlers are then added to the MetaRegistry using the `MetaRegistry.add_registry_handler` method.

In principle, a child registry does not need a registry handler wrapper, if it already conforms to the MetaRegistry's abi standards. However, a wrapper around the child registries can be used to hotfix bugs detected in production when such fixes cannot be introduced to the child registry without significant breaking changes.

# Who should use the MetaRegistry?

Integrators find it quite challenging to integrate a protocol into their dapp if there are multiple on-chain registry stored in separate contracts: They do not have intrinsic knowledge in the protocol level to accommodate edge cases and onboard multiple registries. A single source of information that aggregates all registries makes integrations trivial. If you are an integrator looking to integrate Curve, the MetaRegistry is your best friend.

# The MetaRegistry API

The MetaRegistry offers an on-chain API for various properties of Curve pools. The various getters in the MetaRegistry are explained in the following.

#### `MetaRegistry.get_registry_handlers_from_pool`

Gets registries that a pool has been registered in. Usually, each pool is registered in a single registry.

```
In [1]: metaregistry.get_registry_handlers_from_pool("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]:[
        '0xc7D231bC7ff5AC1E0e67244d1A273a79bC762bfB',
        '0xfBdA211B53e17e10aa5B5c564F19519258dA05B4',
        '0x0000000000000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000',
        ...
    ]
```

#### `MetaRegistry.pool_count`

Returns the total number of pools under all registries registered in the metaregistry.

```
In [1]: metaregistry.pool_count()
Out[1]: 284
```

#### `MetaRegistry.pool_list`

Returns the address of the pool at the input index `i`.

```
In [1]: metaregistry.pool_list(0)
Out[1]: "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7"
```

#### `MetaRegistry.get_pool_name`

Returns the name of the pool.

```
In [1]: metaregistry.get_pool_name("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: '3pool'
```

#### `MetaRegistry.is_meta`

Meta-pools are pools that pair a coin to a base pool comprising multiple coins.

An example is the [`LUSD-3CRV`](https://etherscan.io/address/0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca) pool which pairs [Liquidity's](https://www.liquity.org/) [`LUSD`](https://etherscan.io/address/0x5f98805a4e8be255a32880fdec7f6728c6568ba0) against [`3CRV`](https://etherscan.io/address/0x6c3f90f043a72fa612cbac8115ee7e52bde6e490), where `3CRV` is a liquidity pool token that represents a share of a pool containing `DAI`, `USDC` and `USDT`:

```
In [1]: metaregistry.is_meta("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: True
```

#### `MetaRegistry.get_base_pool`

In the case of the `LUSD-3CRV` pool example, the pool containing `3CRV` underlying coins is the base pool of the `LUSD-3CRV` pool, which is the [`3pool`](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7):

```
In [1]: metaregistry.get_base_pool("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7'
```

It returns `ZERO_ADDRESS` if the pool has no base pool:

```
In [1]: metaregistry.get_base_pool("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: '0x0000000000000000000000000000000000000000'
```

#### `MetaRegistry.get_coins`

Returns coins in a pool. If the pool is a metapool, it then returns the LP token associated with the base pool, and not the underlying coins.

```
In [1]: metaregistry.get_coins("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: [
    '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0',
    '0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490',
    ...
]
```

#### `MetaRegistry.get_underlying_coins`

Returns underlying coins in a pool. Returns underlying coins of the base pool if the pool is a metapool.

```
In [1]: metaregistry.get_underlying_coins("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: [
    '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0',
    '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    ...
]
```

#### `MetaRegistry.get_n_coins`

Returns number of coins in a pool.

```
In [1]: metaregistry.get_n_coins("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: 3
```

#### `MetaRegistry.get_n_underlying_coins`

Returns the total number of underlying coins in a pool.

```
In [1]: metaregistry.get_n_underlying_coins("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: 4
```

#### `MetaRegistry.get_decimals`

Returns decimals of the coins that are returned by `MetaRegistry.get_coins`.

```
In [1]: metaregistry.get_decimals("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: [18, 6, 6, 0, 0, 0, 0, 0]
```

#### `MetaRegistry.get_underlying_decimals`

Returns decimals of coins returned by `MetaRegistry.get_underlying_coins`

```
In [1]: metaregistry.get_underlying_decimals("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: [18, 18, 6, 6, 0, 0, 0, 0]
```

#### `MetaRegistry.get_balances`

Returns balances of each coin in a Curve pool.

```
In [1]: metaregistry.get_balances("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: [344100999218050094997802859, 339451232552152, 323541886417619, 0, 0, 0, 0, 0]
```

#### `MetaRegistry.get_underlying_balances`

Returns a pool's balances of coins returned by `MetaRegistry.get_underlying_coins`.

```
In [25]: populated_metaregistry.get_underlying_balances("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[25]: [5475800032746048063986567, 18068769367677440019648367, 17824609770086, 16989208807146, ...]
```

#### `MetaRegistry.get_admin_balances`

Returns pool's admin balances. These admin balances accrue per swap, since a part of the fees that are generated by Curve pools go to the admin (an external contract, controlled by the Curve DAO). The amount of fees that go to admin and LPs can be set at the time of pool's creation, and for some pools this can be changed later.

The balances represent the balances per coin, and retain the coin's precision.

```
In [1]: metaregistry.get_admin_balances("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: [3332213937603257114591, 6607424786, 9725600245, 0, 0, 0, 0, 0]
```

#### `MetaRegistry.get_fees`

Returns fees that a Curve pool charges per swap. The returned fee data is different for StableSwap pools (which just use a single parameter for fees, other than admin fees), than CryptoSwap pools (which use multiple parameters for fees, due to its dynamic fee structure).

For Stableswap, the getter returns the `fee` per swap as well as the `admin_fee` percentage. For the `3pool`, it shows that the pool charges 1 basis points per swap, 50% of which goes to the DAO.

```
In [1]: metaregistry.get_fees("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: [1000000, 5000000000, 0, 0, 0, 0, 0, 0, 0, 0]
```

For CryptoSwap, the getter returns: `fee`, `admin_fee` percentage, `mid_fee` and `out_fee`. The fee is the dynamic fee charged per swap, and depends on the `mid_fee` (fee when the CryptoSwap pool is pegged) and the `out_fee`. For understanding the dynamic fee algorithm, the reader is pointed to the [CryptoSwap Paper](https://curve.fi/files/crypto-pools-paper).

```
In [1]: metaregistry.get_fees("0xd51a44d3fae010294c616388b506acda1bfaae46")
Out[1]: [5954883, 5000000000, 5000000, 30000000, 0, 0, 0, 0, 0, 0]
```

#### `MetaRegistry.find_pool_for_coins`

Returns a pool that holds two coins (even if the pool is a metapool). The index in the query returns the index of the list of pools containing the two coins.

```
In [1]: metaregistry.find_pool_for_coins(
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            0
        )
Out[1]: '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7'

In [2]: metaregistry.find_pool_for_coins(
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            1
        )
Out[2]: '0xDeBF20617708857ebe4F679508E7b7863a8A8EeE'
```

#### `MetaRegistry.find_pools_for_coins`

Returns a list of pools that holds two coins (even if the pool is a metapool).

```
In [1]: metaregistry.find_pools_for_coins(
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        )
Out[1]:
['0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7',
 '0xDeBF20617708857ebe4F679508E7b7863a8A8EeE',
 '0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27',
 '0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56',
 '0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF',
 '0x06364f10B501e868329afBc005b3492902d6C763',
 '0xA5407eAE9Ba41422680e2e00537571bcC53efBfD',
 '0xA5407eAE9Ba41422680e2e00537571bcC53efBfD',
 '0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C',
 '0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51']
```

#### `MetaRegistry.get_coin_indices`

Given a `_from` coin, a `_to` coin, and a `_pool`, this getter returns coin indices and a boolean that indicates if the coin swap involves an underlying market. In case of a non-metapool, the following is returned:

```

In [1]: metaregistry.get_coin_indices(
"0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
"0x6B175474E89094C44Da98b954EedeAC495271d0F",
"0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
)
Out[1]: (0, 1, False)

```

If the coin combination involves an underlying market (same coins, but with the `LUSD` pool):

```

In [1]: metaregistry.get_coin_indices(
"0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca",
"0x6B175474E89094C44Da98b954EedeAC495271d0F",
"0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
)
Out[1]: (1, 2, True)

```

#### `MetaRegistry.get_pool_params`

Returns a pool's parameters.

For StableSwap, the getter returns the amplification coefficient (`A`) of the pool.

```

In [1]: metaregistry.get_pool_params("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")
Out[1]: [2000, ... ]

```

For CryptoSwap, the getter returns:

1. Amplification coefficient (`A`)
2. Invariant (`D`)
3. Gamma coefficient (`gamma`)
4. Allowed extra profit
5. Fee gamma
6. Adjustment step
7. MA (moving average) half-time

```

In [1]: metaregistry.get_pool_params("0xd51a44d3fae010294c616388b506acda1bfaae46")
Out[1]: [1707629, 257946982336455335322438705, 11809167828997, 2000000000000, 500000000000000, 2000000000000000, 600, ... ]

```

#### `MetaRegistry.get_gauge`

Gets the gauge that receives `CRV` token inflation for depositing the liquidity pool token of a pool.

```

In [1]: metaregistry.get_gauge("0xd51a44d3fae010294c616388b506acda1bfaae46", 0, 0)
Out[1]: '0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168'

```

#### `MetaRegistry.get_gauge_type`

Gets the gauge type of the gauge associated with a pool.

```

In [1]: metaregistry.get_gauge_type("0xd51a44d3fae010294c616388b506acda1bfaae46", 0, 0)
Out[1]: 5

```

#### `MetaRegistry.get_lp_token`

Gets the address of the liquidity pool token minted by a pool.

```

In [1]: metaregistry.get_lp_token("0xd51a44d3fae010294c616388b506acda1bfaae46")
Out[1]: '0xc4AD29ba4B3c580e6D59105FFf484999997675Ff'

```

#### `MetaRegistry.get_pool_asset_type`

Gets the asset type of a pool. `0` = `USD`, `1` = `ETH`, `2` = `BTC`, `3` = Other, `4` = CryptoPool token. The asset type is a property of StableSwaps, and is not enforced in CryptoSwap pools (which always return `4`).

StableSwap pool example for `LUSD-3CRV` pool which is a `USD` stablecoin pool:

```

In [1]: metaregistry.get_pool_asset_type("0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca")
Out[1]: 0

```

CryptoSwap pool example:

```

In [1]: metaregistry.get_pool_asset_type("0xd51a44d3fae010294c616388b506acda1bfaae46")
Out[1]: 4

```

#### `MetaRegistry.get_pool_from_lp_token`

Gets the pool associated with a liquidity pool token.

```

In [1]: metaregistry.get_pool_from_lp_token("0xc4AD29ba4B3c580e6D59105FFf484999997675Ff")
Out[1]: '0xD51a44d3FaE010294C616388b506AcdA1bfAAE46'

```

#### `MetaRegistry.get_virtual_price_from_lp_token`

Gets a token's virtual price. The virtual price of any pool begins with `1`, and increases as the pool accrues fees. This number constantly increases for StableSwap pools, unless the pool's amplification coefficient changes. For CryptoSwap pools, there are moments when the virtual price can go down (admin fee claims, changes to pool's parameters).

```

In [1]: metaregistry.get_virtual_price_from_lp_token("0xc4AD29ba4B3c580e6D59105FFf484999997675Ff")
Out[1]: 1020841390601246610

```

# Setup

Set up the python environment using the following steps:

```

> python -m venv venv
> source ./venv/bin/activate
> python -m pip install --upgrade pip
> pip install -r ./requirements.txt

```

This project uses [`titanoboa`](https://github.com/vyperlang/titanoboa) for deployment and testing.

### Testing

To run tests in interactive mode, please do the following:

```

> python -m pytest

```

# Deployment and Adding Registries

Various deployment scripts are provided in the [scripts](./scripts/) folder.

#### Deployments

Ethereum Mainnet:

- `base_pool_registry`: [0xDE3eAD9B2145bBA2EB74007e58ED07308716B725](https://etherscan.io/address/0xDE3eAD9B2145bBA2EB74007e58ED07308716B725#code)
- `crypto_registry`: [0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0](https://etherscan.io/address/0x9a32aF1A11D9c937aEa61A3790C2983257eA8Bc0#code)
- `stable_registry_handler`: [0x46a8a9CF4Fc8e99EC3A14558ACABC1D93A27de68](https://etherscan.io/address/0x46a8a9CF4Fc8e99EC3A14558ACABC1D93A27de68#code)
- `stable_factory_handler`: [0x127db66E7F0b16470Bec194d0f496F9Fa065d0A9](https://etherscan.io/address/0x127db66E7F0b16470Bec194d0f496F9Fa065d0A9#code)
- `crypto_registry_handler`: [0x22ceb131d3170f9f2FeA6b4b1dE1B45fcfC86E56](https://etherscan.io/address/0x22ceb131d3170f9f2FeA6b4b1dE1B45fcfC86E56#code)
- `crypto_factory_handler`: [0xC4F389020002396143B863F6325aA6ae481D19CE](https://etherscan.io/address/0xC4F389020002396143B863F6325aA6ae481D19CE#code)
- `metaregistry`: [0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC](https://etherscan.io/address/0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC#code)

### Roadmap

1. StableSwap-ng Factory Handler
2. Twocrypto-ng Factory Handler
3. Tricrypto-ng Factory Handler
4. Deployments of Metaregistry with the above handlers across multiple chains.

### License

(c) Curve.Fi, 2023 - [All rights reserved](LICENSE).
