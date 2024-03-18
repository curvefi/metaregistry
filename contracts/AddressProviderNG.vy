# @version 0.3.10
"""
@title CurveAddressProvider
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2020-2023 - all rights reserved
@notice An entrypoint contract for Curve's various registries
"""

event NewAddressIdentifier:
    id: indexed(uint256)
    addr: address
    description: String[64]

event AddressModified:
    id: indexed(uint256)
    new_address: address
    version: uint256

event CommitNewAdmin:
    deadline: indexed(uint256)
    admin: indexed(address)

event NewAdmin:
    admin: indexed(address)


struct AddressInfo:
    addr: address
    type: String[64]
    description: String[256]
    version: uint256
    is_active: bool
    last_modified: uint256


registry: address
admin: public(address)
transfer_ownership_deadline: public(uint256)
future_admin: public(address)

queue_length: uint256
get_id_info: public(HashMap[uint256, AddressInfo])
get_ids_for_type: public(HashMap[String[64], DynArray[uint256, 1000]])


@external
def __init__(_admin: address):
    self.admin = _admin


# -------------------------- State-Mutable Methods ---------------------------


@view
@external
def max_id() -> uint256:
    """
    @notice Get the highest ID set within the address provider
    @return uint256 max ID
    """
    return self.queue_length - 1


@view
@external
def get_address(_id: uint256) -> address:
    """
    @notice Fetch the address associated with `_id`
    @dev Returns ZERO_ADDRESS if `_id` has not been defined, or has been unset
    @param _id Identifier to fetch an address for
    @return Current address associated to `_id`
    """
    return self.get_id_info[_id].addr


# -------------------------- State-Mutable Methods ---------------------------


@external
def add_new_type(_new_type: String[64]):
    self.types


@external
def add_new_id(
    _address: address, 
    _type: String[64],
    _id: uint256,
    _description: String[64]
) -> uint256:
    """
    @notice Add a new identifier to the registry
    @param _address Initial address to assign to new identifier
    @param _type keccak hash of the type of entry. For e.g. keccak(b'StableSwap')
    @param _id ID to assign the address to
    @param _description Human-readable description of the identifier
    @return uint256 identifier
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.get_id_info[_id].addr == empty(address)  # dev: id occupied

    id: uint256 = self.queue_length
    self.get_id_info[id] = AddressInfo({
        addr: _address,
        type: String[64],
        description: _description,
        version: 1,
        is_active: True,
        last_modified: block.timestamp,
    })
    self.queue_length = id + 1

    log NewAddressIdentifier(id, _address, _description)

    return id


@external
def set_address(_id: uint256, _address: address) -> bool:
    """
    @notice Set a new address for an existing identifier
    @param _id Identifier to set the new address for
    @param _address Address to set
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert _address.is_contract  # dev: not a contract
    assert self.queue_length > _id  # dev: id does not exist

    version: uint256 = self.get_id_info[_id].version + 1

    self.get_id_info[_id].addr = _address
    self.get_id_info[_id].is_active = True
    self.get_id_info[_id].version = version
    self.get_id_info[_id].last_modified = block.timestamp

    if _id == 0:
        self.registry = _address

    log AddressModified(_id, _address, version)

    return True


@external
def unset_address(_id: uint256) -> bool:
    """
    @notice Unset an existing identifier
    @dev An identifier cannot ever be removed, it can only have the
         address unset so that it returns empty(address)
    @param _id Identifier to unset
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.get_id_info[_id].is_active  # dev: not active

    self.get_id_info[_id].is_active = False
    self.get_id_info[_id].addr = empty(address)
    self.get_id_info[_id].last_modified = block.timestamp
    self.get_id_info[_id].description = empty(String[64])

    if _id == 0:
        self.registry = empty(address)

    log AddressModified(_id, empty(address), self.get_id_info[_id].version)

    return True


# ------------------------------ Admin Methods -------------------------------


@external
def commit_transfer_ownership(_new_admin: address) -> bool:
    """
    @notice Initiate a transfer of contract ownership
    @dev Once initiated, the actual transfer may be performed three days later
    @param _new_admin Address of the new owner account
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.transfer_ownership_deadline == 0  # dev: transfer already active

    deadline: uint256 = block.timestamp + 3*86400
    self.transfer_ownership_deadline = deadline
    self.future_admin = _new_admin

    log CommitNewAdmin(deadline, _new_admin)

    return True


@external
def apply_transfer_ownership() -> bool:
    """
    @notice Finalize a transfer of contract ownership
    @dev May only be called by the current owner, three days after a
         call to `commit_transfer_ownership`
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.transfer_ownership_deadline != 0  # dev: transfer not active
    assert block.timestamp >= self.transfer_ownership_deadline  # dev: now < deadline

    new_admin: address = self.future_admin
    self.admin = new_admin
    self.transfer_ownership_deadline = 0

    log NewAdmin(new_admin)

    return True


@external
def revert_transfer_ownership() -> bool:
    """
    @notice Revert a transfer of contract ownership
    @dev May only be called by the current owner
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin-only function

    self.transfer_ownership_deadline = 0

    return True