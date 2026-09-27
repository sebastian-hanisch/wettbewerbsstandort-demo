"""Gleichgewichte: reine Nash-Paare (beide Spieler antworten optimal aufeinander) und die Dynamik abwechselnder Bestantworten.

Für die Spieler mit gleich vielen Standorten (p = r) wird die Matrix G[a][b] = Halbeinheiten aufgezählt, die die Menge b gegen die Menge a erobert (-1 bei Überschneidung). Ein Paar (a, b) ist ein reines Gleichgewicht,
wenn b eine Bestantwort auf a und a eine Bestantwort auf b ist (auch bei mehreren gleich guten Antworten). Die Dynamik nimmt bei Gleichstand die lexikografisch kleinste Antwort.
"""

import numpy as np


def payoff_matrix(game, k):
    """G[a][b] (a, b: Indizes der k-Mengen in lexikografischer Reihenfolge): Halbeinheiten, die b gegen a erobert (-1: überschneiden sich)."""
    combos = game.sets(k)[0]
    return np.array([game.gain_vector(tuple(int(x) for x in c), k) for c in combos], dtype=np.int64)


def nash_pairs(game, k):
    """Alle reinen Gleichgewichte für zwei Spieler mit je k Standorten: Liste (a, b, Anteil von a in Halbeinheiten) mit a < b (lexikografisch)."""
    combos = game.sets(k)[0]
    g = payoff_matrix(game, k)
    best = g.max(axis=1)
    is_reply = (g == best[:, None]) & (g >= 0)                # is_reply[a][b]: b ist Bestantwort auf a
    eq = is_reply & is_reply.T
    out = []
    for a, b in zip(*np.nonzero(np.triu(eq, 1))):
        out.append((tuple(int(x) for x in combos[a]), tuple(int(x) for x in combos[b]), 2 * game.total - int(g[a][b])))
    return out


def dynamics(game, start, k, max_rounds=40):
    """Abwechselnde Bestantworten: Spieler 0 steht bei `start`, Spieler 1 antwortet, dann Spieler 0 auf ihn usw. (beide mit k Standorten). Wer schon eine Bestantwort hält, bleibt stehen (bei mehreren
    gleich guten Antworten wechselt er nicht: sonst würden Gleichstände Zyklen vortäuschen); sonst wechselt er zur lexikografisch kleinsten Bestantwort.
    Gibt (Verlauf, Ausgang): Verlauf = [(Spieler, Standorte, Anteil des Spielers in Halbeinheiten nach seinem Zug oder None beim Start)];
    Ausgang = 'Gleichgewicht' (ein Spieler bleibt stehen: beide antworten optimal aufeinander), 'Zyklus' (ein Zustand kehrt wieder) oder 'offen' (max_rounds erreicht)."""
    pos = [tuple(start), None]
    trace = [(0, pos[0], None)]
    seen = set()
    mover = 1
    for _ in range(max_rounds):
        gain_vec = game.gain_vector(pos[1 - mover], k)
        combos = game.sets(k)[0]
        best = int(gain_vec.max())
        if pos[mover] is not None:
            idx = int(np.nonzero((combos == np.array(pos[mover])).all(axis=1))[0][0])
            if int(gain_vec[idx]) == best:
                return trace, "Gleichgewicht"
        reply = tuple(int(x) for x in combos[int(np.argmax(gain_vec))])
        pos[mover] = reply
        trace.append((mover, reply, best))
        state = (mover, tuple(pos))
        if state in seen:
            return trace, "Zyklus"
        seen.add(state)
        mover = 1 - mover
    return trace, "offen"
