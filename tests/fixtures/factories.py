import boa
import pytest

# ---- Stableswap NG ---- #


@pytest.fixture()
def stableswap_ng_deployer():
    return boa.load_partial("contracts/amms/stableswapng/CurveStableSwapNG.vy")


@pytest.fixture()
def stableswap_ng_meta_deployer():
    return boa.load_partial(
        "contracts/amms/stableswapng/CurveStableSwapMetaNG.vy"
    )


@pytest.fixture()
def stableswap_ng_implementation(stableswap_ng_deployer, deployer):
    with boa.env.prank(deployer):
        return stableswap_ng_deployer.deploy_as_blueprint()


@pytest.fixture()
def stableswap_ng_meta_implementation(stableswap_ng_meta_deployer, deployer):
    with boa.env.prank(deployer):
        return stableswap_ng_meta_deployer.deploy_as_blueprint()


@pytest.fixture()
def stableswap_ng_views_implementation(deployer):
    with boa.env.prank(deployer):
        return boa.load_partial(
            "contracts/amms/stableswapng/CurveStableSwapNGViews.vy"
        ).deploy()


@pytest.fixture()
def stableswap_ng_math_implementation(deployer):
    with boa.env.prank(deployer):
        return boa.load_partial(
            "contracts/amms/stableswapng/CurveStableSwapNGMath.vy"
        ).deploy()


@pytest.fixture()
def stableswap_ng_factory_empty(
    deployer,
    ng_fee_receiver,
    ng_owner,
    stableswap_ng_views_implementation,
    stableswap_ng_math_implementation,
    stableswap_ng_implementation,
    stableswap_ng_meta_implementation,
):
    with boa.env.prank(deployer):
        factory = boa.load_partial(
            "contracts/amms/stableswapng/CurveStableSwapFactoryNG.vy"
        ).deploy(ng_fee_receiver, ng_owner)

    with boa.env.prank(ng_owner):
        factory.set_views_implementation(
            stableswap_ng_views_implementation.address
        )
        factory.set_math_implementation(
            stableswap_ng_math_implementation.address
        )
        factory.set_pool_implementations(
            0, stableswap_ng_implementation.address
        )
        factory.set_metapool_implementations(
            0, stableswap_ng_meta_implementation.address
        )

    return factory


@pytest.fixture()
def stableswap_ng_factory(
    stableswap_ng_factory_empty, stableswap_ng_pool, base_pool_coins, ng_owner
):
    stableswap_ng_factory_empty.add_base_pool(
        stableswap_ng_pool.address,
        stableswap_ng_pool.address,
        [0] * len(base_pool_coins),
        len(base_pool_coins),
        sender=ng_owner,
    )
    return stableswap_ng_factory_empty


# ---- Twocrypto NG ---- #


@pytest.fixture(scope="module")
def twocrypto_ng_math_contract(deployer):
    with boa.env.prank(deployer):
        return boa.load(
            "contracts/amms/twocryptong/CurveCryptoMathOptimized2.vy"
        )


@pytest.fixture(scope="module")
def twocrypto_ng_amm_deployer():
    return boa.load_partial(
        "contracts/amms/twocryptong/CurveTwocryptoOptimized.vy"
    )


@pytest.fixture(scope="module")
def twocrypto_ng_amm_implementation(deployer, twocrypto_ng_amm_deployer):
    with boa.env.prank(deployer):
        return twocrypto_ng_amm_deployer.deploy_as_blueprint()


@pytest.fixture(scope="module")
def twocrypto_ng_views_contract(deployer):
    with boa.env.prank(deployer):
        return boa.load(
            "contracts/amms/twocryptong/CurveCryptoViews2Optimized.vy"
        )


@pytest.fixture(scope="module")
def twocrypto_ng_factory(
    deployer,
    ng_fee_receiver,
    ng_owner,
    twocrypto_ng_amm_implementation,
    twocrypto_ng_math_contract,
    twocrypto_ng_views_contract,
):
    with boa.env.prank(deployer):
        factory = boa.load(
            "contracts/amms/twocryptong/CurveTwocryptoFactory.vy"
        )
        factory.initialise_ownership(ng_fee_receiver, ng_owner)

    with boa.env.prank(ng_owner):
        factory.set_pool_implementation(twocrypto_ng_amm_implementation, 0)
        factory.set_views_implementation(twocrypto_ng_views_contract)
        factory.set_math_implementation(twocrypto_ng_math_contract)

    return factory


# ---- Tricrypto NG ---- #


@pytest.fixture(scope="module")
def tricrypto_ng_math_contract(deployer):
    with boa.env.prank(deployer):
        return boa.load(
            "contracts/amms/tricryptong/CurveCryptoMathOptimized3.vy"
        )


@pytest.fixture(scope="module")
def tricrypto_ng_amm_deployer():
    return boa.load_partial(
        "contracts/amms/tricryptong/CurveTricryptoOptimized.vy"
    )


@pytest.fixture(scope="module")
def tricrypto_ng_amm_implementation(deployer, tricrypto_ng_amm_deployer):
    with boa.env.prank(deployer):
        return tricrypto_ng_amm_deployer.deploy_as_blueprint()


@pytest.fixture(scope="module")
def tricrypto_ng_views_contract(deployer):
    with boa.env.prank(deployer):
        return boa.load(
            "contracts/amms/tricryptong/CurveCryptoViews3Optimized.vy"
        )


@pytest.fixture(scope="module")
def tricrypto_ng_factory(
    deployer,
    ng_fee_receiver,
    ng_owner,
    tricrypto_ng_amm_implementation,
    tricrypto_ng_math_contract,
    tricrypto_ng_views_contract,
):
    with boa.env.prank(deployer):
        factory = boa.load(
            "contracts/amms/tricryptong/CurveTricryptoFactory.vy",
            ng_fee_receiver,
            ng_owner,
        )

    with boa.env.prank(ng_owner):
        factory.set_pool_implementation(tricrypto_ng_amm_implementation, 0)
        factory.set_views_implementation(tricrypto_ng_views_contract)
        factory.set_math_implementation(tricrypto_ng_math_contract)

    return factory
