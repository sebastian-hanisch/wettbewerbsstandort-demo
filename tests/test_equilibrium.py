"""Gleichgewichte: reine Nash-Paare gegen eine unabhängige Prüfung in reinem Python, Dynamik (Gleichgewicht, Zyklus), Straße."""

import pytest

import cmp_equilibrium as eq
import cmp_game as gm
import cmp_leader as ld
import cmp_scenario as sc
from helpers import line, slow_nash, tiny


@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("k", [1, 2])
def test_nash_pairs_equal_the_plain_python_check(seed, k):
    net = tiny(seed, n=8)
    g = gm.Game(net)
    assert [(a, b) for a, b, _ in eq.nash_pairs(g, k)] == slow_nash(net, k)


def test_nash_share_is_the_first_players_share_in_half_units():
    net = tiny(1, n=9)
    g = gm.Game(net)
    for a, b, half in eq.nash_pairs(g, 1) + eq.nash_pairs(g, 2):
        assert half == g.split(a, b)[0]


def test_on_an_odd_street_with_one_site_each_the_equilibrium_sits_at_the_middle():
    g = gm.Game(line([0, 10, 20, 30, 40, 50, 60]))
    pairs = eq.nash_pairs(g, 1)
    assert [(a, b) for a, b, _ in pairs] == [((2,), (3,)), ((3,), (4,))]


@pytest.mark.parametrize("seed", range(10))
def test_a_dynamics_that_ends_in_equilibrium_ends_in_a_nash_pair(seed):
    g = gm.Game(tiny(seed, n=10))
    for k in (1, 2):
        trace, outcome = eq.dynamics(g, ld.p_median(g, k), k)
        if outcome == "Gleichgewicht":
            final = [None, None]
            for who, sites, _gain in trace:
                final[who] = sites
            a, b = sorted((final[0], final[1]))
            assert (a, b) in [(x, y) for x, y, _ in eq.nash_pairs(g, k)]


def test_dynamics_reports_a_cycle_when_no_equilibrium_exists():
    g = gm.Game(sc.generate(14, "uniform", 1))
    assert eq.nash_pairs(g, 2) == []
    trace, outcome = eq.dynamics(g, ld.p_median(g, 2), 2)
    assert outcome == "Zyklus" and len(trace) > 2 and trace[0][0] == 0 and trace[0][2] is None and [t[0] for t in trace[1:3]] == [1, 0]


def test_dynamics_on_a_street_from_the_median_settles_at_once():
    g = gm.Game(sc.generate(9, "street", 1))
    trace, outcome = eq.dynamics(g, ld.p_median(g, 1), 1)
    assert outcome == "Gleichgewicht" and len(trace) == 2


def test_a_street_always_has_a_pure_equilibrium_for_small_p():
    for n in (8, 9, 11, 14, 15):
        g = gm.Game(sc.generate(n, "street", 1))
        for k in (1, 2, 3):
            assert eq.nash_pairs(g, k), (n, k)


def test_payoff_matrix_marks_overlapping_pairs():
    g = gm.Game(tiny(3, n=7))
    m = eq.payoff_matrix(g, 2)
    combos = g.sets(2)[0]
    assert m.shape == (len(combos), len(combos)) and all((m[a][b] == -1) == bool(set(combos[a]) & set(combos[b])) for a in range(len(combos)) for b in range(len(combos)))
