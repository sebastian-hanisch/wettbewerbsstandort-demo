"""Orakel-Test: Führer-Optimum, Bestantwort, Greedy, Swap, reine Gleichgewichte und abwechselnde Bestantworten gegen Aufzählung in Brüchen (Fraction), mit doppelten Positionen (Gleichstände)."""

import random
from fractions import Fraction as Fr
from itertools import combinations

import pytest

import cmp_equilibrium as eq
import cmp_game as gm
import cmp_leader as ld
import cmp_scenario as sc


def _net(seed, n):
    rng = random.Random(seed)
    grid = rng.choice([3, 8, 99])                               # kleine Gitter: doppelte Positionen und Gleichstände
    return sc._build("uniform", [(rng.randint(0, grid), rng.randint(0, grid)) for _ in range(n)], [rng.randint(1, 9) for _ in range(n)])


def _share(net, a, b):
    """Anteil von a gegen b als Bruch: Sieg ganz, Gleichstand halb."""
    s = Fr(0)
    for j in range(net.n):
        da, db = min(net.d[i][j] for i in a), min(net.d[i][j] for i in b)
        s += net.w[j] if da < db else Fr(net.w[j], 2) if da == db else 0
    return s


def _reply(net, a, r):
    best = None
    for f in combinations(range(net.n), r):
        if set(f) & set(a):
            continue
        g = net.total - _share(net, a, f)
        if best is None or g > best[0]:
            best = (g, f)
    return best


def _value(net, a, r):
    return net.total - _reply(net, a, r)[0]


@pytest.mark.parametrize("seed", range(10))
def test_leader_methods_equal_fraction_enumeration(seed):
    net = _net(seed, 7)
    g = gm.Game(net)
    for p, r in ((1, 1), (2, 1), (2, 2), (1, 3)):
        vals = [_value(net, a, r) for a in combinations(range(net.n), p)]
        best, vec = ld.exact(g, p, r)
        assert [Fr(int(x), 2) for x in vec] == vals and Fr(best.value, 2) == max(vals)
        assert best.sites == list(combinations(range(net.n), p))[vals.index(max(vals))]
        sites = []
        for _ in range(p):
            cand = [(_value(net, tuple(sorted(sites + [i])), r), i) for i in range(net.n) if i not in sites]
            sites = sorted(sites + [max(cand, key=lambda t: (t[0], -t[1]))[1]])
        gr = ld.greedy(g, p, r)
        assert gr.sites == tuple(sites)
        cur, cv, moves = tuple(sites), _value(net, tuple(sites), r), 0
        while True:
            step = next(((tuple(sorted((set(cur) - {a}) | {b})), v) for a in cur for b in range(net.n) if b not in cur
                         for v in [_value(net, tuple(sorted((set(cur) - {a}) | {b})), r)] if v > cv), None)
            if step is None:
                break
            (cur, cv), moves = step, moves + 1
        sw = ld.swap(g, p, r, start=gr.sites)
        assert (sw.sites, Fr(sw.value, 2), len(sw.moves)) == (cur, cv, moves)


@pytest.mark.parametrize("seed", range(10))
def test_nash_pairs_and_dynamics_equal_enumeration(seed):
    net = _net(seed, 7)
    g = gm.Game(net)
    for k in (1, 2):
        sets = list(combinations(range(net.n), k))
        pairs = []
        for a in sets:
            for b in sets:
                if a < b and not set(a) & set(b) and net.total - _share(net, a, b) == _reply(net, a, k)[0] and _share(net, a, b) == _reply(net, b, k)[0]:
                    pairs.append((a, b, 2 * _share(net, a, b)))
        assert sorted((a, b, Fr(s)) for a, b, s in eq.nash_pairs(g, k)) == sorted(pairs)
        start = ld.p_median(g, k)
        pos, mover, seen = [start, None], 1, set()
        trace, outcome = [(0, start)], "offen"
        for _ in range(40):
            gains = {f: net.total - _share(net, pos[1 - mover], f) for f in sets if not set(f) & set(pos[1 - mover])}
            top = max(gains.values())
            if pos[mover] is not None and gains.get(pos[mover], -1) == top:
                outcome = "Gleichgewicht"
                break
            pos[mover] = min(f for f, v in gains.items() if v == top)
            trace.append((mover, pos[mover]))
            if (mover, tuple(pos)) in seen:
                outcome = "Zyklus"
                break
            seen.add((mover, tuple(pos)))
            mover = 1 - mover
        got, out = eq.dynamics(g, start, k)
        assert out == outcome and [(m, s) for m, s, _ in got] == trace
