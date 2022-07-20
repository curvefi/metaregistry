import ape
import warnings


def check_pool_already_registered(
    metaregistry, pool, registry_handler_for_pool, handler_id: int = 0
):
    """Checks whether the pool was already registered in a different registry.

    Args:
        metaregistry (fixture): MetaRegistry contract fixture.
        pool (str): address of pool
        registry (Contract): Contract instance of registry.
        handler_id (int): 0 if pool is registered at only 1 registry, > 0 otherwise.
    """
    registery_handlers = metaregistry.get_registry_handlers_from_pool(pool)

    if len([1 for handler in registery_handlers if handler != ape.utils.ZERO_ADDRESS]) > 1:
        warnings.warn(f"Pool {pool}registery_handlersis registered in more than one registry.")

    if registry_handler_for_pool != registery_handlers[handler_id]:
        warnings.warn(
            "Pool already registred in another registry. "
            f"Pool: {pool}, "
            f"registry handler for pool: {registry_handler_for_pool}, "
            f"registry handler in metaregistry: {registery_handlers[handler_id]}"
        )
        return True

    return False
