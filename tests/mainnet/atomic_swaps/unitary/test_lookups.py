import pytest
from brownie import ZERO_ADDRESS


def test_synth_pool_fails_before_adding(atomic_swap, sUSD):
    assert atomic_swap.synth_pool(sUSD) == ZERO_ADDRESS


# Adding atomic swaps module scoped 
def test_synth_pool_succeeds_after_adding(atomic_swap, add_atomic_swap_synths, sUSD):
    assert atomic_swap.synth_pool(sUSD) != ZERO_ADDRESS


def test_synth_pool_returns_zero_addr_on_non_synth(atomic_swap, USDT):
    assert atomic_swap.synth_pool(USDT) == ZERO_ADDRESS


def test_swappable_synth_nonzero_on_synth(atomic_swap, sUSD):
    assert atomic_swap.swappable_synth(sUSD) != ZERO_ADDRESS


def test_swappable_synth_matches(atomic_swap, sUSD, USDT):
    susd_synth = atomic_swap.swappable_synth(sUSD)
    usdt_synth = atomic_swap.swappable_synth(USDT)
    assert susd_synth == usdt_synth
    

