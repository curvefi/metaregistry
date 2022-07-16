# @version 0.3.3
"""
@title Curve CryptoSwap Registry
@license MIT
@author Curve.Fi
"""

MAX_COINS: constant(int128) = 8
CALC_INPUT_SIZE: constant(int128) = 100


struct CoinInfo:
    index: uint256
    register_count: uint256
    swap_count: uint256
    swap_for: address[MAX_INT128]


struct PoolArray:
    location: uint256
    base_pool: address
    n_coins: uint256
    name: String[64]
    has_positive_rebasing_tokens: bool


interface AddressProvider:
    def admin() -> address: view
    def get_address(_id: uint256) -> address: view
    def get_registry() -> address: view

interface ERC20:
    def balanceOf(_addr: address) -> uint256: view
    def decimals() -> uint256: view
    def totalSupply() -> uint256: view

interface CurvePool:
    def token() -> address: view
    def coins(i: uint256) -> address: view
    def A() -> uint256: view
    def gamma() -> uint256: view
    def fee() -> uint256: view
    def get_virtual_price() -> uint256: view
    def mid_fee() -> uint256: view
    def out_fee() -> uint256: view
    def admin_fee() -> uint256: view
    def balances(i: uint256) -> uint256: view
    def D() -> uint256: view
    def xcp_profit() -> uint256: view
    def xcp_profit_a() -> uint256: view

interface StableSwapLegacy:
    def coins(i: int128) -> address: view
    def underlying_coins(i: int128) -> address: view
    def balances(i: int128) -> uint256: view

interface LiquidityGauge:
    def lp_token() -> address: view
    def is_killed() -> bool: view

interface GaugeController:
    def gauge_types(gauge: address) -> int128: view

interface BasePoolRegistry:
    def get_base_pool_for_lp_token(_lp_token: address) ->  address: view
    def get_n_coins(_pool: address) -> uint256: view
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_lp_token(_pool: address) -> address: view
    def is_legacy(_pool: address) -> bool: view


event PoolAdded:
    pool: indexed(address)

event BasePoolAdded:
    basepool: indexed(address)

event PoolRemoved:
    pool: indexed(address)


GAUGE_CONTROLLER: constant(address) = 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB

address_provider: public(AddressProvider)
base_pool_registry: public(BasePoolRegistry)
pool_list: public(address[65536])   # master list of pools
pool_count: public(uint256)         # actual length of pool_list
base_pool_count: public(uint256)

pool_data: HashMap[address, PoolArray]

coin_count: public(uint256)  # total unique coins registered
coins: HashMap[address, CoinInfo]
get_coin: public(address[65536])  # unique list of registered coins
# bitwise_xor(coina, coinb) -> (coina_pos, coinb_pos) sorted
# stored as uint128[2]
coin_swap_indexes: HashMap[uint256, uint256]

# lp token -> pool
get_pool_from_lp_token: public(HashMap[address, address])

# pool -> lp token
get_lp_token: public(HashMap[address, address])

# mapping of coins -> pools for trading
# a mapping key is generated for each pair of addresses via
# `bitwise_xor(convert(a, uint256), convert(b, uint256))`
markets: HashMap[uint256, address[65536]]
market_counts: HashMap[uint256, uint256]

liquidity_gauges: HashMap[address, address[10]]

# mapping of pool -> deposit/exchange zap
get_zap: public(HashMap[address, address])

last_updated: public(uint256)


@external
def __init__(_address_provider: address, _base_pool_registry: address):
    """
    @notice Constructor function
    """
    self.address_provider = AddressProvider(_address_provider)
    self.base_pool_registry = BasePoolRegistry(_base_pool_registry)


# internal functionality for getters

@internal
@view
def _get_coins(_pool: address) -> address[MAX_COINS]:
    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    for i in range(MAX_COINS):
        if i == convert(self.pool_data[_pool].n_coins, int128):
            break
        _coins[i] = CurvePool(_pool).coins(convert(i, uint256))
    return _coins


@view
@internal
def _get_decimals(_coins: address[MAX_COINS]) -> uint256[MAX_COINS]:
    decimals: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    value: uint256 = 0
    for i in range(MAX_COINS):
        if _coins[i] == ZERO_ADDRESS:
            break
        coin: address = _coins[i]
        if coin == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
            value = 18
        else:
            value = ERC20(coin).decimals()
            assert value < 256  # dev: decimal overflow

        decimals[i] = value

    return decimals


@view
@internal
def _get_underlying_coins_for_metapool(_pool: address) -> address[MAX_COINS]:

    base_pool_coins: address[MAX_COINS] = self.base_pool_registry.get_coins(self.pool_data[_pool].base_pool)
    _underlying_coins: address[MAX_COINS] = empty(address[MAX_COINS])
    base_coin_offset: int128 = convert(self.pool_data[_pool].n_coins - 1, int128)
    _coins: address[MAX_COINS] = self._get_coins(_pool)

    for i in range(MAX_COINS):
        if i < base_coin_offset:
            _underlying_coins[i] = _coins[i]
        else:
            _underlying_coins[i] = base_pool_coins[i - base_coin_offset]

    assert _underlying_coins[0] != ZERO_ADDRESS

    return _underlying_coins


@view
@internal
def _get_balances(_pool: address) -> uint256[MAX_COINS]:
    balances: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    _coins: address[MAX_COINS] = self._get_coins(_pool)
    for i in range(MAX_COINS):
        if _coins[i] == ZERO_ADDRESS:
            assert i != 0
            break

        balances[i] = CurvePool(_pool).balances(convert(i, uint256))

    return balances


@view
@internal
def _get_meta_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    base_coin_idx: uint256 = self.pool_data[_pool].n_coins - 1
    base_pool: address = self.pool_data[_pool].base_pool
    base_total_supply: uint256 = ERC20(self.base_pool_registry.get_lp_token(base_pool)).totalSupply()

    underlying_balances: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    ul_balance: uint256 = 0
    underlying_pct: uint256 = 0
    if base_total_supply > 0:
        underlying_pct = CurvePool(_pool).balances(base_coin_idx) * 10**36 / base_total_supply

    ul_coins: address[MAX_COINS] = self._get_underlying_coins_for_metapool(_pool)
    for i in range(MAX_COINS):

        if ul_coins[i] == ZERO_ADDRESS:
            break

        if i < convert(base_coin_idx, int128):
            ul_balance = CurvePool(_pool).balances(convert(i, uint256))

        else:

            if self.base_pool_registry.is_legacy(base_pool):
                ul_balance = StableSwapLegacy(base_pool).balances(i - convert(base_coin_idx, int128))
            else:
                ul_balance = CurvePool(base_pool).balances(convert(i, uint256) - base_coin_idx)
            ul_balance = ul_balance * underlying_pct / 10**36
        underlying_balances[i] = ul_balance

    return underlying_balances


@view
@internal
def _is_meta(_pool: address) -> bool:
    return self.pool_data[_pool].base_pool != ZERO_ADDRESS


@view
@internal
def _get_coin_indices(
    _pool: address,
    _from: address,
    _to: address
) -> uint256[3]:
    """
    Convert coin addresses to indices for use with pool methods
    """
    # the return value is stored as `uint256[3]` to reduce gas costs
    # from index, to index, is the market underlying?
    result: uint256[3] = empty(uint256[3])
    _coins: address[MAX_COINS] = self._get_coins(_pool)
    found_market: bool = False

    # check coin markets
    for x in range(MAX_COINS):
        coin: address = _coins[x]
        if coin == ZERO_ADDRESS:
            # if we reach the end of the coins, reset `found_market` and try again
            # with the underlying coins
            found_market = False
            break
        if coin == _from:
            result[0] = convert(x, uint256)
        elif coin == _to:
            result[1] = convert(x, uint256)
        else:
            continue

        if found_market:
            # the second time we find a match, break out of the loop
            break
        # the first time we find a match, set `found_market` to True
        found_market = True

    if not found_market and self._is_meta(_pool):
        # check underlying coin markets
        underlying_coins: address[MAX_COINS] = self._get_underlying_coins_for_metapool(_pool)
        for x in range(MAX_COINS):
            coin: address = underlying_coins[x]
            if coin == ZERO_ADDRESS:
                raise "No available market"
            if coin == _from:
                result[0] = convert(x, uint256)
            elif coin == _to:
                result[1] = convert(x, uint256)
            else:
                continue

            if found_market:
                result[2] = 1
                break
            found_market = True

    return result


@internal
@view
def _get_gauge_type(_gauge: address) -> int128:

    success: bool = False
    response: Bytes[32] = b""
    success, response = raw_call(
        GAUGE_CONTROLLER,
        concat(
            method_id("gauge_type(address)"),
            convert(_gauge, bytes32),
        ),
        max_outsize=32,
        revert_on_failure=False,
        is_static_call=True
    )

    if success and not LiquidityGauge(_gauge).is_killed():
        return convert(response, int128)

    return 0


# targetted external getters, optimized for on-chain calls


@view
@external
def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address:
    """
    @notice Find an available pool for exchanging two coins
    @param _from Address of coin to be sent
    @param _to Address of coin to be received
    @param i Index value. When multiple pools are available
            this value is used to return the n'th address.
    @return Pool address
    """
    key: uint256 = bitwise_xor(convert(_from, uint256), convert(_to, uint256))
    return self.markets[key][i]


@view
@external
def get_n_coins(_pool: address) -> uint256:
    """
    @notice Get the number of coins in a pool
    @dev For non-metapools, both returned values are identical
         even when the pool does not use wrapping/lending
    @param _pool Pool address
    @return Number of wrapped coins, number of underlying coins
    """
    return self.pool_data[_pool].n_coins


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    """
    @notice Get the number of underlying coins in a pool
    """
    if not self._is_meta(_pool):
        return self.pool_data[_pool].n_coins

    base_pool: address = self.pool_data[_pool].base_pool
    return self.pool_data[_pool].n_coins + self.base_pool_registry.get_n_coins(base_pool) - 1


@view
@external
def get_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the coins within a pool
    @dev For pools using lending, these are the wrapped coin addresses
    @param _pool Pool address
    @return List of coin addresses
    """
    return self._get_coins(_pool)


@view
@external
def get_underlying_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the underlying coins within a pool
    @dev For pools that do not lend, returns the same value as `get_coins`
    @param _pool Pool address
    @return List of coin addresses
    """
    if self._is_meta(_pool):
        return self._get_underlying_coins_for_metapool(_pool)
    return self._get_coins(_pool)


@view
@external
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get decimal places for each coin within a pool
    @dev For pools using lending, these are the wrapped coin decimal places
    @param _pool Pool address
    @return uint256 list of decimals
    """
    _coins: address[MAX_COINS] = self._get_coins(_pool)
    return self._get_decimals(_coins)


@view
@external
def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get decimal places for each underlying coin within a pool
    @dev For pools that do not lend, returns the same value as `get_decimals`
    @param _pool Pool address
    @return uint256 list of decimals
    """
    if self._is_meta(_pool):
        _underlying_coins: address[MAX_COINS] = self._get_underlying_coins_for_metapool(_pool)
        _decimals: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
        for i in range(MAX_COINS):
            if _underlying_coins[i] == ZERO_ADDRESS:
                break
            _decimals[i] = ERC20(_underlying_coins[i]).decimals()
        return _decimals

    _coins: address[MAX_COINS] = self._get_coins(_pool)
    return self._get_decimals(_coins)


@view
@external
def get_gauges(_pool: address) -> (address[10], int128[10]):
    """
    @notice Get a list of LiquidityGauge contracts associated with a pool
    @param _pool Pool address
    @return address[10] of gauge addresses, int128[10] of gauge types
    """
    liquidity_gauges: address[10] = empty(address[10])
    gauge_types: int128[10] = empty(int128[10])
    for i in range(10):
        gauge: address = self.liquidity_gauges[_pool][i]
        if gauge == ZERO_ADDRESS:
            break
        liquidity_gauges[i] = gauge
        gauge_types[i] = GaugeController(GAUGE_CONTROLLER).gauge_types(gauge)

    return liquidity_gauges, gauge_types


@view
@external
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get balances for each coin within a pool
    @dev For pools using lending, these are the wrapped coin balances
    @param _pool Pool address
    @return uint256 list of balances
    """
    return self._get_balances(_pool)


@view
@external
def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get balances for each underlying coin within a pool
    @dev  For pools that do not lend, returns the same value as `get_balances`
    @param _pool Pool address
    @return uint256 list of underlyingbalances
    """
    if not self._is_meta(_pool):
        return self._get_balances(_pool)
    return self._get_meta_underlying_balances(_pool)


@view
@external
def get_virtual_price_from_lp_token(_token: address) -> uint256:
    """
    @notice Get the virtual price of a pool LP token
    @param _token LP token address
    @return uint256 Virtual price
    """
    return CurvePool(self.get_pool_from_lp_token[_token]).get_virtual_price()


@view
@external
def get_A(_pool: address) -> uint256:
    return CurvePool(_pool).A()


@view
@external
def get_D(_pool: address) -> uint256:
    return CurvePool(_pool).D()


@view
@external
def get_gamma(_pool: address) -> uint256:
    return CurvePool(_pool).gamma()


@view
@external
def get_fees(_pool: address) -> uint256[4]:
    """
    @notice Get the fees for a pool
    @dev Fees are expressed as integers
    @return Pool fee as uint256 with 1e10 precision
            Admin fee as 1e10 percentage of pool fee
            Mid fee
            Out fee
    """
    return [CurvePool(_pool).fee(), CurvePool(_pool).admin_fee(), CurvePool(_pool).mid_fee(), CurvePool(_pool).out_fee()]


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @dev Cryptoswap pools do not store admin fees in the form of
         admin token balances. Instead, the admin fees are computed
         at the time of claim iff sufficient profits have been made.
         These fees are allocated to the admin by minting LP tokens
         (dilution). The logic to calculate fees are derived from
         cryptopool._claim_admin_fees() method.
    """
    xcp_profit: uint256 = CurvePool(_pool).xcp_profit()
    xcp_profit_a: uint256 = CurvePool(_pool).xcp_profit_a()
    admin_fee: uint256 = CurvePool(_pool).admin_fee()
    admin_balances: uint256[MAX_COINS] = empty(uint256[MAX_COINS])

    # admin balances are non zero if pool has made more than allowed profits:
    if xcp_profit > xcp_profit_a:

        # calculate admin fees in lp token amounts:
        fees: uint256 = (xcp_profit - xcp_profit_a) * admin_fee / (2 * 10**10)
        if fees > 0:
            vprice: uint256 = CurvePool(_pool).get_virtual_price()
            lp_token: address = self.get_lp_token[_pool]
            frac: uint256 = vprice * 10**18 / (vprice - fees) - 10**18

            # the total supply of lp token is current supply + claimable:
            lp_token_total_supply: uint256 = ERC20(lp_token).totalSupply()
            d_supply: uint256 = lp_token_total_supply * frac / 10**18
            lp_token_total_supply += d_supply
            admin_lp_frac: uint256 = d_supply * 10 ** 18 / lp_token_total_supply

            # get admin balances in individual assets:
            reserves: uint256[MAX_COINS] = self._get_balances(_pool)
            for i in range(MAX_COINS):
                admin_balances[i] = admin_lp_frac * reserves[i] / 10 ** 18

    return admin_balances


@view
@external
def get_coin_indices(
    _pool: address,
    _from: address,
    _to: address
) -> (int128, int128, bool):
    """
    @notice Convert coin addresses to indices for use with pool methods
    @param _from Coin address to be used as `i` within a pool
    @param _to Coin address to be used as `j` within a pool
    @return int128 `i`, int128 `j`, boolean indicating if `i` and `j` are underlying coins
    """
    result: uint256[3] = self._get_coin_indices(_pool, _from, _to)
    return convert(result[0], int128), convert(result[1], int128), result[2] > 0


@view
@external
def is_meta(_pool: address) -> bool:
    """
    @notice Verify `_pool` is a metapool
    @param _pool Pool address
    @return True if `_pool` is a metapool
    """
    return self.pool_data[_pool].base_pool != ZERO_ADDRESS


@view
@external
def get_base_pool(_pool: address) -> address:
    return self.pool_data[_pool].base_pool


@view
@external
def get_pool_name(_pool: address) -> String[64]:
    """
    @notice Get the given name for a pool
    @param _pool Pool address
    @return The name of a pool
    """
    return self.pool_data[_pool].name


@view
@external
def get_coin_swap_count(_coin: address) -> uint256:
    """
    @notice Get the number of unique coins available to swap `_coin` against
    @param _coin Coin address
    @return The number of unique coins available to swap for
    """
    return self.coins[_coin].swap_count


@view
@external
def get_coin_swap_complement(_coin: address, _index: uint256) -> address:
    """
    @notice Get the coin available to swap against `_coin` at `_index`
    @param _coin Coin address
    @param _index An index in the `_coin`'s set of available counter
        coin's
    @return Address of a coin available to swap against `_coin`
    """
    return self.coins[_coin].swap_for[_index]


@view
@external
def get_num_coin_registrations(_coin: address) -> uint256:
    return self.coins[_coin].register_count


# internal functionality used in admin setters


@internal
def _register_coin(_coin: address):
    if self.coins[_coin].register_count == 0:
        coin_count: uint256 = self.coin_count
        self.coins[_coin].index = coin_count
        self.get_coin[coin_count] = _coin
        self.coin_count += 1
    self.coins[_coin].register_count += 1


@internal
def _register_coin_pair(_coina: address, _coinb: address, _key: uint256):
    # register _coinb in _coina's array of coins
    coin_b_pos: uint256 = self.coins[_coina].swap_count
    self.coins[_coina].swap_for[coin_b_pos] = _coinb
    self.coins[_coina].swap_count += 1
    # register _coina in _coinb's array of coins
    coin_a_pos: uint256 = self.coins[_coinb].swap_count
    self.coins[_coinb].swap_for[coin_a_pos] = _coina
    self.coins[_coinb].swap_count += 1
    # register indexes (coina pos in coinb array, coinb pos in coina array)
    if convert(_coina, uint256) < convert(_coinb, uint256):
        self.coin_swap_indexes[_key] = shift(coin_a_pos, 128) + coin_b_pos
    else:
        self.coin_swap_indexes[_key] = shift(coin_b_pos, 128) + coin_a_pos


@internal
def _unregister_coin(_coin: address):

    self.coins[_coin].register_count -= 1

    if self.coins[_coin].register_count == 0:
        self.coin_count -= 1
        coin_count: uint256 = self.coin_count
        location: uint256 = self.coins[_coin].index

        if location < coin_count:
            coin_b: address = self.get_coin[coin_count]
            self.get_coin[location] = coin_b
            self.coins[coin_b].index = location

        self.coins[_coin].index = 0
        self.get_coin[coin_count] = ZERO_ADDRESS


@internal
def _unregister_coin_pair(_coina: address, _coinb: address, _coinb_idx: uint256):
    """
    @param _coinb_idx the index of _coinb in _coina's array of unique coin's
    """
    # decrement swap counts for both coins
    self.coins[_coina].swap_count -= 1

    # retrieve the last currently occupied index in coina's array
    coina_arr_last_idx: uint256 = self.coins[_coina].swap_count

    # if coinb's index in coina's array is less than the last
    # overwrite it's position with the last coin
    if _coinb_idx < coina_arr_last_idx:
        # here's our last coin in coina's array
        coin_c: address = self.coins[_coina].swap_for[coina_arr_last_idx]
        # get the bitwise_xor of the pair to retrieve their indexes
        key: uint256 = bitwise_xor(convert(_coina, uint256), convert(coin_c, uint256))
        indexes: uint256 = self.coin_swap_indexes[key]

        # update the pairing's indexes
        if convert(_coina, uint256) < convert(coin_c, uint256):
            # least complicated most readable way of shifting twice to remove the lower order bits
            self.coin_swap_indexes[key] = shift(shift(indexes, -128), 128) + _coinb_idx
        else:
            self.coin_swap_indexes[key] = shift(_coinb_idx, 128) + indexes % 2 ** 128
        # set _coinb_idx in coina's array to coin_c
        self.coins[_coina].swap_for[_coinb_idx] = coin_c

    self.coins[_coina].swap_for[coina_arr_last_idx] = ZERO_ADDRESS


@internal
def _add_coins_to_market(_pool: address, _coin_list: address[MAX_COINS]):

    for i in range(MAX_COINS):
        if _coin_list[i] == ZERO_ADDRESS:
            break

        self._register_coin(_coin_list[i])

        # add pool to markets
        i2: int128 = i + 1
        for x in range(i2, i2 + MAX_COINS):
            if _coin_list[x] == ZERO_ADDRESS:
                break

            key: uint256 = bitwise_xor(
                convert(_coin_list[i], uint256), convert(_coin_list[x], uint256)
            )
            length: uint256 = self.market_counts[key]
            self.markets[key][length] = _pool
            self.market_counts[key] = length + 1

            # register the coin pair
            if length == 0:
                self._register_coin_pair(_coin_list[x], _coin_list[i], key)


@internal
def _remove_market(_pool: address, _coina: address, _coinb: address):
    key: uint256 = bitwise_xor(convert(_coina, uint256), convert(_coinb, uint256))
    length: uint256 = self.market_counts[key] - 1
    if length == 0:
        indexes: uint256 = self.coin_swap_indexes[key]
        if convert(_coina, uint256) < convert(_coinb, uint256):
            self._unregister_coin_pair(_coina, _coinb, indexes % 2 ** 128)
            self._unregister_coin_pair(_coinb, _coina, shift(indexes, -128))
        else:
            self._unregister_coin_pair(_coina, _coinb, shift(indexes, -128))
            self._unregister_coin_pair(_coinb, _coina, indexes % 2 ** 128)
        self.coin_swap_indexes[key] = 0
    for i in range(65536):
        if i > length:
            break
        if self.markets[key][i] == _pool:
            if i < length:
                self.markets[key][i] = self.markets[key][length]
            self.markets[key][length] = ZERO_ADDRESS
            self.market_counts[key] = length
            break


# admin functions


@external
def add_pool(
    _pool: address,
    _lp_token: address,
    _gauge: address,
    _zap: address,
    _n_coins: uint256,
    _name: String[64],
    _base_pool: address = ZERO_ADDRESS,
    _has_positive_rebasing_tokens: bool = False
):
    """
    @notice Add a pool to the registry
    @dev Only callable by admin
    @param _pool Pool address to add
    @param _lp_token Pool deposit token address
    @param _gauge Gauge address
    @param _zap Zap address
    @param _name The name of the pool
    @param _base_pool Address of base pool
    @param _has_positive_rebasing_tokens pool contains positive rebasing tokens
    """
    assert msg.sender == self.address_provider.admin()  # dev: admin-only function
    assert _lp_token != ZERO_ADDRESS
    assert self.get_pool_from_lp_token[_lp_token] == ZERO_ADDRESS  # dev: pool exists

    # initialise PoolArray struct
    length: uint256 = self.pool_count
    self.pool_list[length] = _pool
    self.pool_count = length + 1
    self.pool_data[_pool].location = length
    self.pool_data[_pool].name = _name
    self.pool_data[_pool].n_coins = _n_coins

    # update public mappings
    if _zap != ZERO_ADDRESS:
        self.get_zap[_pool] = _zap

    if _gauge != ZERO_ADDRESS:
        self.liquidity_gauges[_pool][0] = _gauge

    self.get_pool_from_lp_token[_lp_token] = _pool
    self.get_lp_token[_pool] = _lp_token

    # add coins mappings:
    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    for i in range(MAX_COINS):
        if i == convert(_n_coins, int128):
            break
        _coins[i] = CurvePool(_pool).coins(convert(i, uint256))
    self._add_coins_to_market(_pool, _coins)

    if _base_pool != ZERO_ADDRESS:
        assert self.base_pool_registry.get_lp_token(_base_pool) != ZERO_ADDRESS
        self.pool_data[_pool].base_pool = _base_pool

        _underlying_coins: address[MAX_COINS] = self._get_underlying_coins_for_metapool(_pool)
        assert _underlying_coins[0] != ZERO_ADDRESS

        self._add_coins_to_market(_pool, _underlying_coins)

    if _has_positive_rebasing_tokens:
        self.pool_data[_pool].has_positive_rebasing_tokens = True

    # log pool added:
    self.last_updated = block.timestamp
    log PoolAdded(_pool)


@external
def remove_pool(_pool: address):
    """
    @notice Remove a pool to the registry
    @dev Only callable by admin
    @param _pool Pool address to remove
    """
    assert msg.sender == self.address_provider.admin()  # dev: admin-only function
    assert self.get_lp_token[_pool] != ZERO_ADDRESS  # dev: pool does not exist

    # remove coin from markets
    coins: address[MAX_COINS] = self._get_coins(_pool)
    for i in range(MAX_COINS):
        if coins[i] == ZERO_ADDRESS:
            break
        self._unregister_coin(coins[i])

    # check if metapool and remove if there are markets:
    is_meta: bool = self.pool_data[_pool].base_pool != ZERO_ADDRESS
    ucoins: address[MAX_COINS] = empty(address[MAX_COINS])
    if is_meta:
        ucoins = self._get_underlying_coins_for_metapool(_pool)
        self.pool_data[_pool].base_pool = ZERO_ADDRESS

    for i in range(MAX_COINS):
        coin: address = coins[i]
        ucoin: address = ucoins[i]
        if coin == ZERO_ADDRESS and ucoin == ZERO_ADDRESS:
            break

        # remove pool from markets
        i2: int128 = i + 1
        for x in range(i2, i2 + MAX_COINS):
            ucoinx: address = ucoins[x]
            if ucoinx == ZERO_ADDRESS:
                break

            coinx: address = coins[x]
            if coinx != ZERO_ADDRESS:
                self._remove_market(_pool, coin, coinx)

            if coin != ucoin or coinx != ucoinx:
                self._remove_market(_pool, ucoin, ucoinx)

            if is_meta and not ucoin in coins:
                key: uint256 = bitwise_xor(convert(ucoin, uint256), convert(ucoinx, uint256))
                self._unregister_coin_pair(ucoin, ucoinx, key)

    # replace pool data:
    self.get_pool_from_lp_token[self.get_lp_token[_pool]] = ZERO_ADDRESS
    self.get_lp_token[_pool] = ZERO_ADDRESS

    # remove _pool from pool_list
    location: uint256 = self.pool_data[_pool].location
    length: uint256 = self.pool_count - 1

    self.pool_list[location] = ZERO_ADDRESS
    self.pool_count = length
    self.pool_data[_pool].name = ""
    self.pool_data[_pool].n_coins = 0

    if self.pool_data[_pool].has_positive_rebasing_tokens:
        self.pool_data[_pool].has_positive_rebasing_tokens = False

    if self.get_zap[_pool] != ZERO_ADDRESS:
        self.get_zap[_pool] = ZERO_ADDRESS

    self.last_updated = block.timestamp
    log PoolRemoved(_pool)


@external
def set_liquidity_gauges(_pool: address, _liquidity_gauges: address[10]):
    """
    @notice Set liquidity gauge contracts
    @param _pool Pool address
    @param _liquidity_gauges Liquidity gauge address
    """
    assert msg.sender == self.address_provider.admin()  # dev: admin-only function

    _lp_token: address = self.get_lp_token[_pool]
    for i in range(10):
        _gauge: address = _liquidity_gauges[i]
        if _gauge != ZERO_ADDRESS:
            assert LiquidityGauge(_gauge).lp_token() == _lp_token  # dev: wrong token
            self.liquidity_gauges[_pool][i] = _gauge
        elif self.liquidity_gauges[_pool][i] != ZERO_ADDRESS:
            self.liquidity_gauges[_pool][i] = ZERO_ADDRESS
        else:
            break
    self.last_updated = block.timestamp


@external
def batch_set_liquidity_gauges(_pools: address[10], _liquidity_gauges: address[10]):
    """
    @notice Set many liquidity gauge contracts
    @param _pools List of pool addresses
    @param _liquidity_gauges List of liquidity gauge addresses
    """
    assert msg.sender == self.address_provider.admin()  # dev: admin-only function

    for i in range(10):
        _pool: address = _pools[i]
        if _pool == ZERO_ADDRESS:
            break
        _gauge: address = _liquidity_gauges[i]
        assert LiquidityGauge(_gauge).lp_token() == self.get_lp_token[_pool]  # dev: wrong token
        self.liquidity_gauges[_pool][0] = _gauge

    self.last_updated = block.timestamp
