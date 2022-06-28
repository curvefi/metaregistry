import brownie
from brownie import ZERO_ADDRESS


def test_find_best_pool_for_coins_returns_addr(atomic_swap, sUSD, USDT):
    dx = 1000 * 10 ** sUSD.decimals()
    returned_pool = atomic_swap.find_best_pool_for_coins(sUSD, USDT, dx)
    assert returned_pool != ZERO_ADDRESS


def test_registry_swap_dx_returns_nonzero_value(atomic_swap, sUSD, USDT):
    dx = 1000 * 10 ** sUSD.decimals()
    pool = atomic_swap.find_best_pool_for_coins(sUSD, USDT, dx)
    assert atomic_swap.get_registry_swap_amount(pool, sUSD, USDT, dx) > 0


def test_atomic_swap_amount_reverts_on_no_path(atomic_swap, sUSD, USDT):
    dx = 1000 * 10 ** sUSD.decimals()
    with brownie.reverts():
        atomic_swap.get_atomic_swap_amount(sUSD, USDT, dx)


def test_estimated_matches_registry_amount(atomic_swap, sUSD, USDT):
    dx = 1000 * 10 ** sUSD.decimals()
    dy_est = atomic_swap.get_estimated_swap_amount(sUSD, USDT, dx)
    pool = atomic_swap.find_best_pool_for_coins(sUSD, USDT, dx)
    dy_reg = atomic_swap.get_registry_swap_amount(pool, sUSD, USDT, dx)
    assert dy_est == dy_reg


def test_execute_registry_swap_reverts_without_approval(atomic_swap, sUSD, USDT, alice):
    dx = 1000 * 10 ** sUSD.decimals()
    sUSD._mint_for_testing(alice, dx)
    with brownie.reverts():
        atomic_swap.exchange(sUSD, USDT, dx, 0, alice)


def test_execute_registry_swap(atomic_swap, sUSD, USDT, alice):
    dx = 1000 * 10 ** sUSD.decimals()
    sUSD._mint_for_testing(alice, dx)
    sUSD.approve(atomic_swap, sUSD.balanceOf(alice), {"from": alice})

    assert USDT.balanceOf(alice) == 0
    atomic_swap.exchange(sUSD, USDT, dx, 0, alice)
    assert USDT.balanceOf(alice) > 0
