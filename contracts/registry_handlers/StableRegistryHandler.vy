# pragma version 0.3.10
# pragma evm-version paris
"""
@title Curve Registry Handler for v1 Registry
@license MIT
"""
# ---- interface ---- #
interface BaseRegistry:
    def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address: view
    def get_admin_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_A(_pool: address) -> uint256: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool): view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_fees(_pool: address) -> uint256[2]: view
    def get_gauges(_pool: address) -> (address[10], int128[10]): view
    def get_lp_token(_pool: address) -> address: view
    def get_n_coins(_pool: address) -> uint256[2]: view
    def get_pool_asset_type(_pool: address) -> uint256: view
    def get_pool_from_lp_token(_lp_token: address) -> address: view
    def get_pool_name(_pool: address) -> String[64]: view
    def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_underlying_coins(_pool: address) -> address[MAX_COINS]: view
    def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_virtual_price_from_lp_token(_token: address) -> uint256: view
    def is_meta(_pool: address) -> bool: view
    def pool_count() -> uint256: view
    def pool_list(pool_id: uint256) -> address: view


interface CurvePool:
    def base_pool() -> address: view

interface ERC20:
    def decimals() -> uint256: view


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
def _get_n_coins(_pool: address) -> uint256:
    return self.base_registry.get_n_coins(_pool)[0]


@internal
@view
def _is_meta(_pool: address) -> bool:
    return self.base_registry.is_meta(_pool)


# ---- view methods (API) of the contract ---- #
@external
@view
def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address:
    """
    @notice Find the pool that has the given coins.
    @param _from address of coin.
    @param _to address of coin.
    @param i index of list of found pools to return
    @return address of pool at index `i` of pools that hold the two coins
    """
    return self.base_registry.find_pool_for_coins(_from, _to, i)


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the admin balances of the given pool.
    @param _pool address of pool.
    @return admin balances of the pool.
    """
    return self.base_registry.get_admin_balances(_pool)


@external
@view
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the balances of the given pool.
    @param _pool address of pool.
    @return balances of the pool.
    """
    return self.base_registry.get_balances(_pool)


@external
@view
def get_base_pool(_pool: address) -> address:
    """
    @notice Get the base pool of the given pool.
    @param _pool address of pool.
    @return base pool of the pool.
    """
    if not(self._is_meta(_pool)):
        return empty(address)
    return self.base_registry.get_pool_from_lp_token(self.base_registry.get_coins(_pool)[1])


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    """
    @notice Get the indices of the given coins in the given pool.
    @param _pool address of pool.
    @param _from address of coin.
    @param _to address of coin.
    @return index of _from, index of _to, bool indicating whether the
            coins are in an underlying market
    """
    return self.base_registry.get_coin_indices(_pool, _from, _to)


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the coins of the given pool.
    @param _pool address of pool.
    @return coins of the pool.
    """
    return self.base_registry.get_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the decimals of the coins in given pool.
    @param _pool address of pool.
    @return decimals of the coins in the pool.
    """
    return self.base_registry.get_decimals(_pool)


@external
@view
def get_fees(_pool: address) -> uint256[10]:
    """
    @notice Get the fees of the given pool.
    @param _pool address of pool.
    @return fees of the pool.
    """
    fees: uint256[10] = empty(uint256[10])
    pool_fees: uint256[2] = self.base_registry.get_fees(_pool)
    for i in range(2):
        fees[i] = pool_fees[i]
    return fees


@external
@view
def get_gauges(_pool: address) -> (address[10], int128[10]):
    """
    @notice Get the gauges and gauge types of the given pool.
    @param _pool address of pool.
    @return gauges of the pool.
    """
    return self.base_registry.get_gauges(_pool)


@external
@view
def get_lp_token(_pool: address) -> address:
    """
    @notice Get the LP token of the given pool.
    @param _pool address of pool.
    @return LP token of the pool.
    """
    return self.base_registry.get_lp_token(_pool)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    """
    @notice Get the number of coins in the given pool.
    @param _pool address of pool.
    @return number of coins in the pool.
    """
    return self._get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    """
    @notice Get the number of underlying coins in the given pool.
    @param _pool address of pool.
    @return number of underlying coins in the pool.
    """
    return self.base_registry.get_n_coins(_pool)[1]


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    """
    @notice Get the asset type of coins in a given pool.
    @dev 0 = USD, 1 = ETH, 2 = BTC, 3 = Other
    @param _pool address of pool.
    @return asset type of the pool.
    """
    return self.base_registry.get_pool_asset_type(_pool)


@external
@view
def get_pool_from_lp_token(_lp_token: address) -> address:
    """
    @notice Get the pool of the given LP token.
    @param _lp_token address of LP token.
    @return pool of the LP token.
    """
    return self.base_registry.get_pool_from_lp_token(_lp_token)


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    """
    @notice Get the name of the given pool.
    @param _pool address of pool.
    @return name of the pool.
    """
    return self.base_registry.get_pool_name(_pool)


@external
@view
def get_pool_params(_pool: address) -> uint256[20]:
    """
    @notice Get the parameters of the given pool.
    @param _pool address of pool.
    @return parameters of the pool.
    """
    stableswap_pool_params: uint256[20] = empty(uint256[20])
    stableswap_pool_params[0] = self.base_registry.get_A(_pool)
    return stableswap_pool_params


@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the underlying balances of the given pool.
    @dev returns coin balances if pool is not a metapool
    @param _pool address of pool.
    @return underlying balances of the pool.
    """
    if not self._is_meta(_pool):
        return self.base_registry.get_balances(_pool)
    return self.base_registry.get_underlying_balances(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the underlying coins of the given pool.
    @dev For pools that do not lend, the base registry returns the
         same value as `get_coins`
    @param _pool address of pool.
    @return underlying coins of the pool.
    """
    return self.base_registry.get_underlying_coins(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the underlying decimals of coins in the given pool.
    @param _pool address of pool.
    @return underlying decimals of the coins in the pool.
    """
    coin_decimals: uint256[MAX_COINS] = self.base_registry.get_decimals(_pool)
    underlying_coin_decimals: uint256[MAX_COINS] = self.base_registry.get_underlying_decimals(_pool)

    # this is a check for cases where base_registry.get_underlying_decimals
    # returns wrong values but base_registry.get_decimals is the right one:
    for i in range(MAX_COINS):
        if underlying_coin_decimals[i] == 0:
            underlying_coin_decimals[i] = coin_decimals[i]

    return underlying_coin_decimals


@external
@view
def get_virtual_price_from_lp_token(_token: address) -> uint256:
    """
    @notice Get the virtual price of the given LP token.
    @param _token address of LP token.
    @return virtual price of the LP token.
    """
    return self.base_registry.get_virtual_price_from_lp_token(_token)


@external
@view
def is_meta(_pool: address) -> bool:
    """
    @notice Check if the given pool is a metapool.
    @param _pool address of pool.
    @return true if the pool is a metapool.
    """
    return self._is_meta(_pool)


@external
@view
def is_registered(_pool: address) -> bool:
    """
    @notice Check if a pool belongs to the registry using get_n_coins
    @param _pool The address of the pool
    @return A bool corresponding to whether the pool belongs or not
    """
    return self._get_n_coins(_pool) > 0


@external
@view
def pool_count() -> uint256:
    """
    @notice Get the number of pools in the registry.
    @return number of pools in the registry.
    """
    return self.base_registry.pool_count()


@external
@view
def pool_list(_index: uint256) -> address:
    """
    @notice Get the address of the pool at the given index.
    @param _index index of the pool.
    @return address of the pool.
    """
    return self.base_registry.pool_list(_index)
