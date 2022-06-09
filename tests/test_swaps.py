import itertools
import brownie

from .utils import ETH


def test_get_estimated_swap_amount(
    atomic_swap,
    add_atomic_swap_synths,
    sUSD,
    sETH,
    metaregistry,
    DAI,
    WBTC,
    sEUR,
    sBTC,
    USDT,
):

    amounts = {
        DAI: 10**18,
        ETH: 10**18,
        WBTC: 10**8,
        USDT: 10**6,
        sUSD: 10**18,
        sETH: 10**18,
        sEUR: 10**18,
        sBTC: 10**18,
    }

    combinations = itertools.combinations([DAI, ETH, WBTC, USDT, sUSD, sETH, sEUR, sBTC], 2)
    # registry swap estimate:
    for coins in combinations:
        amount_in = amounts[coins[0]]
        _expected = atomic_swap.get_estimated_swap_amount(*coins, amount_in)
        print(f"Expected out for 10**18 between {coins}: {_expected}")
        assert _expected > 0
