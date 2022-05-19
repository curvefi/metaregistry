from ..utils import deploy_stable_factory_pool
from ..utils.constants import METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX, agEUR, sEUR


def test_add_deployed_pool_to_metaregistry(
    fn_isolation,
    metaregistry_mock,
    sync_stable_factory_registry,
    two_coin_plain_pool_implementation,
    stable_factory_handler,
    stable_factory,
    owner,
):

    euro_pool = deploy_stable_factory_pool(
        stable_factory, two_coin_plain_pool_implementation, sEUR, agEUR, owner
    )
    total_pools = stable_factory.pool_count()
    metaregistry_mock.sync_registry(
        METAREGISTRY_STABLE_FACTORY_HANDLER_INDEX, total_pools, {"from": owner}
    )
    assert metaregistry_mock.is_registered(euro_pool)
