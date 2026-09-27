"""Szenario: Standortwettbewerb (Führer und Folger). Ein Führer eröffnet p Standorte, danach antwortet ein Folger mit r Standorten; jeder Kunde geht zum näheren, bei Gleichstand teilen sie die Nachfrage.
Standorte und Kunden sind dieselben n Knoten einer Karte (jeder Knoten hat eine Nachfrage, an jedem Knoten kann ein Standort eröffnet werden).

Alles ist ganzzahlig und läuft über einen eigenen Zufallsgenerator (SplitMix64 auf Python-Ints, Kopie aus `ufl_scenario.py`) statt über `numpy.random`: numpy garantiert keine über Versionen stabilen
Zufallsströme, die CI installiert aber wöchentlich die neueste Version. Abstände sind ganzzahlig (Zehntel-Einheiten), Nachfragen ganzzahlig; Anteile werden in Halbeinheiten gezählt (Sieg = 2 mal Nachfrage, Gleichstand =
Nachfrage): alle Vergleiche sind exakt und auf Windows und Linux dieselben.
"""

from dataclasses import dataclass
from math import isqrt

_MASK = (1 << 64) - 1
MAP_W = 100
CLUSTERS = 4
CLUSTER_SPREAD = 15      # Punkte eines Clusters liegen im Quadrat +- CLUSTER_SPREAD um den Clustermittelpunkt
W_MIN, W_MAX = 1, 9      # Nachfrage je Knoten
STREET_W = 5             # Nachfrage je Knoten der Straße (alle gleich: klassisches Hotelling-Beispiel)


class SplitMix64:
    """Kleiner, gut gemischter 64-Bit-Zufallsgenerator (Vigna); reine Ganzzahl-Arithmetik."""

    def __init__(self, seed):
        self.state = seed & _MASK

    def next(self):
        self.state = (self.state + 0x9E3779B97F4A7C15) & _MASK
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
        return z ^ (z >> 31)

    def below(self, n):
        """Ganzzahl in 0..n-1 (die Modulo-Verzerrung bei n <= 101 liegt um 1e-17)."""
        return self.next() % n


def distance(a, b):
    """Euklidische Entfernung in Zehntel-Einheiten, ganzzahlig (abgerundet)."""
    return isqrt(100 * ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))


@dataclass(frozen=True)
class Net:
    kind: str            # "uniform", "cluster" oder "street"
    names: tuple
    pos: tuple           # ((x, y), ...)
    w: tuple             # Nachfrage je Knoten (ganzzahlig)
    d: tuple             # d[i][j] in Zehntel-Einheiten

    @property
    def n(self):
        return len(self.pos)

    @property
    def total(self):
        return sum(self.w)


def _build(kind, pos, w):
    n = len(pos)
    return Net(kind, tuple(f"Knoten {k + 1}" for k in range(n)), tuple(pos), tuple(w), tuple(tuple(distance(pos[i], pos[j]) for j in range(n)) for i in range(n)))


def generate(n, kind, seed):
    """`uniform`: gleichverteilt auf 0..99, Nachfrage 1..9; `cluster`: vier Cluster (Mittelpunkte gleichverteilt, Punkte in einem Quadrat um sie, auf die Karte begrenzt), Nachfrage 1..9;
    `street`: n Knoten im gleichen ganzzahligen Abstand auf einer Linie (y = 50), alle mit Nachfrage 5 - der Seed spielt keine Rolle."""
    if kind == "street":
        step = 90 // (n - 1)                       # ganzzahliger Knotenabstand: alle Nachbarabstände sind exakt gleich (viele echte Gleichstände)
        pos = [(5 + step * k, 50) for k in range(n)]
        return _build(kind, pos, [STREET_W] * n)
    rng = SplitMix64(seed)
    if kind == "uniform":
        pos = [(rng.below(MAP_W), rng.below(MAP_W)) for _ in range(n)]
    elif kind == "cluster":
        centers = [(rng.below(MAP_W), rng.below(MAP_W)) for _ in range(CLUSTERS)]
        pos = []
        for _ in range(n):
            cx, cy = centers[rng.below(CLUSTERS)]
            x = min(MAP_W - 1, max(0, cx + rng.below(2 * CLUSTER_SPREAD + 1) - CLUSTER_SPREAD))
            y = min(MAP_W - 1, max(0, cy + rng.below(2 * CLUSTER_SPREAD + 1) - CLUSTER_SPREAD))
            pos.append((x, y))
    else:
        raise KeyError(kind)
    w = [W_MIN + rng.below(W_MAX - W_MIN + 1) for _ in range(n)]
    return _build(kind, pos, w)
