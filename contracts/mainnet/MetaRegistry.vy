# @version 0.3.3
"""
@title Curve Meta Registry
@license MIT
"""

# ---- interfaces ---- #
interface AddressProvider:
    def admin() -> address: view
    def get_address(_id: uint256) -> address: view
    def get_id_info(_id: uint256) -> ((address, bool, uint256, uint256, String[64])): view

interface RegistryHandler:
    def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address: view
    def get_admin_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_base_pool(_pool: address) -> address: view
    def get_coins(_pool: address) -> address[MAX_COINS]: view
    def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool): view
    def get_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def get_fees(_pool: address) -> uint256[10]: view
    def get_gauges(_pool: address) -> (address[10], int128[10]): view
    def get_lp_token(_pool: address) -> address: view
    def get_n_coins(_pool: address) -> uint256: view
    def get_n_underlying_coins(_pool: address) -> uint256: view
    def get_pool_asset_type(_pool: address) -> uint256: view
    def get_pool_from_lp_token(_lp_token: address) -> address: view
    def get_pool_name(_pool: address) -> String[64]: view
    def get_pool_params(_pool: address) -> uint256[20]: view
    def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]: view
    def get_underlying_coins(_pool: address) -> address[MAX_COINS]: view
    def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]: view
    def is_meta(_pool: address) -> bool: view
    def is_registered(_pool: address) -> bool: view
    def pool_count() -> uint256: view
    def pool_list(_index: uint256) -> address: view


interface CurvePool:
    def get_virtual_price() -> uint256: view

# ---- events ---- #
event CommitNewAdmin:
    deadline: indexed(uint256)
    admin: indexed(address)

event NewAdmin:
    admin: indexed(address)


# ---- structs ---- #
struct Registry:
    addr: address
    id: uint256 # id in the address provider
    registry_handler: address # contract with custom logic to id (sub)categories
    description: String[64]
    is_active: bool


# ---- constants ---- #
MAX_REGISTRIES: constant(uint256) = 64
MAX_COINS: constant(uint256) = 8
ADMIN_ACTIONS_DELAY: constant(uint256) = 3 * 86400


# ---- storage variables ---- #
address_provider: public(AddressProvider)
admin_actions_deadline: public(uint256)
transfer_ownership_deadline: public(uint256)

owner: public(address)
future_owner: public(address)

get_registry: public(HashMap[uint256, Registry]) # get registry by index, index starts at 0
registry_length: public(uint256)



# ---- constructor ---- #
@external
def __init__(_owner: address, address_provider: address):
    self.owner = _owner
    self.address_provider = AddressProvider(address_provider)


# ---- internal methods ---- #
@internal
def _update_single_registry(_index: uint256, _addr: address, _id: uint256, _registry_handler: address, _description: String[64], _is_active: bool):
    assert _index <= self.registry_length

    if _index == self.registry_length:
        self.registry_length += 1

    self.get_registry[_index] = Registry({addr: _addr, id: _id, registry_handler: _registry_handler, description: _description, is_active: _is_active})


@internal
@view
def _get_pool_from_lp_token(_token: address) -> address:
    for i in range(MAX_REGISTRIES):
        if i == self.registry_length:
            break
        handler: address = self.get_registry[i].registry_handler
        pool: address = RegistryHandler(handler).get_pool_from_lp_token(_token)
        if pool != ZERO_ADDRESS:
            return pool
    return ZERO_ADDRESS


@internal
@view
def _get_registry_handler_from_pool(_pool: address) -> address:
    """
    @dev sometimes a factory pool can be registered in a manual registry
         because of this, we always take the last registry a pool is
         registered in and not the first, as manual registries are first
         and factories come later
    """

    pool_registry_handler: address = ZERO_ADDRESS
    for i in range(MAX_REGISTRIES):

        if i == self.registry_length:
            break
        handler: address = self.get_registry[i].registry_handler

        if self.get_registry[i].is_active and RegistryHandler(handler).is_registered(_pool):
            pool_registry_handler = handler

    if pool_registry_handler == ZERO_ADDRESS:
        raise("no registry")
    return pool_registry_handler


# ---- most used methods: Admin / DAO privileged methods ---- #
@external
def add_registry_by_address_provider_id(_id: uint256, _registry_handler: address):
    """
    @notice Add a registry from the address provider entry
    @param _id Id number in the address provider
    @param _registry_handler Address of the handler contract
    """
    assert msg.sender == self.owner  # dev: only owner

    addr: address = ZERO_ADDRESS
    is_active: bool = False
    version: uint256 = 0
    last_modified: uint256 = 0
    description: String[64] = ""

    (addr, is_active, version, last_modified, description) = self.address_provider.get_id_info(_id)
    self._update_single_registry(self.registry_length, addr, _id, _registry_handler, description, is_active)


@external
def switch_registry_active_status(_index: uint256):
    """
    @notice Disables an active registry (and vice versa)
    @param _index The index of the registry in get_registry
    """
    assert msg.sender == self.owner  # dev: only owner
    assert _index < self.registry_length

    registry: Registry = self.get_registry[_index]
    self._update_single_registry(_index, registry.addr, registry.id, registry.registry_handler, registry.description, not registry.is_active)


@external
def update_address_provider(_provider: address):
    """
    @notice Update the address provider contract
    @dev Only callable by admin
    @param _provider New provider address
    """
    assert msg.sender == self.owner  # dev: only owner
    assert _provider != ZERO_ADDRESS  # dev: not to zero
    self.address_provider = AddressProvider(_provider)


@external
def update_registry_addresses() -> uint256:
    """
    @notice Updates all out-of-date registry addresses from the address provider
    @return The number of updates applied
    """
    assert msg.sender == self.owner  # dev: only owner

    addr: address = ZERO_ADDRESS
    is_active: bool = False
    version: uint256 = 0
    last_modified: uint256 = 0
    description: String[64] = ""
    count: uint256 = 0

    for i in range(MAX_REGISTRIES):
        if i == self.registry_length:
            break
        registry: Registry = self.get_registry[i]
        if registry.is_active and registry.addr != self.address_provider.get_address(registry.id):
            (addr, is_active, version, last_modified, description) = self.address_provider.get_id_info(i)
            self._update_single_registry(i, addr, registry.id, registry.registry_handler, description, is_active)
            count += 1
    return count


@external
def update_registry_handler(_index: uint256, _registry_handler: address):
    """
    @notice Updates the contract used to handle a registry
    @param _index The index of the registry in get_registry
    @param _registry_handler Address of the new handler contract
    """
    assert msg.sender == self.owner  # dev: only owner
    assert _index < self.registry_length

    registry: Registry = self.get_registry[_index]
    self._update_single_registry(_index, registry.addr, registry.id, _registry_handler, registry.description, registry.is_active)


@external
def update_single_registry(_index: uint256, _addr: address, _id: uint256, _registry_handler: address, _description: String[64], _is_active: bool):
    """
    @notice Creates or update a single registry entry
    @param _index The index of the registry in get_registry, equals to registry_length for new entry
    @param _addr Address of the registry contract
    @param _id Id number in the address provider
    @param _registry_handler Address of the handler contract
    @param _description Name of the registry
    @param _is_active Whether registry is active
    """
    assert msg.sender == self.owner  # dev: only owner

    self._update_single_registry(_index, _addr, _id, _registry_handler, _description, _is_active)


# ---- view methods (API) of the contract ---- #
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
    local_index: uint256 = 0
    pool: address = ZERO_ADDRESS
    for registry_index in range(MAX_REGISTRIES):
        if registry_index == self.registry_length:
            break
        registry: RegistryHandler = RegistryHandler(self.get_registry[registry_index].registry_handler)
        for j in range(0, 65536):
            pool = registry.find_pool_for_coins(_from, _to, j)
            if pool == ZERO_ADDRESS:
                break
            local_index += 1
            if local_index > i:
                return pool
    return pool


@external
@view
def get_admin_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get the current admin balances (uncollected fees) for a pool
    @param _pool Pool address
    @return List of uint256 admin balances
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_admin_balances(_pool)


@external
@view
def get_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get balances for each coin within a pool
    @dev For metapools, these are the wrapped coin balances
    @param _pool Pool address
    @return uint256 list of balances
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_balances(_pool)


@external
@view
def get_base_pool(_pool: address) -> address:
    """
    @notice Get the base pool for a given factory metapool
    @dev Will return ZERO_ADDRESS if pool is not a metapool
    @param _pool Metapool address
    @return Address of base pool
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_base_pool(_pool)


@view
@external
def get_coin_indices(_pool: address, _from: address, _to: address) -> (int128, int128, bool):
    """
    @notice Convert coin addresses to indices for use with pool methods
    @param _pool Pool address
    @param _from Coin address to be used as `i` within a pool
    @param _to Coin address to be used as `j` within a pool
    @return from index, to index, is the market underlying ?
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_coin_indices(_pool, _from, _to)


@external
@view
def get_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the coins within a pool
    @dev For metapools, these are the wrapped coin addresses
    @param _pool Pool address
    @return List of coin addresses
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_coins(_pool)


@external
@view
def get_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get decimal places for each coin within a pool
    @dev For metapools, these are the wrapped coin decimal places
    @param _pool Pool address
    @return uint256 list of decimals
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_decimals(_pool)


@external
@view
def get_fees(_pool: address) -> uint256[10]:
    """
    @dev Fees are expressed as integers
    @return Pool fee as uint256 with 1e10 precision
            Admin fee as 1e10 percentage of pool fee
            Mid fee
            Out fee
            6 blank spots for future use cases
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_fees(_pool)


@external
@view
def get_gauges(_pool: address) -> (address[10], int128[10]):
    """
    @notice Get a list of LiquidityGauge contracts associated with a pool
    @param _pool Pool address
    @return address[10] of gauge addresses, int128[10] of gauge types
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_gauges(_pool)


@external
@view
def get_lp_token(_pool: address) -> address:
    """
    @notice Get the address of the LP token of a pool
    @return Address of the LP token
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_lp_token(_pool)


@external
@view
def get_n_coins(_pool: address) -> uint256:
    """
    @notice Get the number of coins in a pool
    @dev For metapools, it is tokens + wrapping/lending token (no underlying)
    @param _pool Pool address
    @return Number of coins
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_n_coins(_pool)


@external
@view
def get_n_underlying_coins(_pool: address) -> uint256:
    """
    @notice Get the number of underlying coins in a pool
    @dev For non metapools, returns the same as get_n_coins
    @param _pool Pool address
    @return Number of coins
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_n_underlying_coins(_pool)


@external
@view
def get_pool_asset_type(_pool: address) -> uint256:
    """
    @notice Query the asset type of `_pool`
    @param _pool Pool Address
    @return The asset type as an unstripped string
    @dev 0 : USD, 1: ETH, 2: BTC, 3: Other, 4: CryptoSwap
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_pool_asset_type(_pool)


@external
@view
def get_pool_from_lp_token(_token: address) -> address:
    """
    @notice Get the pool associated with an LP token
    @param _token LP token address
    @return Pool address
    """
    return self._get_pool_from_lp_token(_token)


@external
@view
def get_pool_name(_pool: address) -> String[64]:
    """
    @notice Get the given name for a pool
    @param _pool Pool address
    @return The name of a pool
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_pool_name(_pool)


@external
@view
def get_pool_params(_pool: address) -> uint256[20]:
    """
    @notice Return pool parameters for a
    @param _pool address of the pool
    @return uint256[20] zero-padded array containing pool params
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_pool_params(_pool)


@external
@view
def get_registry_handler_from_pool(_pool: address) -> address:
    return self._get_registry_handler_from_pool(_pool)


@external
@view
def get_underlying_balances(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get balances for each underlying coin within a pool
    @dev For non metapools, returns the same value as `get_balances`
    @param _pool Pool address
    @return uint256 list of underlyingbalances
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_underlying_balances(_pool)


@external
@view
def get_underlying_coins(_pool: address) -> address[MAX_COINS]:
    """
    @notice Get the underlying coins within a pool
    @dev For non metapools, returns the same value as `get_coins`
    @param _pool Pool address
    @return List of coin addresses
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_underlying_coins(_pool)


@external
@view
def get_underlying_decimals(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get decimal places for each underlying coin within a pool
    @dev For non metapools, returns the same value as `get_decimals`
    @param _pool Pool address
    @return uint256 list of decimals
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).get_underlying_decimals(_pool)


@external
@view
def get_virtual_price_from_lp_token(_token: address) -> uint256:
    """
    @notice Get the virtual price of a pool LP token
    @param _token LP token address
    @return uint256 Virtual price
    """
    return CurvePool(self._get_pool_from_lp_token(_token)).get_virtual_price()


@external
@view
def is_meta(_pool: address) -> bool:
    """
    @notice Verify `_pool` is a metapool
    @param _pool Pool address
    @return True if `_pool` is a metapool
    """
    return RegistryHandler(self._get_registry_handler_from_pool(_pool)).is_meta(_pool)


@external
@view
def is_registered(_pool: address) -> bool:
    """
    @notice Check if a pool is in the metaregistry using get_n_coins
    @param _pool The address of the pool
    @return A bool corresponding to whether the pool belongs or not
    """
    return self._get_registry_handler_from_pool(_pool) != ZERO_ADDRESS


@external
@view
def pool_count() -> uint256:
    """
    @notice Return the total number of pools tracked by the metaregistry
    """
    total_pools: uint256 = 0
    for i in range(MAX_REGISTRIES):
        if i == self.registry_length:
            break
        handler: address = self.get_registry[i].registry_handler
        total_pools += RegistryHandler(handler).pool_count()
    return total_pools


@external
@view
def pool_list(_index: uint256) -> address:
    """
    @notice Return the pool at a given index in the metaregistry
    """
    pools_skip: uint256 = 0
    for i in range(MAX_REGISTRIES):
        if i == self.registry_length:
            break
        handler: address = self.get_registry[i].registry_handler
        count: uint256 = RegistryHandler(handler).pool_count()
        if _index - pools_skip < count:
            return RegistryHandler(handler).pool_list(_index - pools_skip)
        pools_skip += count
    return ZERO_ADDRESS


# ---- lesser used methods go here (slightly more gas optimal) ---- #
# -- admin ownership transfer methods -- #
@external
def commit_transfer_ownership(_owner: address):
    assert msg.sender == self.owner  # dev: only owner
    assert self.transfer_ownership_deadline == 0  # dev: active transfer

    _deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY
    self.transfer_ownership_deadline = _deadline
    self.future_owner = _owner

    log CommitNewAdmin(_deadline, _owner)


@external
def apply_transfer_ownership():
    assert msg.sender == self.owner  # dev: only owner
    assert block.timestamp >= self.transfer_ownership_deadline  # dev: insufficient time
    assert self.transfer_ownership_deadline != 0  # dev: no active transfer

    self.transfer_ownership_deadline = 0
    _owner: address = self.future_owner
    self.owner = _owner

    log NewAdmin(_owner)


@external
def revert_transfer_ownership():
    assert msg.sender == self.owner  # dev: only owner

    self.transfer_ownership_deadline = 0
