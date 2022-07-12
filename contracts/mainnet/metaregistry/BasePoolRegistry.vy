# @version 0.3.3
"""
@title Curve CryptoSwap Registry
@license MIT
@author Curve.Fi
"""
MAX_COINS: constant(int128) = 8


struct BasePool:
    location: uint256
    lp_token: address
    coins: address[MAX_COINS]
    decimals: uint256[MAX_COINS]
    n_coins: uint256
    is_legacy: bool
    name: String[64]


interface AddressProvider:
    def admin() -> address: view
    def get_address(_id: uint256) -> address: view
    def get_registry() -> address: view


interface ERC20:
    def balanceOf(_addr: address) -> uint256: view
    def decimals() -> uint256: view
    def totalSupply() -> uint256: view


event BasePoolAdded:
    basepool: indexed(address)


admin: public(address)
base_pool_data: HashMap[address, BasePool]
get_base_pool_for_lp_token: public(HashMap[address, address])
base_pool_count: public(uint256)
last_updated: public(uint256)


@external
def __init__(_address_provider: address):
    """
    @notice Constructor function
    """
    self.admin = AddressProvider(_address_provider).admin()


@view
@external
def get_base_pool_data(_base_pool: address) -> BasePool:
    return self.base_pool_data[_base_pool]


@external
def add_base_pool(_pool: address, _lp_token: address, _coins: address[MAX_COINS], _name: String[64]):
    """
    @notice Add a base pool to the registry
    @dev this is needed since paired base pools might be in a different registry
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert ZERO_ADDRESS not in [_pool, _lp_token]
    assert self.base_pool_data[_pool].coins[0] == ZERO_ADDRESS  # dev: pool exists
    assert self.base_pool_data[_pool].lp_token == ZERO_ADDRESS  # dev: pool exists

    # add pool to base_pool_list
    base_pool_count: uint256 = self.base_pool_count
    self.base_pool_data[_pool].location = base_pool_count + 1
    self.base_pool_data[_pool].coins = _coins
    self.base_pool_data[_pool].name = _name
    self.base_pool_data[_pool].lp_token = _lp_token

    # for reverse lookup:
    self.get_base_pool_for_lp_token[_lp_token] = _pool

    _decimals: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    for i in range(MAX_COINS):
        if _coins[i] == ZERO_ADDRESS:
            self.base_pool_data[_pool].n_coins = convert(i, uint256) + 1
            break
        if _coins[i] == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
            _decimals[i] = 18
        else:
            _decimals[i] = ERC20(_coins[i]).decimals()

    self.base_pool_data[_pool].decimals = _decimals

    # check if pool uses int128 or uint256 for indices:
    success: bool = False
    response: Bytes[32] = b""
    success, response = raw_call(
        _pool,
        concat(
            method_id("balances(int128)"),
            convert(0, bytes32),
        ),
        max_outsize=32,
        revert_on_failure=False,
        is_static_call=True
    )

    if success:
        self.base_pool_data[_pool].is_legacy = False
    else:
        self.base_pool_data[_pool].is_legacy = True

    self.last_updated = block.timestamp
    self.base_pool_count = base_pool_count + 1
    log BasePoolAdded(_pool)