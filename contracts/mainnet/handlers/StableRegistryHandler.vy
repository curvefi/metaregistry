# @version 0.3.3
"""
@title Curve Registry Handler for v1 Registry
@license MIT
"""

# ---- interface ---- #
interface AddressProvider:
    def get_address(_id: uint256) -> address: view


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


interface MetaRegistry:
    def registry_length() -> uint256: view


# ---- constants ---- #
MAX_COINS: constant(uint256) = 8


# ---- storage variables ---- #
base_registry: public(BaseRegistry)
registry_id: uint256
registry_index: uint256


# ---- constructor ---- #
@external
def __init__(_metaregistry: address, _id: uint256, address_provider: address):
    self.base_registry = BaseRegistry(AddressProvider(address_provider).get_address(_id))
    self.registry_id = _id
    self.registry_index = MetaRegistry(_metaregistry).registry_length()


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
    return self.base_registry.find_pool_for_coins(_from, _to, i)


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_admin_balances(_pool)


@external
@view
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_balances(_pool)


@external
@view
def get_base_pool(_pool: address) -> address:
    if not(self._is_meta(_pool)):
        return ZERO_ADDRESS
    return CurvePool(_pool).base_pool()


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    return self.base_registry.get_coin_indices(_pool, _from, _to)


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    return self.base_registry.get_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_decimals(_pool)


@external
@view
def get_fees(_pool: address) -> uint256[10]:
    fees: uint256[10] = empty(uint256[10])
    pool_fees: uint256[2] = self.base_registry.get_fees(_pool)
    for i in range(2):
        fees[i] = pool_fees[i]
    return fees


@external
@view
def get_gauges(_pool: address) -> (address[10], int128[10]):
    return self.base_registry.get_gauges(_pool)


@external
@view
def get_lp_token(_pool: address) -> address:
    return self.base_registry.get_lp_token(_pool)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    return self._get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    return self.base_registry.get_n_coins(_pool)[1]


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    return self.base_registry.get_pool_asset_type(_pool)


@external
@view
def get_pool_from_lp_token(_lp_token: address) -> address:
    return self.base_registry.get_pool_from_lp_token(_lp_token)


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    return self.base_registry.get_pool_name(_pool)


@external
@view
def get_pool_params(_pool: address) -> uint256[20]:
    stableswap_pool_params: uint256[20] = empty(uint256[20])
    stableswap_pool_params[0] = self.base_registry.get_A(_pool)
    return stableswap_pool_params


@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    if not self._is_meta(_pool):
        return self.base_registry.get_balances(_pool)
    return self.base_registry.get_underlying_balances(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_COINS]:
    """
    @dev does't do
        `if not self._is_meta(_pool)`
        `    return self.base_registry.get_coins(_pool)`
        because that will exclude lending pools which have
        underlying coins.
    """
    return self.base_registry.get_underlying_coins(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]:
    if not self._is_meta(_pool):
        return self.base_registry.get_decimals(_pool)
    return self.base_registry.get_underlying_decimals(_pool)


@external
@view
def get_virtual_price_from_lp_token(_token: address) -> uint256:
    return self.base_registry.get_virtual_price_from_lp_token(_token)


@external
@view
def is_meta(_pool: address) -> bool:
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
    return self.base_registry.pool_count()


@external
@view
def pool_list(_index: uint256) -> address:
    return self.base_registry.pool_list(_index)
