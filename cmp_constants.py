"""Konstanten, Regler-Grenzen, Presets und feste Seed-Mengen der Demo "Standortwettbewerb: wer vorwegnimmt, gewinnt"."""

# --- Regler ---------------------------------------------------------------------------------------------------------------------
N_MIN, N_MAX, DEFAULT_N = 8, 24, 14
P_MIN, P_MAX, DEFAULT_P = 1, 3, 2
R_MIN, R_MAX, DEFAULT_R = 1, 3, 2
DEFAULT_SEED = 1
SEED_MAX = 2_000_000_000

NETS = {
    "uniform": "Zufallsnetz, gleichverteilt",
    "cluster": "Zufallsnetz mit vier Clustern",
    "street": "Straße (Knoten auf einer Linie, gleiche Nachfrage)",
}
DEFAULT_NET = "uniform"
FIXED_NETS = ("street",)          # Seed ohne Wirkung

# --- feste Seed-Mengen (unabhängig vom Nutzer-Seed) ---------------------------------------------------------------------------------
DIST_SEEDS = tuple(range(100000, 100100))
SWEEP_SEEDS = DIST_SEEDS[:40]
GRID_SEEDS = DIST_SEEDS[:20]
GRID_P = (1, 2, 3)
GRID_R = (1, 2, 3)

COLORS = {"leader": "#1f77b4", "follower": "#d62728", "tie": "#9467bd", "site_leader": "#08519c", "site_follower": "#a50f15", "line": "#b0b0b0"}

# --- Presets -----------------------------------------------------------------------------------------------------------------
_BASE = dict(net=DEFAULT_NET, n=DEFAULT_N, p=DEFAULT_P, r=DEFAULT_R, seed=DEFAULT_SEED)
PRESETS = {
    "🗺️ Standardnetz": {**_BASE},
    "🛣️ Die Mitte gewinnt": {**_BASE, "net": "street", "n": 9, "p": 1, "r": 1},
    "🙈 Ohne Vorwegnahme": {**_BASE, "seed": 24},
    "⚖️ Ein Gleichgewicht": {**_BASE, "seed": 14},
    "🏃 Folger stärker": {**_BASE, "p": 1},
    "👑 Führer stärker": {**_BASE, "r": 1},
    "🧲 Greedy versagt": {**_BASE, "net": "street", "p": 3, "r": 3},
    "🪤 Swap steckt fest": {**_BASE, "seed": 6},
}
# Jede Zahl in diesen Texten ist in tests/test_claims.py belegt.
PRESET_HELP = {
    "🗺️ Standardnetz": "14 Knoten, p = r = 2, Seed 1: der p-Median-Führer (Knoten 7 und 13) behält nach der besten Antwort 45,5 %, der optimale Führer (3 und 13) 54,5 %; Greedy und Swap finden das Optimum. Es gibt kein reines Gleichgewicht: abwechselnde Bestantworten laufen im Kreis (Wiederkehr nach 8 Zügen).",
    "🛣️ Die Mitte gewinnt": "Straße mit 9 Knoten, p = r = 1: der Führer in der Mitte (Knoten 5) behält 55,6 %, der Folger nimmt einen Nachbarn und bekommt 44,4 %. Es gibt zwei Gleichgewichte (die Mitte mit einem Nachbarn); die Bestantworten erreichen es nach einem Zug.",
    "🙈 Ohne Vorwegnahme": "Seed 24: der p-Median-Führer (Knoten 2 und 10) behält nur 39,7 %; der optimale Führer (9 und 10) behält 53,4 % - 13,7 Prozentpunkte mehr durch Vorwegnehmen der Antwort.",
    "⚖️ Ein Gleichgewicht": "Seed 14: genau ein reines Gleichgewicht (Knoten 5 und 13 gegen 8 und 11, 43,6 % zu 56,4 %); abwechselnde Bestantworten erreichen es nach 6 Zügen. Der optimale Führer (8 und 11) behält 56,4 %, der p-Median-Führer 49,1 %.",
    "🏃 Folger stärker": "p = 1, r = 2 (Seed 1): der Führer behält höchstens 28,8 % (p-Median-Führer und Optimum fallen bei Knoten 3 zusammen). Wer weniger Standorte hat, verliert.",
    "👑 Führer stärker": "p = 2, r = 1 (Seed 1): der p-Median-Führer behält 66,7 %, der optimale Führer (3 und 5) 71,2 %.",
    "🧲 Greedy versagt": "Straße mit 14 Knoten, p = r = 3: Greedy endet bei 21,4 %, die Swap-Lokalsuche erreicht das Optimum 53,6 % (nach 7 Zügen), der p-Median-Führer behält 50,0 %. Es gibt 20 Gleichgewichte.",
    "🪤 Swap steckt fest": "Seed 6: der p-Median-Führer (Knoten 7 und 14) behält 37,2 %, Greedy und Swap enden bei 39,5 % (kein einzelner Tausch hilft), das Optimum (5 und 7) liegt bei 51,2 %.",
}
