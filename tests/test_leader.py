"""Führer-Verfahren: das exakte Optimum gegen zwei geschachtelte Aufzählungen in reinem Python, Greedy und Swap nie besser als das Optimum, p-Median gegen Brute Force."""

from itertools import combinations

import pytest

import cmp_game as gm
import cmp_leader as ld
from helpers import line, slow_leader, tiny


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("p, r", [(1, 1), (2, 1), (1, 2), (2, 2)])
def test_exact_leader_equals_nested_plain_enumeration(seed, p, r):
    net = tiny(seed, n=8)
    g = gm.Game(net)
    res, values = ld.exact(g, p, r)
    best, best_set = slow_leader(net, p, r)
    assert res.value == best and res.sites == best_set and values.max() == best and len(values) == len(list(combinations(range(8), p)))


@pytest.mark.parametrize("seed", range(6))
def test_heuristics_never_beat_the_optimum_and_swap_never_loses_to_greedy(seed):
    g = gm.Game(tiny(seed, n=10))
    for p, r in ((2, 2), (3, 2), (2, 3)):
        best, _ = ld.exact(g, p, r)
        gre = ld.greedy(g, p, r)
        swp = ld.swap(g, p, r, start=gre.sites)
        assert swp.value >= gre.value and best.value >= swp.value and len(gre.sites) == len(swp.sites) == p
        assert [m[2] for m in swp.moves] == sorted(m[2] for m in swp.moves) and all(v > gre.value for _a, _b, v in swp.moves)


@pytest.mark.parametrize("seed", range(6))
def test_p_median_is_the_brute_force_minimum_of_the_weighted_distance_sum(seed):
    net = tiny(seed, n=9)
    g = gm.Game(net)
    for p in (1, 2, 3):
        cost = lambda s: sum(net.w[j] * min(net.d[i][j] for i in s) for j in range(net.n))
        best = min(combinations(range(net.n), p), key=lambda s: (cost(s), s))
        assert ld.p_median(g, p) == best


def test_naive_is_evaluated_against_the_exact_reply_and_can_lose_to_the_optimum():
    g = gm.Game(tiny(6, n=14))
    naive, exact = ld.naive(g, 2, 2), ld.exact(g, 2, 2)[0]
    assert naive.sites == ld.p_median(g, 2) and naive.value == 2 * g.total - g.best_reply(naive.sites, 2)[0] and naive.value < exact.value


def test_hotelling_median_wins_on_an_odd_street_with_one_site_each():
    g = gm.Game(line([0, 10, 20, 30, 40, 50, 60]))
    best, _ = ld.exact(g, 1, 1)
    assert best.sites == (3,) and g.pct(best.value) == pytest.approx(4 / 7 * 100) and ld.naive(g, 1, 1).sites == (3,)


def test_swap_from_a_given_start_never_ends_worse_than_the_start():
    g = gm.Game(tiny(2, n=12))
    start = (0, 1)
    res = ld.swap(g, 2, 2, start=start)
    assert res.value >= g.leader_value(start, 2)
