# @version 0.3.3
"""
@title Curve Registry Handler for v2 Crypto Registry
@license MIT
"""

# ---- interfaces --- #
interface AddressProvider:
    def get_address(_id: uint256) -> address: view


interface BaseRegistry:
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_admin_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_gauges(_pool: address) -> (address[10], int128[10]): view
    def get_pool_name(_pool: address) -> String[64]: view
    def get_n_coins(_pool: address) -> uint256: view
    def get_lp_token(_pool: address) -> address: view
    def get_virtual_price_from_lp_token(_token: address) -> uint256: view
    def get_fees(_pool: address) -> uint256[4]: view
    def pool_count() -> uint256: view
    def pool_list(pool_id: uint256) -> address: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> uint256[2]: view


interface CurvePool:
    def A() -> uint256: view
    def D() -> uint256: view
    def gamma() -> uint256: view
    def fee() -> uint256: view
    def mid_fee() -> uint256: view
    def out_fee() -> uint256: view
    def allowed_extra_profit() -> uint256: view
    def fee_gamma() -> uint256: view
    def adjustment_step() -> uint256: view
    def ma_half_time() -> uint256: view
    def admin_fee() -> uint256: view
    def get_virtual_price() -> uint256: view


interface MetaRegistry:
    def admin() -> address: view
    def update_internal_pool_registry(_pool: address, _incremented_index: uint256): nonpayable
    def registry_length() -> uint256: view
    def update_lp_token_mapping(_pool: address, _token: address): nonpayable
    def update_coin_map(_pool: address, _coin_list: address[MAX_COINS], _n_coins: uint256): nonpayable
    def pool_to_registry(_pool: address) -> PoolInfo: view


# ---- structs ---- #
struct PoolInfo:
    registry: uint256
    location: uint256

# ---- constants ---- #
MAX_COINS: constant(uint256) = 8
MAX_POOLS: constant(uint256) = 128

# ---- storage variables ---- #
base_registry: public(BaseRegistry)
metaregistry: public(address)
registry_id: uint256
registry_index: uint256
total_pools: public(uint256) 


# ---- constructor ---- #
@external
def __init__(_metaregistry: address, _id: uint256, address_provider: address):
    self.base_registry = BaseRegistry(AddressProvider(address_provider).get_address(_id))
    self.metaregistry = _metaregistry
    self.registry_id = _id
    self.registry_index = MetaRegistry(_metaregistry).registry_length()


# ---- internal methods ---- #
@internal
@view
def _get_n_coins(_pool: address) -> uint256:
    return self.base_registry.get_n_coins(_pool)


@internal
@view
def _get_lp_token(_pool: address) -> address:
    return self.base_registry.get_lp_token(_pool)


@internal
@view
def _get_coins(_pool: address) -> address[MAX_COINS]:
    return self.base_registry.get_coins(_pool)


@internal
@view
def _get_balances(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_balances(_pool)


# ---- most used Methods: MetaRegistry append / add to registry ---- #
@external
def sync_pool_list(_limit: uint256):
    """
    @notice Records any newly added pool on the metaregistry    
    @param _limit Maximum number of pool to sync (avoid hitting gas limit), 0 = no limits
    @dev To be called from the metaregistry
    @dev In the event of a removal on the registry, sync will be unreliable. A manual update is required
    """
    assert msg.sender == self.metaregistry  # dev: only metaregistry has access
    last_pool: uint256 = self.total_pools
    pool_cap: uint256 = self.base_registry.pool_count()

    if (_limit > 0):
        pool_cap = min((last_pool + _limit), pool_cap)

    for i in range(last_pool, last_pool + MAX_POOLS):
        if i == pool_cap:
            break
        _pool: address = self.base_registry.pool_list(i)
        self.total_pools += 1
        # if the pool has already been added by another registry, we leave it with the original
        if MetaRegistry(self.metaregistry).pool_to_registry(_pool).registry > 0:
            continue

        MetaRegistry(self.metaregistry).update_internal_pool_registry(_pool, self.registry_index + 1)
        MetaRegistry(self.metaregistry).update_lp_token_mapping(_pool, self._get_lp_token(_pool))
        MetaRegistry(self.metaregistry).update_coin_map(_pool, self._get_coins(_pool), self._get_n_coins(_pool))


@external
def add_pool(_pool: address):
    """
    @notice Add a pool to the metaregistry
    @dev To be called from the metaregistry
    @dev To be used when a pool was added to the base registry before a pool removal
    """
    assert msg.sender == self.metaregistry  # dev: only metaregistry has access
    MetaRegistry(self.metaregistry).update_internal_pool_registry(_pool, self.registry_index + 1)
    MetaRegistry(self.metaregistry).update_lp_token_mapping(_pool, self._get_lp_token(_pool))
    self.total_pools -= 1


# ---- view methods (API) of the contract ---- #
@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    return self._get_coins(_pool)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    return self._get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    """
    todo: what if it is a crypto metapool?
    """
    return self._get_n_coins(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_COINS]:
    return self._get_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_decimals(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_decimals(_pool)


@external
@view
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    return self._get_balances(_pool)


@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    return self._get_balances(_pool)


@external
@view
def get_lp_token(_pool: address) -> address:
    return self._get_lp_token(_pool)


@external
@view
def get_gauges(_pool: address) -> (address[10], int128[10]):
    return self.base_registry.get_gauges(_pool)


@external
@view
def is_meta(_pool: address) -> bool:
    return False


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    return self.base_registry.get_pool_name(_pool)


@external
@view
def get_fees(_pool: address) -> uint256[10]:
    fees: uint256[10] = empty(uint256[10])
    pool_fees: uint256[4] = self.base_registry.get_fees(_pool)
    for i in range(4):
        fees[i] = pool_fees[i]
    return fees


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_COINS]:
    return self.base_registry.get_admin_balances(_pool)
    

@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    """
    review: this can just be a public constant so it has a 
            getter auto-generated by the compiler.
    """
    return 4


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
def get_base_pool(_pool: address) -> address:
    return ZERO_ADDRESS


@external
@view
def get_virtual_price_from_lp_token(_token: address) -> uint256:
    return self.base_registry.get_virtual_price_from_lp_token(_token)


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    indices: uint256[2] = self.base_registry.get_coin_indices(_pool, _from, _to)
    return convert(indices[0], int128), convert(indices[1], int128), False


@external
@view
def is_registered(_pool: address) -> bool:
    """
    @notice Check if a pool belongs to the registry using get_n_coins
    @param _pool The address of the pool
    @return A bool corresponding to whether the pool belongs or not
    """
    return self.base_registry.get_n_coins(_pool) > 0


# ---- lesser used methods go here (slightly more gas optimal) ---- #
@external
def remove_pool(_pool: address):
    """
    @notice Removes a pool from the metaregistry
    @dev To be called from the metaregistry
    @dev To be used when a pool is removed from the registry
    @dev A removed registry pool may hide a new pool
    """
    assert msg.sender == self.metaregistry  # dev: only metaregistry has access
    MetaRegistry(self.metaregistry).update_internal_pool_registry(_pool, 0)
    MetaRegistry(self.metaregistry).update_lp_token_mapping(ZERO_ADDRESS, self._get_lp_token(_pool))
    self.total_pools -= 1


@external
def reset_pool_list():
    """
    @notice Removes all pools from the metaregistry
    @dev To be called from the metaregistry
    """
    assert msg.sender == self.metaregistry  # dev: only metaregistry has access
    pool_count: uint256 = self.base_registry.pool_count()
    last_pool: uint256 = self.total_pools
    for i in range(MAX_POOLS):
        if i == pool_count:
            break
        _pool: address = self.base_registry.pool_list(i)
        MetaRegistry(self.metaregistry).update_internal_pool_registry(_pool, 0)
        MetaRegistry(self.metaregistry).update_lp_token_mapping(ZERO_ADDRESS, self._get_lp_token(_pool))
    self.total_pools = 0
