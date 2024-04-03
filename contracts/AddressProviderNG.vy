# @version 0.3.10
"""
@title CurveAddressProvider
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2020-2023 - all rights reserved
@notice An entrypoint contract for Curve's various registries
@dev Allows adding arbitrary IDs instead of sequential IDs.
"""

event NewEntry:
    id: indexed(uint256)
    addr: address
    description: String[64]

event EntryModified:
    id: indexed(uint256)
    version: uint256

event EntryRemoved:
    id: indexed(uint256)

event CommitNewAdmin:
    admin: indexed(address)

event NewAdmin:
    admin: indexed(address)


struct AddressInfo:
    addr: address
    description: String[256]
    version: uint256
    last_modified: uint256


admin: public(address)
future_admin: public(address)

num_entries: public(uint256)
check_id_exists: public(HashMap[uint256, bool])
_ids: DynArray[uint256, 1000]
get_id_info: public(HashMap[uint256, AddressInfo])


@external
def __init__(_admin: address):
    self.admin = _admin


# ------------------------------ View Methods --------------------------------

@view
@external
def ids() -> DynArray[uint256, 1000]:
    """
    @notice returns IDs of active registry items in the AddressProvider.
    @returns An array of IDs.
    """
    _ids: DynArray[uint256, 1000] = []
    for _id in self._ids:
        if self.check_id_exists[_id]:
            _ids.append(_id)

    return _ids


@view
@external
def get_address(_id: uint256) -> address:
    """
    @notice Fetch the address associated with `_id`
    @dev Returns empty(address) if `_id` has not been defined, or has been unset
    @param _id Identifier to fetch an address for
    @return Current address associated to `_id`
    """
    return self.get_id_info[_id].addr


# -------------------------- State-Mutable Methods ---------------------------


@internal
def _update_entry_metadata(_id: uint256):

    version: uint256 = self.get_id_info[_id].version + 1
    self.get_id_info[_id].version = version
    self.get_id_info[_id].last_modified = block.timestamp

    log EntryModified(_id, version)


@external
def add_new_id(
    _id: uint256,
    _address: address,
    _description: String[64],
):
    """
    @notice Enter a new registry item
    @param _id Address assigned to the input _id
    @param _address Address assigned to the _id
    @param _description Human-readable description of the identifier
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert not self.check_id_exists[_id]  # dev: id exists

    self.check_id_exists[_id] = True
    self._ids.append(_id)

    # Add entry:
    self.get_id_info[_id] = AddressInfo(
        {
            addr: _address,
            description: _description,
            version: 1,
            last_modified: block.timestamp,
        }
    )
    self.num_entries += 1

    log NewEntry(_id, _address, _description)


@external
def update_id(
    _id: uint256,
    _new_address: address,
    _new_description: String[64],
):
    """
    @notice Update entries at an ID
    @param _id Address assigned to the input _id
    @param _new_address Address assigned to the _id
    @param _new_description Human-readable description of the identifier
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.check_id_exists[_id]  # dev: id does not exist

    # Update entry at _id:
    self.get_id_info[_id].addr = _new_address
    self.get_id_info[_id].description = _new_description

    # Update metadata (version, update time):
    self._update_entry_metadata(_id)


@external
def update_address(_id: uint256, _address: address):
    """
    @notice Set a new address for an existing identifier
    @param _id Identifier to set the new address for
    @param _address Address to set
    """
    assert msg.sender == self.admin  # dev: admin-only function

    # Update address:
    self.get_id_info[_id].addr = _address

    # Update metadata (version, update time):
    self._update_entry_metadata(_id)


@external
def update_description(_id: uint256, _description: String[256]):
    """
    @notice Update description for an existing _id
    @param _id Identifier to set the new description for
    @param _description New description to set
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.get_id_info[_id].addr != empty(address)  # dev: id is empty

    # Update description:
    self.get_id_info[_id].description = _description

    # Update metadata (version, update time):
    self._update_entry_metadata(_id)


@external
def remove_id(_id: uint256) -> bool:
    """
    @notice Unset an existing identifier
    @dev An identifier cannot ever be removed, it can only have the
         address unset so that it returns empty(address)
    @param _id Identifier to unset
    @return bool success
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.get_id_info[_id].addr != empty(address)  # dev: inactive id

    # Clear ID:
    self.get_id_info[_id].addr = empty(address)
    self.get_id_info[_id].last_modified = 0
    self.get_id_info[_id].description = ''
    self.get_id_info[_id].version = 0

    self.check_id_exists[_id] = False

    # Reduce num entries:
    self.num_entries -= 1

    # Emit 0 in version to notify removal of id:
    log EntryRemoved(_id)

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
    self.future_admin = _new_admin

    log CommitNewAdmin(_new_admin)

    return True


@external
def apply_transfer_ownership() -> bool:
    """
    @notice Finalize a transfer of contract ownership
    @dev May only be called by the next owner
    @return bool success
    """
    assert msg.sender == self.future_admin  # dev: admin-only function

    new_admin: address = self.future_admin
    self.admin = new_admin

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
    self.future_admin = empty(address)

    return True
