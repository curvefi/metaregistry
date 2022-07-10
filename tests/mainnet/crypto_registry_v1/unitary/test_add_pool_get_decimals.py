import brownie


def test_get_decimals(crypto_registry_v1, mock_cryptoeth_pool, mock_cryptoeth_lp_token, owner):

    crypto_registry_v1.add_pool(
        mock_cryptoeth_pool,  # _pool
        mock_cryptoeth_lp_token,  # _lp_token
        brownie.ZERO_ADDRESS,  # _gauge
        brownie.ZERO_ADDRESS,  # _zap
        "Mock CryptoETH Pool",  # _name
        brownie.ZERO_ADDRESS,  # _base_pool
        0,  # _has_positive_rebasing_tokens
    )


def test_get_decimals_metapool(owner):

    pass


def test_revert_get_decimals(owner):

    pass
