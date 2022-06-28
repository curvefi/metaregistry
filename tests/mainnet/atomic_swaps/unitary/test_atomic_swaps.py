import brownie
from brownie import ZERO_ADDRESS

from tests.utils.constants import ETH, WETH


def test_nonregistry_path_returns_zero_before_adding_synth(atomic_swap, sUSD, sBTC):
    dx = 10 ** sUSD.decimals()
    dy_est = atomic_swap.get_estimated_swap_amount(sUSD, sBTC, dx)
    assert dy_est == 0


def test_synth_swap_through(WBTC, USDT, atomic_swap, add_atomic_swap_synths):
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


# Verify sUSD -> sBTC is not a registry path
def test_find_pool_returns_zero_addr_on_failed_path(atomic_swap, sUSD, sBTC):
    dx = 10000 * 10 ** sUSD.decimals()
    pool = atomic_swap.find_best_pool_for_coins(sUSD, sBTC, dx)
    assert pool == ZERO_ADDRESS


def test_nonregistry_path_returns_zero_swap_amount(atomic_swap, sUSD, sBTC):
    dx = 10 ** sUSD.decimals()
    dy_est = atomic_swap.get_estimated_swap_amount(sUSD, sBTC, dx)
    assert dy_est > 0


def test_nonregistry_path_returns_atomic_swap_amount(atomic_swap, sUSD, sBTC):
    dx = 10 ** sUSD.decimals()
    dy_est = atomic_swap.get_atomic_swap_amount(sUSD, sBTC, dx)
    assert dy_est > 0


def test_nonregistry_path_estimates_match(atomic_swap, sUSD, sBTC):
    dx = 10 ** sUSD.decimals()
    dy_registry_est = atomic_swap.get_estimated_swap_amount(sUSD, sBTC, dx)
    dy_atomic_est = atomic_swap.get_atomic_swap_amount(sUSD, sBTC, dx)
    assert dy_registry_est == dy_atomic_est


def test_nonregistry_path_exchange_fails(atomic_swap, sUSD, sBTC, alice):
    dx = 100_000 * 10 ** sUSD.decimals()

    sUSD._mint_for_testing(alice, dx)
    sUSD.approve(atomic_swap, sUSD.balanceOf(alice), {"from": alice})

    assert sBTC.balanceOf(alice) == 0
    with brownie.reverts(""):
        atomic_swap.exchange(sUSD, sBTC, dx, 0, alice, {"from": alice})


def test_synth_path_reverts_on_normal_exchange(atomic_swap, USDT, WBTC, alice):
    dx = 10 ** USDT.decimals()

    USDT._mint_for_testing(alice, dx)
    USDT.approve(atomic_swap, USDT.balanceOf(alice), {"from": alice})

    with brownie.reverts("Could not find swap"):
        atomic_swap.exchange(USDT, WBTC, dx, 0, alice, {"from": alice})


def test_exchange_through_synths_occurs(atomic_swap, USDT, WBTC, alice):
    dx = 20000 * 10 ** USDT.decimals()

    USDT._mint_for_testing(alice, dx)
    USDT.approve(atomic_swap, USDT.balanceOf(alice), {"from": alice})

    assert WBTC.balanceOf(alice) == 0
    atomic_swap.exchange_through_synth(USDT, WBTC, dx, 0, alice, {"from": alice})
    assert WBTC.balanceOf(alice) > 0
