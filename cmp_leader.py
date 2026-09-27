"""Führer-Verfahren: der Führer, der den Wettbewerb ignoriert (p-Median), Greedy und Swap-Lokalsuche gegen die exakte Antwort des Folgers, und das exakte Führer-Optimum durch Aufzählung.

Bewertet wird immer, was der Führer NACH der besten Antwort des Folgers behält (Halbeinheiten, ganzzahlig). Gleichstände werden lexikografisch (kleinste Menge, kleinster Index) entschieden.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LeaderResult:
    sites: tuple
    value: int           # Halbeinheiten, die der Führer nach der Antwort behält
    reply: tuple         # Antwort des Folgers
    evals: int = 0       # bewertete Führermengen (Bestantworten)
    moves: tuple = ()    # Züge der Lokalsuche: (entfernt, hinzugefügt, Wert danach)


def _result(game, sites, r, evals=0, moves=()):
    gain, reply = game.best_reply(sites, r)
    return LeaderResult(tuple(sorted(sites)), 2 * game.total - gain, reply, evals, tuple(moves))


def p_median(game, p):
    """Der Führer, der den Folger nicht bedenkt: p Standorte mit der kleinsten Summe nachfragegewichteter Abstände (exakte Aufzählung, Gleichstand: kleinste Menge)."""
    combos, fmin, _member = game.sets(p)
    cost = fmin @ game.w
    return tuple(int(x) for x in combos[int(np.argmin(cost))])


def naive(game, p, r):
    """p-Median-Führer, bewertet gegen die exakte Antwort."""
    return _result(game, p_median(game, p), r)


def exact(game, p, r):
    """Optimaler Führer (max-min): alle p-Mengen aufzählen. Gibt (Ergebnis, Werte aller Mengen in lexikografischer Reihenfolge) zurück; Gleichstand: kleinste Menge."""
    combos = game.sets(p)[0]
    values = np.array([game.leader_value(tuple(int(x) for x in c), r) for c in combos], dtype=np.int64)
    i = int(np.argmax(values))
    return _result(game, tuple(int(x) for x in combos[i]), r, evals=len(combos)), values


def greedy(game, p, r):
    """Standort für Standort: der nächste Standort ist der, der den Anteil gegen die exakte Antwort des Folgers (mit r Standorten) am größten macht; Gleichstand: kleinster Index."""
    sites = ()
    evals = 0
    for _ in range(p):
        best, best_i = None, None
        for i in range(game.n):
            if i in sites:
                continue
            v = game.leader_value(tuple(sorted(sites + (i,))), r)
            evals += 1
            if best is None or v > best:
                best, best_i = v, i
        sites = tuple(sorted(sites + (best_i,)))
    return _result(game, sites, r, evals)


def swap(game, p, r, start=None):
    """Swap-Lokalsuche ab `start` (Standard: Greedy): einen Führerstandort gegen einen anderen Knoten tauschen, solange der Wert steigt (erste Verbesserung in fester Reihenfolge)."""
    cur = greedy(game, p, r) if start is None else _result(game, start, r)
    sites, value, evals, moves = cur.sites, cur.value, cur.evals, []
    memo = {sites: value}

    def val(s):
        nonlocal evals
        if s not in memo:
            memo[s] = game.leader_value(s, r)
            evals += 1
        return memo[s]

    improved = True
    while improved:
        improved = False
        for a in sites:
            for b in range(game.n):
                if b in sites:
                    continue
                cand = tuple(sorted((set(sites) - {a}) | {b}))
                v = val(cand)
                if v > value:
                    sites, value, improved = cand, v, True
                    moves.append((a, b, v))
                    break
            if improved:
                break
    return _result(game, sites, r, evals, moves)
