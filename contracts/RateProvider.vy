# pragma version 0.3.10
# pragma evm-version paris
"""
@title CurveRateProvider
@custom:version 1.1.0
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2020-2024 - all rights reserved
@notice Provides quotes for coin pairs, iff coin pair is in a Curve AMM
        that the Metaregistry recognises.
@dev Rate contract calls metaregistry to fetch a list of coins for coin_a and coin_b via: metaregistry.find_pools_for_coins
     Rate contract gets coin indices from metaregistry.get_coin_indices
     If pool is stableswap (check if pool has gamma parameter], then step 2 returns is_underlying as True in the Tuple output.
     The rate contract calls get_dy or get_dy_underlying for each pool and coin indices list.
     The rate contract compiles this into a list of quotes.
"""

version: public(constant(String[8])) = "1.1.0"

MAX_COINS: constant(uint256) = 8
MAX_QUOTES: constant(uint256) = 100

struct Quote:

    source_token_index: uint256
    dest_token_index: uint256
    is_underlying: bool

    amount_out: address

    pool: address

    pool_balances: DynArray[uint256, MAX_COINS]

    # 0 for stableswap, 1 for cryptoswap, 2 for LLAMMA.
    pool_type: uint8


# Interfaces

interface AddressProvider:
    def get_address(id: uint256) -> address: view

interface Metaregistry:
    def find_pools_for_coins(source_coin: address, destination_coin: address) -> DynArray[address, 1000]: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool): view
    def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_n_underlying_coins(_pool: address) -> uint256: view
    def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]: view


ADDRESS_PROVIDER: public(immutable(AddressProvider))
METAREGISTRY_ID: constant(uint256) = 7


@external
def __init__(address_provider: address):
    ADDRESS_PROVIDER = AddressProvider(address_provider)

# Quote View method

@external
@view
def get_quotes(source_token: address, destination_token: address, amount_in: uint256) -> DynArray[Quote, MAX_QUOTES]:

    quotes: DynArray[Quote, MAX_QUOTES] = []
    metaregistry: Metaregistry = Metaregistry(ADDRESS_PROVIDER.get_address(METAREGISTRY_ID))
    pools: DynArray[address, 1000] = metaregistry.find_pools_for_coins(source_token, destination_token)

    if len(pools) == 0:
        return quotes

    # get  pool types for each pool
    for pool in pools:

        # is it a stableswap pool? are the coin pairs part of a metapool?
        pool_type: uint8 = self._get_pool_type(pool, metaregistry)

        # get coin indices
        i: uint256 = 0
        j: uint256 = 0
        is_underlying: uint256 = False
        (i, j, is_underlying) = metaregistry.get_coin_indices(pool, source_token, destination_token)

        # get balances
        balances: uint256[MAX_COINS] = metaregistry.get_underlying_balances(pool)

        # if pool is too small, dont post call and skip pool:
        if balances[source_token_index] <= amount_in:
            continue

        # do a get_dy call and only save quote if call does not bork; use correct abi (in128 vs uint256)
        success: bool = False
        response: Bytes[32] = b""

        method_abi: String[50] = ""
        if pool_type == 0 and is_stableswap_metapool:
            method_abi = "get_dy_underlying(int128,int128,uint256)"
        elif pool_type == 0 and not is_underlying:
            method_abi = "get_dy(int128,int128,uint256)"
        else:
            method_abi = "get_dy(uint256,uint256,uint256)"

        success, response = raw_call(
            pool,
            concat(
                method_id(method_abi),
                convert(i, bytes32),
                convert(j, bytes32),
                convert(amount_in, bytes32),
            ),
            max_outsize=32,
            revert_on_failure=False,
            is_static_call=True
        )

        # check if get_dy works and if so, append quote to dynarray
        if success:
            quotes.append(
                Quote(
                    {
                        source_token_index: i,
                        dest_token_index: j,
                        is_underlying: is_underlying,
                        amount_out: convert(response, uint256),
                        pool: pool,
                        pool_balances: balances,
                        pool_type: pool_type
                    }
                )
            )

    return quotes

# Internal methods

@internal
@view
def _get_pool_type(pool: address, metaregistry: Metaregistry) -> uint8
    # 0 for stableswap, 1 for cryptoswap, 2 for LLAMMA.

    success: bool = False
    response: Bytes[32] = b""

    # check if cryptoswap
    success, response = raw_call(
        pool,
        method_id("allowed_extra_profit"),
        max_outsize=32,
        revert_on_failure=False,
        is_static_call=True
    )
    if success:
        return 1

    # check if llamma
    success, response = raw_call(
        pool,
        method_id("get_rate_mul"),
        max_outsize=32,
        revert_on_failure=False,
        is_static_call=True
    )
    if success:
        return 2

    return 0
