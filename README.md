# Curve Metaregistry

### TODO: 
- Fix the pool removal logic to account for when a factory pool is removed from a registry (and therefore not from factory registry)
- Handle de-registering coins when a pool is removed
- Add categorization scheme and query for pools
- Add `get_coin_indices` 
- Speed up test set up
- Fix / improve the `is_active` logic for registries
- Refactor `get_A`, `get_gamma` etc into `get_params` with buffer for potential future new pool params