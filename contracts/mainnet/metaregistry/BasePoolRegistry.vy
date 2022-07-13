# @version 0.3.3
"""
@title Curve BasePool Registry
@license MIT
@author Curve.Fi
"""
MAX_COINS: constant(int128) = 8


struct BasePool:
    lp_token: address
    coins: address[MAX_COINS]
    is_v2: bool


interface AddressProvider:
    def admin() -> address: view


interface ERC20:
    def decimals() -> uint256: view


interface CurvePool():
    def coins(i: uint256) -> address: view


event BasePoolAdded:
    basepool: indexed(address)


ADDRESS_PROVIDER: immutable(address)
base_pool: HashMap[address, BasePool]
get_base_pool_for_lp_token: public(HashMap[address, address])
base_pool_count: public(uint256)
last_updated: public(uint256)


@external
def __init__(_address_provider: address):
    """
    @notice Constructor function
    """
    ADDRESS_PROVIDER = _address_provider


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    return self.base_pool[_pool].coins


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    _coins: address[MAX_COINS] = self.base_pool[_pool].coins
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
def get_n_coins(_pool: address) -> uint256:
    _coins: address[MAX_COINS] = self.base_pool[_pool].coins
    for i in range(MAX_COINS):
        if _coins[i] == ZERO_ADDRESS:
            return convert(i, uint256) + 1

    raise


@internal
@view
def _get_basepool_coins(_pool: address) -> address[MAX_COINS]:

    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    _coin: address = ZERO_ADDRESS
    for i in range(MAX_COINS):
        success: bool = False
        response: Bytes[32] = b""
        success, response = raw_call(
            _pool,
            concat(
                method_id("coins(uint256"),
                convert(i, bytes32)
            ),
            max_outsize=32,
            revert_on_failure=False,
            is_static_call=True
        )
        if not success:
            break
        _coins[i] = convert(response, address)

    return _coins


@external
def add_base_pool(_pool: address, _lp_token: address) -> bool:
    """
    @notice Add a base pool to the registry
    @dev this is needed since paired base pools might be in a different registry
    """
    assert msg.sender == AddressProvider(ADDRESS_PROVIDER).admin()  # dev: admin-only function
    assert ZERO_ADDRESS not in [_pool, _lp_token]
    assert self.base_pool[_pool].coins[0] == ZERO_ADDRESS  # dev: pool exists
    assert self.base_pool[_pool].lp_token == ZERO_ADDRESS  # dev: pool exists


    # add pool to base_pool_list
    base_pool_count: uint256 = self.base_pool_count
    self.base_pool[_pool].lp_token = _lp_token

    # for reverse lookup:
    self.get_base_pool_for_lp_token[_lp_token] = _pool
    self.base_pool[_pool].coins = self._get_basepool_coins(_pool)

    # check if pool is a v2 pool:
    success: bool = False
    response: Bytes[32] = b""
    success, response = raw_call(
        _pool,
        method_id("gamma"),
        max_outsize=32,
        revert_on_failure=False,
        is_static_call=True
    )
    self.base_pool[_pool].is_v2 = success

    self.last_updated = block.timestamp
    self.base_pool_count = base_pool_count + 1
    log BasePoolAdded(_pool)

    return True
