# @version 0.3.3
"""
@title api for coin
@license MIT
@author fiddy
"""

interface ERC20:
    def decimals() -> uint256: view

interface Pool:
    def coins(id: uint256) -> address: view
    def get_virtual_price() -> uint256: view


MAX_COINS: constant(uint256) = 4


@external
def __init__():
    pass


@internal
@view
def _get_coin_decimal(coin: address) -> uint256:
    return ERC20(coin).decimals()


@external
@view
def get_decimals_for_coin_in_pool(pool: address, coin_id: uint256) -> uint256:
    coin: address = Pool(pool).coins(coin_id)
    if coin == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        return 18
    return self._get_coin_decimal(coin)


@external
@view
def get_virtual_price(_pool: address) -> uint256:
    return Pool(_pool).get_virtual_price()


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    coins: address[MAX_COINS] = empty(address[MAX_COINS])
    success: bool = False
    response: Bytes[32] = b""
    for i in range(MAX_COINS):

        success, response = raw_call(
            _pool,
            concat(
                method_id("coins(uint256)"),
                convert(i, bytes32),
            ),
            max_outsize=32,
            revert_on_failure=False,
            is_static_call=True
        )

        if success:
            coins[i] = convert(response, address)
        else:
            coins[i] = ZERO_ADDRESS

    return coins


@external
@view
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    balances: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    success: bool = False
    response: Bytes[32] = b""
    for i in range(MAX_COINS):

        success, response = raw_call(
            _pool,
            concat(
                method_id("balances(uint256)"),
                convert(i, bytes32),
            ),
            max_outsize=32,
            revert_on_failure=False,
            is_static_call=True
        )

        if success:
            balances[i] = convert(response, uint256)
        else:
            balances[i] = 0

    return balances
