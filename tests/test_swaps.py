import itertools

from .utils import WETH, ETH


def test_synth_swap_through(WBTC, USDT, atomic_swap, add_atomic_swap_synths, metaregistry):
    """test swap through synthswap
    note: if link:coin pair exists in registry, then this test will just go to the registry swap
    instead of synth swap.
    """
    amount_in = 10**18
    _expected = atomic_swap.get_atomic_swap_amount(WBTC, ETH, amount_in)
    print(f"Expected out for between {WBTC} > {WETH} -> in: {amount_in}, out: {_expected} \n")
    assert _expected > 0

    _expected = atomic_swap.get_atomic_swap_amount(WBTC, USDT, amount_in)
    print(f"Expected out for between {WBTC} > {USDT} -> in: {amount_in}, out: {_expected} \n")
    assert _expected > 0


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
        print(f"Expected out for between {coins} -> in: {amount_in}, out: {_expected} \n")
        assert _expected > 0
