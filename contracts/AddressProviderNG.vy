# @version 0.3.10
"""
@title CurveAddressProvider
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2020-2023 - all rights reserved
@notice An entrypoint contract for Curve's various registries
"""

event NewEntry:
    id: indexed(uint256)
    addr: address
    description: String[64]

event EntryModified:
    id: indexed(uint256)
    version: uint256

event CommitNewAdmin:
    deadline: indexed(uint256)
    admin: indexed(address)

event NewAdmin:
    admin: indexed(address)


struct AddressInfo:
    addr: address
    description: String[256]
    tags: DynArray[String[64], 20]
    version: uint256
    last_modified: uint256


admin: public(address)
transfer_ownership_deadline: public(uint256)
future_admin: public(address)

num_entries: public(uint256)
check_tag_exists: public(HashMap[String[64], bool])
check_id_exists: public(HashMap[uint256, bool])
ids: public(DynArray[uint256, 1000])
tags: public(DynArray[String[64], 1000])
id_tag_mapping: HashMap[bytes32, bool]
get_id_info: public(HashMap[uint256, AddressInfo])


@external
def __init__(_admin: address):
    self.admin = _admin


# ------------------------------ View Methods --------------------------------


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


@view
@external
def get_addresses_for_tags(_tag: String[64]) -> DynArray[address, 100]:
    """
    @notice Fetch all addresses that are tagged with `_tag`
    @param _tag tag to fetch an address for
    @return Array of addresses tagged with `_tag`
    """

    tagged_ids: DynArray[address, 100] = []
    for _id in self.ids:
        if self.id_tag_mapping[keccak256(concat(uint2str(_id), _tag))]:
            tagged_ids.append(self.get_id_info[_id].addr)

    return tagged_ids


# -------------------------- State-Mutable Methods ---------------------------


@external
def add_new_tags(_new_tags: DynArray[String[64], 20]):
    """
    @notice Add new tag
    @dev method allows a max number of entry of 20
    @param _new_tags An array of types to add to the registry
           e.g. ['StableSwap', 'CryptoSwap', ...] 
    """
    for _new_tag in _new_tags:
        if not self.check_tag_exists[_new_tag]:
            self.check_tag_exists[_new_tag] = True
            self.tags.append(_new_tag)


@internal
def _update_entry_metadata(_id: uint256):

    version: uint256 = self.get_id_info[_id].version + 1
    self.get_id_info[_id].version = version
    self.get_id_info[_id].last_modified = block.timestamp

    log EntryModified(_id, version)


@external
def add_new_id(
    _address: address, 
    _id: uint256,
    _tags: DynArray[String[64], 20],
    _description: String[64],
):
    """
    @notice Enter a new registry item
    @param _address Address assigned to the _id
    @param _id Address assigned to the input _id
    @param _tags tags defining the entry. e.g. ['StableSwap', 'Factory']
                 Entry can have a maximum of 20 tags. Tags need to be
                 added to the AddressProvider via `add_new_tags` before id can be added.
    @param _description Human-readable description of the identifier
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert not self.check_id_exists[_id]  # dev: id exists
    assert len(_tags) > 0  # dev: entry needs at least one tag

    self.check_id_exists[_id] = True
    self.ids.append(_id)

    # Check if tags are correct and add them to tag > id mapping:
    for _tag in _tags:
        assert self.check_tag_exists[_tag]  # dev: unrecognised tag
        self.id_tag_mapping[
            keccak256(concat(uint2str(_id), _tag))
        ] = True

    # Add entry:
    self.get_id_info[_id] = AddressInfo(
        {
            addr: _address,
            description: _description,
            tags: _tags,
            version: 1,
            last_modified: block.timestamp,
        }
    )
    self.num_entries += 1

    log NewEntry(_id, _address, _description)


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
def update_tags(_id: uint256, _tags: DynArray[String[64], 20]):
    """
    @notice Update tags for an existing _id
    @param _id Identifier to set the new description for
    @param _tags New tags to set to
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.get_id_info[_id].addr != empty(address)  # dev: id is empty

    # Update tags:
    self.get_id_info[_id].tags = _tags

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

    self.get_id_info[_id].addr = empty(address)
    self.get_id_info[_id].last_modified = block.timestamp
    self.get_id_info[_id].description = ''
    self.get_id_info[_id].tags = []
    self.get_id_info[_id].version = 0

    self.num_entries -= 1

    self.check_id_exists[_id] = False

    # Emit 0 in version to notify removal of id:
    log EntryModified(_id, 0)

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