# @version 0.3.3
"""
@title Curve Registry Handler for v2 Factory
@license MIT
"""

# ---- interfaces ---- #
interface BaseRegistry:
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_gauge(_pool: address) -> address: view
    def get_n_coins(_pool: address) -> uint256: view
    def get_token(_pool: address) -> address: view
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
    def get_pool_from_lp_token(_pool: address) -> address: view
    def update_coin_map(_pool: address, _coin_list: address[MAX_METAREGISTRY_COINS], _n_coins: uint256): nonpayable
    def pool_to_registry(_pool: address) -> PoolInfo: view


interface AddressProvider:
    def get_address(_id: uint256) -> address: view


interface GaugeController:
    def gauge_types(gauge: address) -> int128: view


interface ERC20:
    def name() -> String[64]: view
    def balanceOf(_addr: address) -> uint256: view


# ---- structs ---- #
struct PoolInfo:
    registry: uint256
    location: uint256


# ---- constants ---- #
GAUGE_CONTROLLER: constant(address) = 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
MAX_COINS: constant(uint256) = 2
MAX_METAREGISTRY_COINS: constant(uint256) = 8
MAX_POOLS: constant(uint256) = 128
N_COINS: constant(uint256) = 2


# ---- storage variables ---- #
metaregistry: public(address)
base_registry: public(BaseRegistry)
registry_id: uint256
registry_index: uint256
total_pools: public(uint256) 


# ---- constructor ---- #
@external
def __init__(_metaregistry: address, _id: uint256, address_provider: address):
    self.metaregistry = _metaregistry
    self.base_registry = BaseRegistry(AddressProvider(address_provider).get_address(_id))
    self.registry_id = _id
    self.registry_index = MetaRegistry(_metaregistry).registry_length()


# ---- Most used Methods: MetaRegistry append / add to registry ---- #
@internal
@view
def _get_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    _coins: address[MAX_COINS] = self.base_registry.get_coins(_pool)
    _padded_coins: address[MAX_METAREGISTRY_COINS] = empty(address[MAX_METAREGISTRY_COINS])
    for i in range(MAX_COINS):
        _padded_coins[i] = _coins[i]
    return _padded_coins


@internal
@view
def _get_lp_token(_pool: address) -> address:
    return self.base_registry.get_token(_pool)


@external
def sync_pool_list(_limit: uint256):
    """
    @notice Records any newly added pool on the metaregistry
    @param _limit Maximum number of pool to sync (avoid hitting gas limit), 0 = no limits
    @dev To be called from the metaregistry
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
        MetaRegistry(self.metaregistry).update_coin_map(_pool, self._get_coins(_pool), N_COINS)


# ---- view methods (API) of the contract ---- #
@internal
@view
def _pad_uint_array(_array: uint256[MAX_COINS]) -> uint256[MAX_METAREGISTRY_COINS]:
    _padded_array: uint256[MAX_METAREGISTRY_COINS] = empty(uint256[MAX_METAREGISTRY_COINS])
    for i in range(MAX_COINS):
        _padded_array[i] = _array[i]
    return _padded_array


@internal
@view
def _get_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._pad_uint_array(self.base_registry.get_decimals(_pool))


@internal
@view
def _get_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._pad_uint_array(self.base_registry.get_balances(_pool))


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
def get_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    return self._get_coins(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    return self._get_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    return N_COINS


@external
@view
def get_n_coins(_pool: address) -> uint256:
    return N_COINS


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_decimals(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_decimals(_pool)


@external
@view
def get_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_balances(_pool)

@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_balances(_pool)


@external
@view
def get_lp_token(_pool: address) -> address:
    return self._get_lp_token(_pool)


@external
@view
def get_gauges(_pool: address) -> (address[10], int128[10]):
    gauges: address[10] = empty(address[10])
    types: int128[10] = empty(int128[10])
    gauges[0] = self.base_registry.get_gauge(_pool)
    types[0] = GaugeController(GAUGE_CONTROLLER).gauge_types(gauges[0])
    return (gauges, types)


@external
@view
def is_meta(_pool: address) -> bool:
    return False


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    token: address = self._get_lp_token(_pool)
    if token != ZERO_ADDRESS:
        return ERC20(self.base_registry.get_token(_pool)).name()
    else:
        return ""


@external
@view
def get_fees(_pool: address) -> uint256[10]:
    fees: uint256[10] = empty(uint256[10])
    pool_fees: uint256[4] = [CurvePool(_pool).fee(), CurvePool(_pool).admin_fee(), CurvePool(_pool).mid_fee(), CurvePool(_pool).out_fee()]
    for i in range(4):
        fees[i] = pool_fees[i]
    return fees


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    balances: uint256[MAX_METAREGISTRY_COINS] = self._get_balances(_pool)
    coins: address[MAX_METAREGISTRY_COINS] = self._get_coins(_pool)
    for i in range(N_COINS):
        coin: address = coins[i]
        if (coin == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE or coin == 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2):
            balances[i] = _pool.balance - balances[i]
        else:
            balances[i] = ERC20(coin).balanceOf(_pool) - balances[i]
    return balances


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    return 4


@external
@view
def get_D(_pool: address) -> uint256:
    return CurvePool(_pool).D()


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
    return CurvePool(MetaRegistry(self.metaregistry).get_pool_from_lp_token(_token)).get_virtual_price()


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    indices: uint256[2] = self.base_registry.get_coin_indices(_pool, _from, _to)
    return convert(indices[0], int128), convert(indices[1], int128), False


# ---- lesser used methods go here (slightly more gas optimal) ---- #
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
