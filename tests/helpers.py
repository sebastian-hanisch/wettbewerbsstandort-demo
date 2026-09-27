"""Gemeinsame Hilfen der Tests: kleine Netze von Hand und unabhängige Reimplementierungen (reines Python) zum Gegenprüfen der Aufzählungen."""

from itertools import combinations

import cmp_scenario as sc


def line(xs, w=None):
    """Netz von Knoten auf einer Linie (y = 0) an den Stellen `xs` mit Nachfrage `w` (Standard 1)."""
    w = w or [1] * len(xs)
    return sc._build("hand", [(x, 0) for x in xs], w)


def tiny(seed, n=8, kind="uniform"):
    return sc.generate(n, kind, seed)


def slow_gain(net, opp, mine):
    """Halbeinheiten, die `mine` gegen `opp` erobert (reines Python, unabhängig von numpy)."""
    total = 0
    for j in range(net.n):
        do = min(net.d[i][j] for i in opp)
        dm = min(net.d[i][j] for i in mine)
        total += net.w[j] * (2 if dm < do else 1 if dm == do else 0)
    return total


def slow_best_reply(net, opp, k):
    best, best_set = -1, None
    for cand in combinations(range(net.n), k):
        if set(cand) & set(opp):
            continue
        g = slow_gain(net, opp, cand)
        if g > best:
            best, best_set = g, cand
    return best, best_set


def slow_leader(net, p, r):
    """Optimaler Führer (max-min) mit zwei geschachtelten Aufzählungen: (Halbeinheiten des Führers, kleinste optimale Menge)."""
    best, best_set = -1, None
    for lead in combinations(range(net.n), p):
        v = 2 * sum(net.w) - slow_best_reply(net, lead, r)[0]
        if v > best:
            best, best_set = v, lead
    return best, best_set


def slow_nash(net, k):
    """Alle reinen Gleichgewichte (a < b) durch Nachrechnen der Bestantwort-Bedingung."""
    sets = list(combinations(range(net.n), k))
    br = {a: slow_best_reply(net, a, k)[0] for a in sets}
    out = []
    for a in sets:
        for b in sets:
            if a < b and not set(a) & set(b) and slow_gain(net, a, b) == br[a] and slow_gain(net, b, a) == br[b]:
                out.append((a, b))
    return out
