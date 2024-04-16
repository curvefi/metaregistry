import boa
from rich import Console as RichConsole

from scripts.deployment_utils import setup_environment
from scripts.utils.constants import BASE_POOLS

def main():
    """
    Deploy the contracts to the network.
    It does the following:
    1. deploys the base pool registry
    2. deploys the crypto registry
    3. deploys the stable registry handler
    4. deploys the stable factory handler
    5. deploys the crypto registry handler
    6. deploys the crypto factory handler
    7. deploys the metaregistry
    """
    console = RichConsole()
    setup_environment(console)
    
    # deploy basepool registry:
    base_pool_registry = boa.load(
        "contracts/mainnet/registries/BasePoolRegistryNG.vy",
        '0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf',  # stableswap factory ng
    )
    
    for _, data in BASE_POOLS.items():

        base_pool_registry.add_custom_base_pool(
            data["pool"],
            data["lp_token"],
            data["num_coins"],
            data["is_legacy"],
            data["is_lending"],
            data["is_v2"],
        )

        console.log(f"Added base pool [blue]{data['pool']} to base pool registry.")

    breakpoint()
    
    
if __name__ == "__main__":
    main()
