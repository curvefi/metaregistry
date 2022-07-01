# @version 0.3.3
"""
@title Curve Registry Handler for v1 Factory (latest)
@license MIT
"""

# ---- interfaces ---- #
interface AddressProvider:
    def get_address(_id: uint256) -> address: view
    def get_registry() -> address: view


interface BaseRegistry:
    def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address: view
    def get_admin_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_A(_pool: address) -> uint256: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_base_pool(_pool: address) -> address: view
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128): view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_fees(_pool: address) -> uint256[2]: view
    def get_gauge(_pool: address) -> address: view
    def get_lp_token(_pool: address) -> address: view
    def get_meta_n_coins(_pool: address) -> (uint256, uint256): view
    def get_n_coins(_pool: address) -> uint256: view
    def get_pool_asset_type(_pool: address) -> uint256: view
    def get_underlying_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]: view
    def get_underlying_coins(_pool: address) -> address[MAX_COINS]: view
    def get_underlying_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]: view
    def is_meta(_pool: address) -> bool: view
    def pool_count() -> uint256: view
    def pool_list(pool_id: uint256) -> address: view


interface CurveLegacyPool:
    def balances(i: int128) -> uint256: view


interface CurvePool:
    def balances(i: uint256) -> uint256: view


interface ERC20:
    def balanceOf(_addr: address) -> uint256: view
    def decimals() -> uint256: view
    def name() -> String[64]: view
    def totalSupply() -> uint256: view


interface GaugeController:
    def gauge_types(gauge: address) -> int128: view


interface MetaRegistry:
    def registry_length() -> uint256: view


# ---- constants ---- #
BTC_BASE_POOL: constant(address) = 0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714
GAUGE_CONTROLLER: constant(address) = 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
MAX_COINS: constant(uint256) = 4
MAX_METAREGISTRY_COINS: constant(uint256) = 8


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
def _is_meta(_pool: address) -> bool:
    return self.base_registry.is_meta(_pool)


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
def _get_btc_underlying_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    """
    @notice Get balances for each underlying coin within a metapool
    @dev  Used with BTC factory metapools that do not have a base_pool attribute
    @param _pool Metapool address
    @return uint256 list of underlying balances
    """
    underlying_balances: uint256[MAX_METAREGISTRY_COINS] = empty(uint256[MAX_METAREGISTRY_COINS])
    underlying_balances[0] = CurvePool(_pool).balances(0)

    base_total_supply: uint256 = ERC20(self.base_registry.get_coins(_pool)[1]).totalSupply()
    if base_total_supply > 0:
        underlying_pct: uint256 = CurvePool(_pool).balances(1) * 10**36 / base_total_supply
        for i in range(3):
            underlying_balances[i + 1] = CurveLegacyPool(BTC_BASE_POOL).balances(i) * underlying_pct / 10**36
    return underlying_balances


@internal
@view
def _get_n_coins(_pool: address) -> uint256:
    if self._is_meta(_pool):
        return 2
    return self.base_registry.get_n_coins(_pool)


@internal
@view
def _get_underlying_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    _coins: address[MAX_COINS] = self.base_registry.get_underlying_coins(_pool)
    _padded_coins: address[MAX_METAREGISTRY_COINS] = empty(address[MAX_METAREGISTRY_COINS])
    for i in range(MAX_COINS):
        _padded_coins[i] = _coins[i]
    return _padded_coins


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
def _get_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._pad_uint_array(self.base_registry.get_decimals(_pool))


@internal
@view
def _get_base_pool(_pool: address) -> address:
    if not self._is_meta(_pool):
        return ZERO_ADDRESS
    if (self.base_registry.get_pool_asset_type(_pool) == 2):
        return BTC_BASE_POOL
    return self.base_registry.get_base_pool(_pool)


# ---- view methods (API) of the contract ---- #
@external
@view
def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address:
    return self.base_registry.find_pool_for_coins(_from, _to, i)


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._pad_uint_array(self.base_registry.get_admin_balances(_pool))


@external
@view
def get_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    return self._get_balances(_pool)


@external
@view
def get_base_pool(_pool: address) -> address:
    return self._get_base_pool(_pool)


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    coin1: int128 = 0
    coin2: int128 = 0
    is_underlying: bool = False

    (coin1, coin2) = self.base_registry.get_coin_indices(_pool, _from, _to)

    # due to a bug in original factory contract, `is_underlying`` is always True
    # to fix this, we first check if it is a metapool, and if not then we return
    # False. If so, then we check if basepool lp token is one of the two coins,
    # in which case `is_underlying` would be False
    if self._is_meta(_pool):
        base_pool_lp_token: address = self.base_registry.get_coins(_pool)[1]
        if base_pool_lp_token not in [_from, _to]:
            is_underlying = True

    return (coin1, coin2, is_underlying)


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
    pool_fees: uint256[2] = self.base_registry.get_fees(_pool)
    for i in range(2):
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
    return _pool


@external
@view
def get_n_coins(_pool: address) -> uint256:
    return self._get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    if self._is_meta(_pool):
        return self.base_registry.get_meta_n_coins(_pool)[1]
    else:
        return self.base_registry.get_n_coins(_pool)


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    return self.base_registry.get_pool_asset_type(_pool)


@external
@view
def get_pool_from_lp_token(_lp_token: address) -> address:
    if self._get_n_coins(_lp_token) > 0:
        return _lp_token
    return ZERO_ADDRESS


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    """
    @dev stable factory pools are ERC20 tokenized
    """
    if self._get_n_coins(_pool) == 0:
        # _pool is not in base registry, so we ignore:
        return ""
    return ERC20(_pool).name()


@external
@view
def get_pool_params(_pool: address) -> uint256[20]:
    stableswap_pool_params: uint256[20] = empty(uint256[20])
    stableswap_pool_params[0] = self.base_registry.get_A(_pool)
    return stableswap_pool_params


@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    """
    @dev some metapools (BTC) do not have a base_pool attribute so some registry functions
         will revert because the pools are not recognized as metapools.
    """
    if not self._is_meta(_pool):
        return self._get_balances(_pool)
    if (self.base_registry.get_pool_asset_type(_pool) == 2):
        # some metapools (BTC) do not have a base_pool attribute so some registry functions
        # will revert because the pools are not recognized as metapools.
        return self._get_btc_underlying_balances(_pool)
    return self.base_registry.get_underlying_balances(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_METAREGISTRY_COINS]:
    if not self._is_meta(_pool):
        return self._get_coins(_pool)
    return self._get_underlying_coins(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_METAREGISTRY_COINS]:
    """
    @notice If it is a metapool, method uses the base registry. Else it uses a
    custom getter. This is because the base registry cannot unpack decimals
    (stored as a bitmap) if there is no metapool. So it returns the decimals of
    only the first coin.
    @param _pool Address of the pool
    """
    if not self._is_meta(_pool):
        return self._get_decimals(_pool)
    return self.base_registry.get_underlying_decimals(_pool)


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
