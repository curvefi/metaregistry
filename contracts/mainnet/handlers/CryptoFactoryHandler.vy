# @version 0.3.3
"""
@title Curve Registry Handler for v2 Factory
@license MIT
"""

# ---- interfaces ---- #
interface AddressProvider:
    def get_address(_id: uint256) -> address: view


interface BaseRegistry:
    def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> uint256[2]: view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_gauge(_pool: address) -> address: view
    def get_n_coins(_pool: address) -> uint256: view
    def get_token(_pool: address) -> address: view
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


interface ERC20:
    def name() -> String[64]: view
    def balanceOf(_addr: address) -> uint256: view


interface GaugeController:
    def gauge_types(gauge: address) -> int128: view


interface MetaRegistry:
    def registry_length() -> uint256: view


# ---- constants ---- #
GAUGE_CONTROLLER: constant(address) = 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
MAX_COINS: constant(uint256) = 2
MAX_METAREGISTRY_COINS: constant(uint256) = 8
MAX_POOLS: constant(uint256) = 65536
N_COINS: constant(uint256) = 2


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
def _pad_uint_array(_array: uint256[MAX_COINS]) -> uint256[MAX_METAREGISTRY_COINS]:
    _padded_array: uint256[MAX_METAREGISTRY_COINS] = empty(uint256[MAX_METAREGISTRY_COINS])
    for i in range(MAX_COINS):
        _padded_array[i] = _array[i]
    return _padded_array


@internal
@view
def _get_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._pad_uint_array(self.base_registry.get_balances(_pool))


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
def _get_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._pad_uint_array(self.base_registry.get_decimals(_pool))


@internal
@view
def _get_lp_token(_pool: address) -> address:
    return self.base_registry.get_token(_pool)


@internal
@view
def _get_n_coins(_pool: address) -> uint256:
    if (self.base_registry.get_coins(_pool)[0] != ZERO_ADDRESS):
        return N_COINS
    return 0


# ---- view methods (API) of the contract ---- #
@external
@view
def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address:
    return self.base_registry.find_pool_for_coins(_from, _to, i)


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
def get_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_balances(_pool)


@external
@view
def get_base_pool(_pool: address) -> address:
    return ZERO_ADDRESS


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    indices: uint256[2] = self.base_registry.get_coin_indices(_pool, _from, _to)
    return convert(indices[0], int128), convert(indices[1], int128), False


@external
@view
def get_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    return self._get_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_decimals(_pool)


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
def get_gauges(_pool: address) -> (address[10], int128[10]):
    gauges: address[10] = empty(address[10])
    types: int128[10] = empty(int128[10])
    gauges[0] = self.base_registry.get_gauge(_pool)
    types[0] = GaugeController(GAUGE_CONTROLLER).gauge_types(gauges[0])
    return (gauges, types)


@external
@view
def get_lp_token(_pool: address) -> address:
    return self._get_lp_token(_pool)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    return self._get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    return self._get_n_coins(_pool)


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    return 4


@external
@view
def get_pool_from_lp_token(_lp_token: address) -> address:
    max_pools: uint256 = self.base_registry.pool_count()
    for i in range(MAX_POOLS):
        if i == max_pools:
            break
        pool: address = self.base_registry.pool_list(i)
        token: address = self._get_lp_token(pool)
        if token == _lp_token:
            return pool
    return ZERO_ADDRESS


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
def get_underlying_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_balances(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    return self._get_coins(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_decimals(_pool)


@external
@view
def is_meta(_pool: address) -> bool:
    return False


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