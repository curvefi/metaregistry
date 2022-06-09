import brownie


def test_add_synth(alice, atomic_swap, sUSD, curve_susd):
    atomic_swap.add_synth(sUSD, curve_susd, {"from": alice})

    assert atomic_swap.synth_pool(sUSD) == curve_susd
    for coin in [curve_susd.coins(i) for i in range(4)]:
        assert atomic_swap.swappable_synth(coin) == sUSD


def test_already_added(alice, atomic_swap, sUSD, curve_susd):
    atomic_swap.add_synth(sUSD, curve_susd, {"from": alice})

    with brownie.reverts("dev: already added"):
        atomic_swap.add_synth(sUSD, curve_susd, {"from": alice})


def test_wrong_pool(alice, atomic_swap, sUSD, curve_sbtc):
    with brownie.reverts("dev: synth not in pool"):
        atomic_swap.add_synth(sUSD, curve_sbtc, {"from": alice})


def test_not_a_synth(alice, atomic_swap, curve_susd):
    dai = curve_susd.coins(0)
    with brownie.reverts():
        atomic_swap.add_synth(dai, curve_susd, {"from": alice})
