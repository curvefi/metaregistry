# @version 0.3.3
"""
@title Curve SynthSwap
@author Curve.fi
@license MIT
@notice Allows atomic cross-asset swaps via Curve and Synthetix
"""


interface AddressProvider:
    def get_address(_id: uint256) -> address: view


interface Curve:
    def get_dy(i: int128, j: int128, dx: uint256) -> uint256: view


interface MetaRegistry:
    def get_coins(_pool: address) -> address[8]: view
    def get_coin_indices(pool: address, _from: address, _to: address) -> (int128, int128, bool): view
    def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address: view
    def get_balances(_pool: address) -> uint256[8]: view


interface RegistrySwap:
    def exchange(
        _pool: address,
        _from: address,
        _to: address,
        _amount: uint256,
        _expected: uint256,
        _receiver: address,
    ) -> uint256: payable


interface SNXAddressResolver:
    def getAddress(name: bytes32) -> address: view


interface Synth:
    def currencyKey() -> bytes32: nonpayable


interface Exchanger:
    def getAmountsForAtomicExchange(
        sourceAmount: uint256,
        sourceCurrencyKey: bytes32,
        destinationCurrencyKey: bytes32
    ) -> (uint256, uint256, uint256): view
    def exchangeAtomically(
        sourceCurrencyKey: bytes32, 
        sourceAmount: uint256, 
        destinationCurrencyKey: bytes32,
        destinationAddress: address,
        trackingCode: bytes32, 
        minAmount: uint256
        ) -> uint256: payable


event NewSynth:
    synth: address
    pool: address


# the following registries will never change:
ADDRESS_PROVIDER: constant(address) = 0x0000000022D53366457F9d5E68Ec105046FC4383
SNX_ADDRESS_RESOLVER: constant(address) = 0x4E3b31eB0E5CB73641EE1E65E7dCEFe520bA3ef2
EXCHANGER_KEY: constant(bytes32) = 0x45786368616e6765720000000000000000000000000000000000000000000000

# affiliate program tracking code:
TRACKING_CODE: immutable(bytes32)
# Curve MetaRegistry
METAREGISTRY: immutable(address)

# coin -> synth that it can be swapped for
swappable_synth: public(HashMap[address, address])
# synth -> pool that it can be swapped at
synth_pool: public(HashMap[address, address])
# coin -> spender -> is approved to transfer from this contract?
is_approved: HashMap[address, HashMap[address, bool]]
# synth -> currency key
currency_keys: public(HashMap[address, bytes32])
# synthetix exchanger:
exchanger: Exchanger



@external
def __init__(tracking_code: bytes32, metaregistry: address):
    """
    @notice Contract constructor
    @param tracking_code tracking code for affiliate program
    @param metaregistry Curvefi MetaRegistry
    """
    self.exchanger = Exchanger(SNXAddressResolver(SNX_ADDRESS_RESOLVER).getAddress(EXCHANGER_KEY))
    TRACKING_CODE = tracking_code
    METAREGISTRY = metaregistry
    

@view
@internal
def _get_swap_into_synth(_from: address, _synth: address, _amount: uint256) -> uint256:
    intermediate_synth: address = self.swappable_synth[_from]
    pool: address = self.synth_pool[intermediate_synth]

    synth_amount: uint256 = _amount
    if _from != intermediate_synth:
        i: int128 = 0
        j: int128 = 0
        is_meta: bool = False
        i, j, is_meta = MetaRegistry(METAREGISTRY).get_coin_indices(pool, _from, intermediate_synth)
        synth_amount = Curve(pool).get_dy(i, j, _amount)

    return self.exchanger.getAmountsForAtomicExchange(
        synth_amount,
        self.currency_keys[intermediate_synth],
        self.currency_keys[_synth],
    )[0]


@view
@internal
def _get_registry_swap_amount(_pool: address, _from: address, _to: address, _amount: uint256) -> uint256:

    i: int128 = 0
    j: int128 = 0
    is_meta: bool = False
    i, j, is_meta = MetaRegistry(METAREGISTRY).get_coin_indices(_pool, _from, _to)

    success: bool = False
    response: Bytes[32] = b""
    success, response = raw_call(
        _pool, 
        concat(
            method_id("get_dy(uint256,uint256,uint256)"),
            convert(i, bytes32),
            convert(j, bytes32),
            convert(_amount, bytes32)
        ),
        max_outsize=32,
        revert_on_failure=False,
        is_static_call=True
    )

    if success:
        return convert(response, uint256)
    
    return Curve(_pool).get_dy(i, j, _amount)


@view
@external
def get_registry_swap_amount(_pool: address, _from: address, _to: address, _amount: uint256) -> uint256:
    return self._get_registry_swap_amount(_pool, _from, _to, _amount)


@view
@internal
def _find_best_pool_for_coins(_coin_in: address, _coin_out: address, _amount: uint256) -> address:

    _max_expected: uint256 = 0
    _expected: uint256 = 0
    _pool_balance_coin_0: uint256 = 0
    _pool: address = ZERO_ADDRESS
    _intermediate_pool: address = ZERO_ADDRESS

    for i in range(256):
        _intermediate_pool = MetaRegistry(METAREGISTRY).find_pool_for_coins(_coin_in, _coin_out, i)
        if _intermediate_pool == ZERO_ADDRESS:
            break

        _pool_balance_coin_0 = MetaRegistry(METAREGISTRY).get_balances(_intermediate_pool)[0]
        if _pool_balance_coin_0 == 0:
            continue

        _expected = self._get_registry_swap_amount(_intermediate_pool, _coin_in, _coin_out, _amount)

        if _expected >= _max_expected:
            _max_expected = _expected
            _pool = _intermediate_pool

    return _pool


@view
@internal
def _get_swap_from_synth(_synth: address, _to: address, _amount: uint256) -> uint256:
    _intermediate_synth: address = self.swappable_synth[_to]
    synth_amount: uint256 = _amount

    synth_amount = self.exchanger.getAmountsForAtomicExchange(
        synth_amount,
        self.currency_keys[_synth],
        self.currency_keys[_intermediate_synth],
    )[0]

    _pool: address = self._find_best_pool_for_coins(_synth, _to, _amount)
    return self._get_registry_swap_amount(_pool, _intermediate_synth, _to, synth_amount)


@view
@internal
def _is_registered_synth(_synth: address) -> bool:
    return self.synth_pool[_synth] != ZERO_ADDRESS


@view
@internal
def _is_registered_asset(_asset: address) -> bool:
    return self.swappable_synth[_asset] != ZERO_ADDRESS


@view
@external
def get_best_registry_swap_amount(_from: address, _to: address, _amount: uint256) -> uint256:
    _pool: address = self._find_best_pool_for_coins(_from, _to, _amount)
    return self._get_registry_swap_amount(_pool, _from, _to, _amount)


@view
@external
def get_atomic_swap_amount(_coin_in: address, _coin_out: address, _amount: uint256) -> uint256:   
    return self.exchanger.getAmountsForAtomicExchange(
        _amount, 
        self.currency_keys[self.swappable_synth[_coin_in]], 
        self.currency_keys[self.swappable_synth[_coin_out]]
    )[0]


@view
@external
def find_best_pool_for_coins(_coin_in: address, _coin_out: address, _amount: uint256) -> address:
    return self._find_best_pool_for_coins(_coin_in, _coin_out, _amount)


@view
@external
def get_estimated_swap_amount(_coin_in: address, _coin_out: address, _amount: uint256) -> uint256:
    """
    @notice Estimate the final amount received when swapping between `_coin_in` and `_coin_out`
    @param _coin_in Address of the initial asset being exchanged
    @param _coin_out Address of the asset to swap into
    @param _amount Amount of `_coin_in` being exchanged
    @return uint256 Estimated amount of `_coin_out` received
    """
    _expected: uint256 = 0
    _pool: address = self._find_best_pool_for_coins(_coin_in, _coin_out, _amount)

    # if _coin_in and _coin_out already have a Curve pool:
    if _pool != ZERO_ADDRESS:
        _expected = self._get_registry_swap_amount(_pool, _coin_in, _coin_out, _amount)

    # if `_from` is a synth, `_to` are synths, the just perform exchangeAtomically:
    elif self._is_registered_synth(_coin_in) and self._is_registered_synth(_coin_out):
        _expected = self.exchanger.getAmountsForAtomicExchange(
            _amount,
            self.currency_keys[_coin_in],
            self.currency_keys[_coin_out]
        )[0]

    # if `_from` is asset, `_to` is synth, then _swap_asset_into_synth
    elif self._is_registered_asset(_coin_in) and self._is_registered_synth(_coin_out):
        _expected = self._get_swap_into_synth(_coin_in, _coin_out, _amount)
    
    # if `_from` is synth and not `_to`, then _swap_synth_into_asset
    elif self._is_registered_synth(_coin_in) and self._is_registered_asset(_coin_out):
        _expected = self._get_swap_from_synth(_coin_in, _coin_out, _amount)

    # if both `_from` and `_to` are assets, then _swap_asset_into_synth 
    #    and then registry_swap to `_coin_out`
    elif self._is_registered_asset(_coin_in) and self._is_registered_asset(_coin_out):
        _intermediate_synth: address = self.swappable_synth[_coin_out]
        _expected =  self._get_swap_into_synth(_coin_in, _intermediate_synth, _amount)
        _pool = self._find_best_pool_for_coins(_intermediate_synth, _coin_out, _amount)
        _expected = self._get_registry_swap_amount(_pool, _intermediate_synth, _coin_out, _expected)

    return _expected


@internal
def _approve(_token: address, _contract: address):

    if not self.is_approved[_token][_contract]:
        response: Bytes[32] = raw_call(
            _token,
            concat(
                method_id("approve(address,uint256)"),
                convert(_contract, bytes32),
                convert(MAX_UINT256, bytes32),
            ),
            max_outsize=32,
        )
        if len(response) != 0:
            assert convert(response, bool)
        self.is_approved[_token][_contract] = True


@payable
@internal
def _swap_asset_into_synth(
    _asset: address,
    _synth: address,
    _amount: uint256,
    _expected: uint256 = 0,
    _receiver: address = self,
) -> uint256:
    """
    @notice Perform a cross-asset swap between `_asset` and `_synth`
    @notice All swaps in this method are internal. `self` must have non-zero `_asset` balance.
    @param _asset Address of the initial asset being exchanged
    @param _synth Address of the synth being swapped into
    @param _amount Amount of `_asset` to swap
    @param _expected Minimum amount of `_synth` to receive. Defaults to zero.
    @param _receiver Address that receives swapped `_synth`
    @return uint256 Amount received by `self`
    """
    registry_swap: address = AddressProvider(ADDRESS_PROVIDER).get_address(2)
    intermediate_synth: address = self.swappable_synth[_asset]
    synth_amount: uint256 = 0
    
    if _asset != 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        self._approve(_asset, registry_swap)

    # swap asset to intermediate synth
    synth_amount = RegistrySwap(registry_swap).exchange(
        self.synth_pool[intermediate_synth],
        _asset,
        intermediate_synth,
        _amount,
        0,                  # expected is 0
        self,               # `_receiver` is `self`
        value=msg.value
    )

    # notice: swapped amount goes to `_receiver`
    self._approve(intermediate_synth, self.exchanger.address)
    swap_out: uint256 = self.exchanger.exchangeAtomically(
        self.currency_keys[intermediate_synth],
        synth_amount,
        self.currency_keys[_synth],
        _receiver,
        TRACKING_CODE,
        _expected,
    )
    
    assert swap_out >= _expected, "Rekt by slippage"
    return swap_out


@payable
@internal
def _swap_synth_into_asset(
    _synth: address,
    _asset: address,
    _amount: uint256,
    _expected: uint256,
    _receiver: address = self
) -> uint256:
    """
    @notice Perform a cross-asset swap between `_synth` and `_asset`
    @notice `self` must have non-zero `_synth` balance
    @param _synth Address of the synth being swapped from
    @param _asset Address of the initial asset being exchanged into
    @param _amount Amount of `_synth` to swap
    @param _expected Minimum amount of `_asset` to receive
    @param _receiver Address of the recipient of `_to`, if not given
                       defaults to `self`
    @return uint256 Amount received by `self`
    """
    intermediate_synth: address = self.swappable_synth[_asset]
    self._approve(_synth, self.exchanger.address)
    
    # swap _synth to intermediate synth:
    swap_out: uint256 = self.exchanger.exchangeAtomically(
        self.currency_keys[_synth],
        _amount,
        self.currency_keys[intermediate_synth],
        self,               # `destinationAddress` is `self`
        TRACKING_CODE,
        0,                  # expected is zero
    )

    # swap intermediate sToken into _asset:
    registry_swap: address = AddressProvider(ADDRESS_PROVIDER).get_address(2)
    self._approve(intermediate_synth, registry_swap)
    _received: uint256 = RegistrySwap(registry_swap).exchange(
        self.synth_pool[intermediate_synth],
        intermediate_synth,
        _asset,
        swap_out,
        0,                  # expected is 0
        _receiver,          # swap to `_receiver` and finish swaps
    )
    assert _received >= _expected,  "Rekt by slippage"
    return _received


@payable
@external
def exchange(
    _coin_in: address, 
    _coin_out: address, 
    _amount: uint256, 
    _expected: uint256, 
    _receiver: address
) -> uint256:
    """
    @notice Perform a cross asset swap between `_coin_out` and `_coin_out`
    @param _coin_in Address of the initial asset being exchanged
    @param _coin_out Address of the final asset being swapped into
    @param _amount Amount of `_coin_out` to swap
    @param _expected Minimum amount of `_coin_out` to receive
    @param _receiver Address of the recipient of `_coin_out`, if not given
                       defaults to `msg.sender`
    @return uint256 Amount received by `msg.sender`
    """
    _received: uint256 = 0
    _pool: address = MetaRegistry(METAREGISTRY).find_pool_for_coins(_coin_in, _coin_out, 0)

    # transfer `_coin_in` to `self`:
    if _coin_in != 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        # Vyper equivalent of SafeERC20Transfer, handles most ERC20 return values
        response: Bytes[32] = raw_call(
            _coin_in,
            concat(
                method_id("transferFrom(address,address,uint256)"),
                convert(msg.sender, bytes32),
                convert(self, bytes32),
                convert(_amount, bytes32),
            ),
            max_outsize=32,
        )
        if len(response) != 0:
            assert convert(response, bool)


    # if _coin_in and _coin_out already have a Curve pool:
    if _pool != ZERO_ADDRESS:
        registry_swap: address = AddressProvider(ADDRESS_PROVIDER).get_address(2)
        _received = RegistrySwap(registry_swap).exchange(
            _pool,
            _coin_in,
            _coin_out,
            _received,
            _expected,
            msg.sender,
        )

    # if `_from` is a synth, `_to` is a synth, the just perform exchangeAtomically:
    elif self._is_registered_synth(_coin_in) and self._is_registered_synth(_coin_out):
        _received = self.exchanger.exchangeAtomically(
            self.currency_keys[_coin_in],
            _amount,
            self.currency_keys[_coin_out],
            msg.sender,
            TRACKING_CODE,
            _expected,
        )

    # if `_from` is asset, `_to` is, then _swap_asset_into_synth
    elif self._is_registered_asset(_coin_in) and self._is_registered_synth(_coin_out):
        _received = self._swap_asset_into_synth(
            _coin_in,
            _coin_out,
            _amount,
            _expected,
            msg.sender,
        )
    
    # if `_from` is synth and not `_to`, then _swap_synth_into_asset
    elif self._is_registered_synth(_coin_in) and self._is_registered_asset(_coin_out):
        _received = self._swap_synth_into_asset(
            _coin_in,
            _coin_out,
            _amount,
            _expected,
            msg.sender,
        )

    # if both `_from` and `_to` are assets, then _swap_asset_into_synth and then registry_swap to `_coin_out`
    elif self._is_registered_asset(_coin_in) and self._is_registered_asset(_coin_out):
        _intermediate_synth: address = self.swappable_synth[_coin_out]
        registry_swap: address = AddressProvider(ADDRESS_PROVIDER).get_address(2)
        _received = self._swap_asset_into_synth(
            _coin_in,
            _intermediate_synth,
            _amount,
            0,
            self,
        )
        self._approve(_intermediate_synth, registry_swap)
        _received = RegistrySwap(registry_swap).exchange(
            self.synth_pool[_intermediate_synth],
            _intermediate_synth,
            _coin_out,
            _received,
            _expected,
            msg.sender,
        )

    assert _received != 0, "Could not find swap"
    return _received


@payable
@external
def exchange_through_synth(
    _coin_in: address, 
    _coin_out: address, 
    _amount: uint256, 
    _expected: uint256, 
    _receiver: address
) -> uint256:
    """
    @notice Perform a cross asset swap through Synthetix between `_coin_out` and `_coin_out`
    @param _coin_in Address of the initial asset being exchanged
    @param _coin_out Address of the final asset being swapped into
    @param _amount Amount of `_coin_out` to swap
    @param _expected Minimum amount of `_coin_out` to receive
    @param _receiver Address of the recipient of `_coin_out`, if not given 
                    defaults to `msg.sender`
    @return uint256 Amount received by `msg.sender`
    """
    # transfer `_coin_in` to `self`:
    if _coin_in != 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        # Vyper equivalent of SafeERC20Transfer, handles most ERC20 return values
        response: Bytes[32] = raw_call(
            _coin_in,
            concat(
                method_id("transferFrom(address,address,uint256)"),
                convert(msg.sender, bytes32),
                convert(self, bytes32),
                convert(_amount, bytes32),
            ),
            max_outsize=32,
        )
        if len(response) != 0:
            assert convert(response, bool)

    _intermediate_synth: address = self.swappable_synth[_coin_out]
    registry_swap: address = AddressProvider(ADDRESS_PROVIDER).get_address(2)
    _received: uint256 = self._swap_asset_into_synth(
        _coin_in,
        _intermediate_synth,
        _amount,
        0,
        self,
    )
    self._approve(_intermediate_synth, registry_swap)
    _received = RegistrySwap(registry_swap).exchange(
        self.synth_pool[_intermediate_synth],
        _intermediate_synth,
        _coin_out,
        _received,
        _expected,
        msg.sender,
    )

    assert _received != 0, "Could not find swap"
    return _received


@external
def add_synth(_synth: address, _pool: address):
    """
    @notice Add a new swappable synth
    @dev Callable by anyone, however `_pool` must exist within the Curve
         pool registry and `_synth` must be a valid synth that is swappable
         within the pool
    @param _synth Address of the synth to add
    @param _pool Address of the Curve pool where `_synth` is swappable
    """
    assert self.synth_pool[_synth] == ZERO_ADDRESS, "dev: already added"

    # this will revert if `_synth` is not actually a synth
    self.currency_keys[_synth] = Synth(_synth).currencyKey()
    pool_coins: address[8] = MetaRegistry(METAREGISTRY).get_coins(_pool)
    has_synth: bool = False
    for coin in pool_coins:
        if coin == ZERO_ADDRESS:
            assert has_synth, "dev: synth not in pool"
            break
        if coin == _synth:
            self.synth_pool[_synth] = _pool
            has_synth = True
        self.swappable_synth[coin] = _synth

    log NewSynth(_synth, _pool)


@external
def rebuildCache():
    """
    @notice Update the current address of the SNX Exchanger contract
    """
    self.exchanger = Exchanger(SNXAddressResolver(SNX_ADDRESS_RESOLVER).getAddress(EXCHANGER_KEY))