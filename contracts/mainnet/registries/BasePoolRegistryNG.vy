#pragma version ^0.3.7
"""
@title CurveBasePoolRegistryv2
@license MIT
@author Curve.Fi
"""
MAX_COINS: constant(uint256) = 8


struct BasePool:
    location: uint256
    lp_token: address
    n_coins: uint256
    is_v2: bool
    is_legacy: bool
    is_lending: bool

struct NGBasePoolArray:
    lp_token: address
    coins: DynArray[address, MAX_COINS]
    decimals: uint256
    n_coins: uint256
    asset_types: DynArray[uint8, MAX_COINS]


interface AddressProvider:
    def admin() -> address: view

interface ERC20:
    def decimals() -> uint256: view

interface CurvePoolLegacy:
    def coins(i: int128) -> address: view

interface CurvePool:
    def coins(i: uint256) -> address: view
    def N_COINS() -> uint256: view

interface CurveStableswapNGFactory:
    def base_pool_count() -> uint256: view
    def base_pool_list(i: uint256) -> address: view
    def get_coins(_pool: address) -> DynArray[address, MAX_COINS]: view
    def base_pool_data(_pool: address) -> NGBasePoolArray: view


event BasePoolAdded:
    basepool: indexed(address)


event BasePoolRemoved:
    basepool: indexed(address)


stableswap_ng_factory: public(immutable(CurveStableswapNGFactory))
admin: public(address)
future_admin: public(address)

manually_added_base_pool: HashMap[address, BasePool]
manually_added_base_pool_list: address[10000]
manually_added_base_pool_for_lp_token: HashMap[address, address]
manually_added_base_pool_count: uint256
last_updated: public(uint256)  # last manual update!


@external
def __init__(_stableswap_ng_factory: address):
    self.admin = msg.sender
    stableswap_ng_factory = CurveStableswapNGFactory(_stableswap_ng_factory)


@internal
@view
def _pool_is_ng(_pool: address) -> bool:

    # Check if pool is from stableswap ng factory:
    return raw_call(
        stableswap_ng_factory.address,
        concat(
            method_id('get_n_coins(address)'),
            convert(_pool, bytes32),
        ),
        revert_on_failure=False,
        is_static_call=True,
    )


@internal
@view
def _pool_is_ng_basepool(_pool: address) -> bool:

    # Check if pool is a base pool on stableswap ng factory:
    if stableswap_ng_factory.base_pool_data(_pool).n_coins > 0:
        return True

    return False


@internal
@view
def _get_basepool_coins(_pool: address) -> DynArray[address, MAX_COINS]:

    if self._pool_is_ng(_pool):
        return stableswap_ng_factory.get_coins(_pool)

    _coins: DynArray[address, MAX_COINS] = []
    _n_coins: uint256 = self.manually_added_base_pool[_pool].n_coins
    _is_legacy: bool = self.manually_added_base_pool[_pool].is_legacy
    for i in range(_n_coins, bound=MAX_COINS):

        if _is_legacy:
            _coins.append(CurvePoolLegacy(_pool).coins(convert(i, int128)))
        else:
            _coins.append(CurvePool(_pool).coins(i))

    return _coins


@internal
@view
def _get_base_pools() -> DynArray[address, 10000]:

    # manually added base pools are listed first:
    __base_pool_list: DynArray[address, 10000] = []

    for i in range(self.manually_added_base_pool_count, bound=10000):
        __base_pool_list.append(self.manually_added_base_pool_list[i])

    for j in range(stableswap_ng_factory.base_pool_count(), bound=10000):
        stableswap_factory_ng_base_pool: address = stableswap_ng_factory.base_pool_list(j)
        if stableswap_factory_ng_base_pool not in __base_pool_list:
            __base_pool_list.append(stableswap_factory_ng_base_pool)

    return __base_pool_list


@internal
@view
def _base_pool_list(i: uint256) -> address:
    return self._get_base_pools()[i]


@internal
@view
def _base_pool_count() -> uint256:
    return len(self._get_base_pools())


@internal
@view
def _get_base_pool_for_lp_token(_lp_token: address) -> address:

    base_pool: address = self.manually_added_base_pool_for_lp_token[_lp_token]

    if base_pool != empty(address):

        return base_pool

    elif (
        base_pool == empty(address) and 
        self._pool_is_ng(_lp_token) and 
        self._pool_is_ng_basepool(_lp_token)
    ):
        return _lp_token

    return empty(address)


@internal
@view
def _get_basepools_for_coin(_coin: address) -> DynArray[address, 1000]:
    """
    @notice Gets the base pool for a coin
    @dev Some coins can be in multiple base pools, this function returns
         the base pool with the input coin as an underlying asset
    @param _coin Address of the coin
    @return basepool addresses
    """
    _base_pools: DynArray[address, 10000] = self._get_base_pools()
    _base_pools_for_coin: DynArray[address, 1000] = []
    for _pool in _base_pools:
        _coins: DynArray[address, MAX_COINS] = self._get_basepool_coins(_pool)
        if _coin in _coins:
            _base_pools_for_coin.append(_pool)

    return _base_pools_for_coin


# ------- public view methods --------


@external
@view
def get_base_pool_for_lp_tokens(_lp_token: address) -> address:
    """
    @notice Gets pool address for lp token
    @param _pool Address of the base pool
    @return address address of the base pool
    """
    return self._get_base_pool_for_lp_token(_lp_token)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    """
    @notice Gets the number of coins in a base pool
    @param _pool Address of the base pool
    @return uint256 number of coins
    """

    n_coins: uint256 = self.manually_added_base_pool[_pool].n_coins
    
    if not n_coins == 0:
        
        return n_coins

    elif (
        n_coins == 0 and 
        self._pool_is_ng(_pool) and 
        self._pool_is_ng_basepool(_pool)
    ):
    
        return CurvePool(_pool).N_COINS()
    
    else:  # pool is not registered, so register it first

        return 0


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Gets coins in a base pool
    @param _pool Address of the base pool
    @return address[MAX_COINS] with coin addresses
    """
    coins: DynArray[address, MAX_COINS] = self._get_basepool_coins(_pool)
    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    for i in range(len(coins), bound=MAX_COINS):
        _coins[i] = coins[i]
    return _coins


@external
@view
def get_basepool_for_coin(_coin: address, _idx: uint256 = 0) -> address:
    """
    @notice Gets the base pool for a coin
    @dev Some coins can be in multiple base pools, this function returns
         the base pool for a coin at a specific index
    @param _coin Address of the coin
    @param _idx Index of base pool that holds the coin
    @return basepool address
    """
    return self._get_basepools_for_coin(_coin)[_idx]


@external
@view
def get_basepools_for_coin(_coin: address) -> DynArray[address, 1000]:
    """
    @notice Gets the base pool for a coin
    @dev Some coins can be in multiple base pools, this function returns
         the base pool for a coin at a specific index
    @param _coin Address of the coin
    @return basepool addresses
    """
    return self._get_basepools_for_coin(_coin)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Gets decimals of coins in a base pool
    @param _pool Address of the base pool
    @return uint256[MAX_COINS] containing coin decimals
    """
    _coins: DynArray[address, MAX_COINS] = self._get_basepool_coins(_pool)
    _decimals: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    for i in range(MAX_COINS):
        if _coins[i] == empty(address):
            break
        if _coins[i] == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
            _decimals[i] = 18
        else:
            _decimals[i] = ERC20(_coins[i]).decimals()

    return _decimals


@external
@view
def get_lp_token(_pool: address) -> address:
    """
    @notice Gets the LP token of a base pool
    @param _pool Address of the base pool
    @return address of the LP token
    """
    lp_token: address = self.manually_added_base_pool[_pool].lp_token
    if lp_token != empty(address):
        return lp_token

    if self._pool_is_ng_basepool(_pool):
        return stableswap_ng_factory.base_pool_data(_pool).lp_token

    return empty(address)


@external
@view
def is_legacy(_pool: address) -> bool:
    """
    @notice Checks if a base pool uses Curve's legacy abi
    @dev Legacy abi includes int128 indices whereas the newer
         abi uses uint256 indices
    @param _pool Address of the base pool
    @return bool True if legacy abi is used
    """
    # Will return false if it is an ng pool (not manually registered)
    return self.manually_added_base_pool[_pool].is_legacy


@external
@view
def is_v2(_pool: address) -> bool:
    """
    @notice Checks if a base pool is a Curve CryptoSwap pool
    @param _pool Address of the base pool
    @return bool True if the pool is a Curve CryptoSwap pool
    """
    # Will return false if it is an ng pool (not manually registered)
    return self.manually_added_base_pool[_pool].is_v2


@external
@view
def is_lending(_pool: address) -> bool:
    """
    @notice Checks if a base pool is a Curve Lending pool
    @param _pool Address of the base pool
    @return bool True if the pool is a Curve Lending pool
    """
    # Will return false if it is an ng pool (not manually registered)
    return self.manually_added_base_pool[_pool].is_lending


# ----------- Admin methods ----------

@external
def add_custom_base_pool(
    _pool: address, 
    _lp_token: address, 
    _n_coins: uint256, 
    _is_legacy: bool, 
    _is_lending: bool, 
    _is_v2: bool
):
    """
    @notice Add a base pool to the registry
    @param _pool Address of the base pool
    @param _lp_token Address of the LP token
    @param _n_coins Number of coins in the base pool
    @param _is_legacy True if the base pool uses legacy abi
    @param _is_lending True if the base pool is a Curve Lending pool
    @param _is_v2 True if the base pool is a Curve CryptoSwap pool
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.manually_added_base_pool[_pool].lp_token == empty(address)  # dev: pool exists

    # add pool to base_pool_list
    manually_added_base_pool_count: uint256 = self.manually_added_base_pool_count
    self.manually_added_base_pool[_pool].location = manually_added_base_pool_count
    self.manually_added_base_pool[_pool].lp_token = _lp_token
    self.manually_added_base_pool[_pool].n_coins = _n_coins
    self.manually_added_base_pool[_pool].is_v2 = _is_v2
    self.manually_added_base_pool[_pool].is_legacy = _is_legacy
    self.manually_added_base_pool[_pool].is_lending = _is_lending

    # for reverse lookup:
    self.manually_added_base_pool_for_lp_token[_lp_token] = _pool

    self.last_updated = block.timestamp
    self.manually_added_base_pool_list[manually_added_base_pool_count] = _pool
    self.manually_added_base_pool_count = manually_added_base_pool_count + 1
    log BasePoolAdded(_pool)


@external
def remove_custom_base_pool(_pool: address):
    """
    @notice Remove a base pool from the registry
    @param _pool Address of the base pool
    """
    assert msg.sender == self.admin # dev: admin-only function
    assert _pool != empty(address)
    assert self.manually_added_base_pool[_pool].lp_token != empty(address)  # dev: pool doesn't exist

    # reset pool <> lp_token mappings
    self.manually_added_base_pool_for_lp_token[self.manually_added_base_pool[_pool].lp_token] = empty(address)
    self.manually_added_base_pool[_pool].lp_token = empty(address)
    self.manually_added_base_pool[_pool].n_coins = 0

    # remove base_pool from base_pool_list
    location: uint256 = self.manually_added_base_pool[_pool].location
    length: uint256 = self.manually_added_base_pool_count - 1
    assert location < length

    # because self.base_pool_list is a static array,
    # we can replace the last index with empty(address)
    # and replace the first index with the base pool
    # that was previously in the last index.
    # we skip this step if location == last index
    if location < length:
        # replace _pool with final value in pool_list
        addr: address = self.manually_added_base_pool_list[length]
        assert addr != empty(address)
        self.manually_added_base_pool_list[location] = addr
        self.manually_added_base_pool[addr].location = location

    # delete final pool_list value
    self.manually_added_base_pool_list[length] = empty(address)
    self.manually_added_base_pool_count = length

    self.last_updated = block.timestamp
    log BasePoolRemoved(_pool)


@external
def commit_transfer_ownership(_addr: address):
    """
    @notice Transfer ownership of this contract to `addr`
    @param _addr Address of the new owner
    """
    assert msg.sender == self.admin  # dev: admin only
    self.future_admin = _addr


@external
def accept_transfer_ownership():
    """
    @notice Accept a pending ownership transfer
    @dev Only callable by the new owner
    """
    _admin: address = self.future_admin
    assert msg.sender == _admin  # dev: future admin only

    self.admin = _admin
    self.future_admin = empty(address)
