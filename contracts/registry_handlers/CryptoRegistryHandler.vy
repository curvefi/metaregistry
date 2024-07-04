# pragma version 0.3.10
# pragma evm-version paris
"""
@title Curve Registry Handler for v2 Crypto Registry
@license MIT
"""

# ---- interfaces --- #
interface BaseRegistry:
    def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address: view
    def get_admin_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_base_pool(_pool: address) -> address: view
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool): view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_fees(_pool: address) -> uint256[4]: view
    def get_gauges(_pool: address) -> (address[10], int128[10]): view
    def get_lp_token(_pool: address) -> address: view
    def get_n_coins(_pool: address) -> uint256: view
    def get_pool_from_lp_token(_lp_token: address) -> address: view
    def get_pool_name(_pool: address) -> String[64]: view
    def get_n_underlying_coins(_pool: address) -> uint256: view
    def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_underlying_coins(_pool: address) -> address[MAX_COINS]: view
    def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_virtual_price_from_lp_token(_token: address) -> uint256: view
    def is_meta(_pool: address) -> bool: view
    def pool_count() -> uint256: view
    def pool_list(pool_id: uint256) -> address: view


interface CurvePool:
    def adjustment_step() -> uint256: view
    def admin_fee() -> uint256: view
    def allowed_extra_profit() -> uint256: view
    def A() -> uint256: view
    def D() -> uint256: view
    def fee() -> uint256: view
    def fee_gamma() -> uint256: view
    def gamma() -> uint256: view
    def get_virtual_price() -> uint256: view
    def ma_half_time() -> uint256: view
    def mid_fee() -> uint256: view
    def out_fee() -> uint256: view
    def virtual_price() -> uint256: view
    def xcp_profit() -> uint256: view
    def xcp_profit_a() -> uint256: view


interface ERC20:
    def name() -> String[64]: view
    def balanceOf(_addr: address) -> uint256: view
    def totalSupply() -> uint256: view


interface MetaRegistry:
    def registry_length() -> uint256: view


# ---- constants ---- #
MAX_COINS: constant(uint256) = 8

# ---- storage variables ---- #
base_registry: public(BaseRegistry)


# ---- constructor ---- #
@external
def __init__(_base_registry: address):
    self.base_registry = BaseRegistry(_base_registry)


# ---- internal methods ---- #


@internal
@view
def _get_lp_token(_pool: address) -> address:
    return self.base_registry.get_lp_token(_pool)


# ---- view methods (API) of the contract ---- #
@external
@view
def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address:
    """
    @notice Find the pool that has the given coins.
    @param _from The address of the coin holder.
    @param _to The address of the coin holder.
    @param i The index of the pool in the list of pools containing the two coins.
    @return The address of the pool.
    """
    return self.base_registry.find_pool_for_coins(_from, _to, i)


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the admin balances of the given pool.
    @param _pool The address of the pool.
    @return The admin balances of the pool.
    """
    return self.base_registry.get_admin_balances(_pool)


@external
@view
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the balances of the given pool.
    @param _pool The address of the pool.
    @return The balances of the pool.
    """
    return self.base_registry.get_balances(_pool)


@external
@view
def get_base_pool(_pool: address) -> address:
    """
    @notice Get the base pool of the given pool.
    @param _pool The address of the pool.
    @return The base pool of the pool.
    """
    return self.base_registry.get_base_pool(_pool)


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    """
    @notice Get the indices of the coins in the given pool.
    @param _pool The address of the pool.
    @param _from The _from coin address.
    @param _to The _to coin address.
    @return The indices of the coins in the pool.
    """
    return self.base_registry.get_coin_indices(_pool, _from, _to)


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the coins of the given pool.
    @param _pool The address of the pool.
    @return address[MAX_COINS] list of coins in the pool.
    """
    return self.base_registry.get_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the decimals of the given pool.
    @param _pool The address of the pool.
    @return uint256[MAX_COINS] list of decimals of the coins in the pool.
    """
    return self.base_registry.get_decimals(_pool)


@external
@view
def get_fees(_pool: address) -> uint256[10]:
    """
    @notice Get the fees of the given pool.
    @param _pool The address of the pool.
    @return Pool fee as uint256 with 1e10 precision
        Admin fee as 1e10 percentage of pool fee
        Mid fee
        Out fee
    """
    fees: uint256[10] = empty(uint256[10])
    pool_fees: uint256[4] = self.base_registry.get_fees(_pool)
    for i in range(4):
        fees[i] = pool_fees[i]
    return fees


@external
@view
def get_gauges(_pool: address) -> (address[10], int128[10]):
    """
    @notice Get the gauges and gauge_types for a given pool.
    @param _pool The address of the pool.
    @return The gauges of the pool.
    """
    return self.base_registry.get_gauges(_pool)


@external
@view
def get_lp_token(_pool: address) -> address:
    """
    @notice Get the LP token of the given pool.
    @param _pool The address of the pool.
    @return The LP token of the pool.
    """
    return self._get_lp_token(_pool)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    """
    @notice Get the number of coins in the given pool.
    @param _pool The address of the pool.
    @return The number of coins in the pool.
    """
    return self.base_registry.get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    """
    @notice Get the number of underlying coins in the given pool.
    @param _pool The address of the pool.
    @return The number of underlying coins in the pool.
    """
    return self.base_registry.get_n_underlying_coins(_pool)


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    """
    @notice Get the asset type of the given pool.
    @dev Returns 4: 0 = USD, 1 = ETH, 2 = BTC, 3 = Other
    @param _pool The address of the pool.
    @return The asset type of the pool.
    """
    return 4


@external
@view
def get_pool_from_lp_token(_lp_token: address) -> address:
    """
    @notice Get the pool of the given LP token.
    @param _lp_token The address of the LP token.
    @return The address of the pool.
    """
    return self.base_registry.get_pool_from_lp_token(_lp_token)


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    """
    @notice Get the name of the given pool.
    @param _pool The address of the pool.
    @return The name of the pool.
    """
    return self.base_registry.get_pool_name(_pool)


@external
@view
def get_pool_params(_pool: address) -> uint256[20]:
    """
    @notice returns pool params given a cryptopool address
    @dev contains all settable parameter that alter the pool's performance
    @dev only applicable for cryptopools
    @param _pool Address of the pool for which data is being queried.
    """

    pool_params: uint256[20] = empty(uint256[20])
    pool_params[0] = CurvePool(_pool).A()
    pool_params[1] = CurvePool(_pool).D()
    pool_params[2] = CurvePool(_pool).gamma()
    pool_params[3] = CurvePool(_pool).allowed_extra_profit()
    pool_params[4] = CurvePool(_pool).fee_gamma()
    pool_params[5] = CurvePool(_pool).adjustment_step()
    pool_params[6] = CurvePool(_pool).ma_half_time()
    return pool_params


@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the underlying balances of the given pool.
    @param _pool The address of the pool.
    @return The underlying balances of the pool.
    """
    return self.base_registry.get_underlying_balances(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the underlying coins of the given pool.
    @param _pool The address of the pool.
    @return The underlying coins of the pool.
    """
    return self.base_registry.get_underlying_coins(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the underlying decimals of coins in a given pool.
    @param _pool The address of the pool.
    @return The underlying decimals of coins in the pool.
    """
    return self.base_registry.get_underlying_decimals(_pool)


@external
@view
def get_virtual_price_from_lp_token(_token: address) -> uint256:
    """
    @notice Get the virtual price of the given LP token.
    @param _token The address of the LP token.
    @return uint256 The virtual price of the LP token.
    """
    return self.base_registry.get_virtual_price_from_lp_token(_token)


@external
@view
def is_meta(_pool: address) -> bool:
    """
    @notice Check if the given pool is a meta pool.
    @param _pool The address of the pool.
    @return True if the pool is a meta pool, false otherwise.
    """
    return self.base_registry.is_meta(_pool)


@external
@view
def is_registered(_pool: address) -> bool:
    """
    @notice Check if a pool belongs to the registry using get_n_coins
    @param _pool The address of the pool
    @return A bool corresponding to whether the pool belongs or not
    """
    return self.base_registry.get_n_coins(_pool) > 0


@external
@view
def pool_count() -> uint256:
    """
    @notice Get the number of pools in the registry.
    @return The number of pools in the registry.
    """
    return self.base_registry.pool_count()


@external
@view
def pool_list(_index: uint256) -> address:
    """
    @notice Get the address of the pool at the given index.
    @param _index The index of the pool.
    @return The address of the pool.
    """
    return self.base_registry.pool_list(_index)
