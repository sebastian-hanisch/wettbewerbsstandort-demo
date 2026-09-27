"""Das Spiel: Anteile, exakte Bestantwort und die Aufzählungen, auf denen alles Weitere beruht.

Ein Spieler mit den Standorten `a` und ein Gegner mit `b` (verschiedene Knoten): jeder Kunde j geht zum näheren; der Anteil des Gegners heißt gain. In **Halbeinheiten**: ein Sieg zählt das Doppelte der Nachfrage,
ein Gleichstand einfach - zusammen 2 * W je Spielpaar. Alle Größen sind ganze Zahlen; die Bestantwort nimmt bei Gleichstand die lexikografisch kleinste Menge.
"""

from itertools import combinations

import numpy as np


class Game:
    """Alle Mengen der Größe k werden bei Bedarf einmal aufgezählt: `Fmin[k]` (K x n) hält je Menge den kleinsten Abstand jedes Knotens zu ihr, `member[k]` (K x n) die Zugehörigkeit."""

    def __init__(self, net):
        self.net = net
        self.n = net.n
        self.D = np.array(net.d, dtype=np.int64)
        self.w = np.array(net.w, dtype=np.int64)
        self.total = int(self.w.sum())          # W; ganze Größe = 2 * W Halbeinheiten
        self._sets = {}

    def sets(self, k):
        """(Mengen (K x k), kleinste Abstände (K x n), Zugehörigkeit (K x n)) aller k-Teilmengen in lexikografischer Reihenfolge."""
        if k not in self._sets:
            combos = np.array(list(combinations(range(self.n), k)), dtype=np.int64)
            fmin = self.D[combos].min(axis=1)
            member = np.zeros((len(combos), self.n), dtype=bool)
            member[np.arange(len(combos))[:, None], combos] = True
            self._sets[k] = (combos, fmin, member)
        return self._sets[k]

    def dist_to(self, sites):
        """Kleinster Abstand jedes Knotens zu den Standorten."""
        return self.D[list(sites)].min(axis=0)

    def gain_vector(self, opp, k):
        """Halbeinheiten, die jede k-Menge gegen die Standorte `opp` erobert; Mengen, die einen Knoten von `opp` besetzen, bekommen -1 (nicht zulässig)."""
        combos, fmin, member = self.sets(k)
        dl = self.dist_to(opp)
        gain = ((fmin < dl) * 2 + (fmin == dl)) @ self.w
        return np.where(member[:, list(opp)].any(axis=1), -1, gain)

    def best_reply(self, opp, k):
        """Exakte Bestantwort mit k Standorten auf `opp`: (Halbeinheiten, Standorte). Gleichstand: kleinste lexikografische Menge."""
        gain = self.gain_vector(opp, k)
        i = int(np.argmax(gain))
        return int(gain[i]), tuple(int(x) for x in self.sets(k)[0][i])

    def split(self, a, b):
        """Halbeinheiten von `a` und von `b` gegeneinander (verschiedene Knoten): (a, b); zusammen 2 * W."""
        da, db = self.dist_to(a), self.dist_to(b)
        gb = int(((db < da) * 2 + (db == da)) @ self.w)
        return 2 * self.total - gb, gb

    def owner(self, a, b):
        """Je Knoten: 0 = geht zu `a`, 1 = zu `b`, 2 = Gleichstand (geteilt)."""
        da, db = self.dist_to(a), self.dist_to(b)
        return np.where(da < db, 0, np.where(db < da, 1, 2))

    def leader_value(self, leader, r):
        """Halbeinheiten, die der Führer behält, wenn der Folger mit r Standorten exakt antwortet."""
        return 2 * self.total - self.best_reply(leader, r)[0]

    def pct(self, half):
        """Halbeinheiten in Prozent der gesamten Nachfrage."""
        return 100 * half / (2 * self.total)
