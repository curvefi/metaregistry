# @version 0.3.3
"""
@title Curve BasePool Registry
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


interface AddressProvider:
    def admin() -> address: view


interface ERC20:
    def decimals() -> uint256: view


interface CurvePoolLegacy:
    def coins(i: int128) -> address: view


interface CurvePool:
    def coins(i: uint256) -> address: view


event BasePoolAdded:
    basepool: indexed(address)


event BasePoolRemoved:
    basepool: indexed(address)


ADDRESS_PROVIDER: constant(address) = 0x0000000022D53366457F9d5E68Ec105046FC4383
base_pool: HashMap[address, BasePool]
base_pool_list: public(address[100])
get_base_pool_for_lp_token: public(HashMap[address, address])
base_pool_count: public(uint256)
last_updated: public(uint256)


@internal
@view
def _get_basepool_coins(_pool: address) -> address[MAX_COINS]:
    _n_coins: uint256 = self.base_pool[_pool].n_coins
    _is_legacy: bool = self.base_pool[_pool].is_legacy
    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    for i in range(MAX_COINS):
        if i == _n_coins:
            break

        if _is_legacy:
            _coins[i] = CurvePoolLegacy(_pool).coins(convert(i, int128))
        else:
            _coins[i] = CurvePool(_pool).coins(i)

    return _coins


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    return self._get_basepool_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    _coins: address[MAX_COINS] = self._get_basepool_coins(_pool)
    _decimals: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    for i in range(MAX_COINS):
        if _coins[i] == ZERO_ADDRESS:
            break
        if _coins[i] == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
            _decimals[i] = 18
        else:
            _decimals[i] = ERC20(_coins[i]).decimals()

    return _decimals


@external
@view
def get_lp_token(_pool: address) -> address:
    return self.base_pool[_pool].lp_token


@external
@view
def get_n_coins(_pool: address) -> uint256:
    return self.base_pool[_pool].n_coins


@external
@view
def get_location(_pool: address) -> uint256:
    return self.base_pool[_pool].location


@external
@view
def is_legacy(_pool: address) -> bool:
    return self.base_pool[_pool].is_legacy


@external
@view
def is_v2(_pool: address) -> bool:
    return self.base_pool[_pool].is_v2


@external
@view
def is_lending(_pool: address) -> bool:
    return self.base_pool[_pool].is_lending


@external
def add_base_pool(_pool: address, _lp_token: address, _n_coins: uint256, _is_legacy: bool, _is_lending: bool, _is_v2: bool):
    """
    @notice Add a base pool to the registry
    @dev this is needed since paired base pools might be in a different registry
    """
    assert msg.sender == AddressProvider(ADDRESS_PROVIDER).admin()  # dev: admin-only function
    assert self.base_pool[_pool].lp_token == ZERO_ADDRESS  # dev: pool exists

    # add pool to base_pool_list
    base_pool_count: uint256 = self.base_pool_count
    self.base_pool[_pool].location = base_pool_count
    self.base_pool[_pool].lp_token = _lp_token
    self.base_pool[_pool].n_coins = _n_coins
    self.base_pool[_pool].is_v2 = _is_v2
    self.base_pool[_pool].is_legacy = _is_legacy
    self.base_pool[_pool].is_lending = _is_lending

    # for reverse lookup:
    self.get_base_pool_for_lp_token[_lp_token] = _pool

    self.last_updated = block.timestamp
    self.base_pool_list[base_pool_count] = _pool
    self.base_pool_count = base_pool_count + 1
    log BasePoolAdded(_pool)


@external
def remove_base_pool(_pool: address):
    assert msg.sender == AddressProvider(ADDRESS_PROVIDER).admin()  # dev: admin-only function
    assert _pool != ZERO_ADDRESS
    assert self.base_pool[_pool].lp_token != ZERO_ADDRESS  # dev: pool doesn't exist

    # reset pool <> lp_token mappings
    self.get_base_pool_for_lp_token[self.base_pool[_pool].lp_token] = ZERO_ADDRESS
    self.base_pool[_pool].lp_token = ZERO_ADDRESS

    # remove base_pool from base_pool_list
    location: uint256 = self.base_pool[_pool].location
    length: uint256 = self.base_pool_count - 1

    self.base_pool_count = length

    # we set ZERO_ADDRESS at _pool's location
    self.base_pool_list[location] = ZERO_ADDRESS
    self.base_pool[_pool].n_coins = 0

    self.last_updated = block.timestamp
    log BasePoolRemoved(_pool)
