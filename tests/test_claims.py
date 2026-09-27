"""Jede Zahl, die README und App nennen, ist hier belegt: Beispielnetze über ihre Seeds, Verteilungen über 40 feste Netze (Seeds ab 100000), das Raster über 20 feste Netze, die Straße.
Anteile sind exakt (Halbeinheiten, ganze Zahlen); Prozentwerte werden mit Toleranz verglichen. Gezählt werden Werte und Anzahlen, nie welche von mehreren gleich guten Mengen gewählt wird
(Ausnahme: die Voreinstellungen nennen die Knoten, die bei Gleichstand die lexikografisch kleinste Menge sind - deterministisch und plattformgleich)."""

import numpy as np
import pytest

import cmp_constants as C
import cmp_equilibrium as eq
import cmp_evaluation as ev
import cmp_game as gm
import cmp_leader as ld
import cmp_scenario as sc

PCT = pytest.approx


def P(kind="uniform", n=14, p=2, r=2, seed=1):
    return ev.Params(kind, n, p, r, seed)


def _preset(name):
    d = dict(C.PRESETS[name])
    d["kind"] = d.pop("net")
    return ev.Params(**d)


def _dist(**kw):
    return ev.distribution(P(**kw))["summary"]


def _nodes(sites):
    return [i + 1 for i in sites]


# --- Beispielnetze und Voreinstellungen ------------------------------------------------------------------------------------------------

def test_standard_net_leader_methods():
    """Standardnetz (14 Knoten, p = r = 2, Seed 1, Gesamtnachfrage 66): p-Median-Führer (Knoten 7, 13) 45,45 %; optimaler Führer (3, 13) 54,55 % mit der Antwort (6, 9); Greedy und Swap treffen das Optimum;
    zufällige Führer im Mittel 26,7 %, der schlechteste 7,6 %."""
    a = ev.analyse(P())
    assert a["net"].total == 66 and _nodes(a["naive"].sites) == [7, 13] and _nodes(a["exact"].sites) == [3, 13] and _nodes(a["exact"].reply) == [6, 9]
    assert a["pct"]["naive"] == PCT(45.45, abs=0.005) and a["pct"]["exact"] == PCT(54.55, abs=0.005) and a["pct"]["greedy"] == a["pct"]["swap"] == a["pct"]["exact"]
    assert a["random"] == PCT(26.66, abs=0.005) and a["worst"] == PCT(7.58, abs=0.005)


def test_standard_net_has_no_equilibrium_and_the_best_replies_cycle():
    """Standardnetz: kein reines Gleichgewicht; abwechselnde Bestantworten ab dem p-Median-Führer kehren nach 8 Zügen zu einem Zustand zurück (Zyklus)."""
    a = ev.analyse(P())
    assert a["nash"] == [] and a["outcome"] == "Zyklus" and len(a["trace"]) - 1 == 8


def test_the_middle_wins_on_a_street():
    """Straße mit 9 Knoten, p = r = 1: der Führer in der Mitte (Knoten 5) behält 55,56 %, die Antwort des Folgers ist ein Nachbar (Knoten 4) mit 44,44 %; zwei Gleichgewichte (4 gegen 5, 5 gegen 6);
    die Bestantworten erreichen ein Gleichgewicht nach einem Zug; p-Median-Führer und Optimum fallen zusammen."""
    a = ev.analyse(_preset("🛣️ Die Mitte gewinnt"))
    assert _nodes(a["exact"].sites) == [5] and _nodes(a["exact"].reply) == [4] and a["pct"]["exact"] == PCT(55.56, abs=0.005) and a["pct"]["naive"] == a["pct"]["exact"]
    assert [(_nodes(x), _nodes(y)) for x, y, _ in a["nash"]] == [([4], [5]), ([5], [6])] and a["outcome"] == "Gleichgewicht" and len(a["trace"]) - 1 == 1
    assert a["game"].pct(a["nash"][0][2]) == PCT(44.44, abs=0.005) and a["game"].pct(a["nash"][1][2]) == PCT(55.56, abs=0.005)


def test_preset_without_anticipation():
    """Seed 24: p-Median-Führer (2, 10) 39,73 %, optimaler Führer (9, 10) 53,42 % - 13,7 Prozentpunkte mehr durch Vorwegnehmen."""
    a = ev.analyse(_preset("🙈 Ohne Vorwegnahme"))
    assert _nodes(a["naive"].sites) == [2, 10] and _nodes(a["exact"].sites) == [9, 10]
    assert (a["pct"]["naive"], a["pct"]["exact"]) == (PCT(39.73, abs=0.005), PCT(53.42, abs=0.005)) and a["pct"]["exact"] - a["pct"]["naive"] == PCT(13.69, abs=0.01)


def test_preset_with_one_equilibrium():
    """Seed 14: genau ein Gleichgewicht ((5, 13) gegen (8, 11), 43,64 % zu 56,36 %), von den Bestantworten nach 6 Zügen erreicht; optimaler Führer (8, 11) 56,36 %, p-Median-Führer 49,09 %."""
    a = ev.analyse(_preset("⚖️ Ein Gleichgewicht"))
    assert [(_nodes(x), _nodes(y)) for x, y, _ in a["nash"]] == [([5, 13], [8, 11])] and a["game"].pct(a["nash"][0][2]) == PCT(43.64, abs=0.005)
    assert a["outcome"] == "Gleichgewicht" and len(a["trace"]) - 1 == 6 and _nodes(a["exact"].sites) == [8, 11] and (a["pct"]["exact"], a["pct"]["naive"]) == (PCT(56.36, abs=0.005), PCT(49.09, abs=0.005))


def test_preset_follower_stronger_and_leader_stronger():
    """p = 1, r = 2 (Seed 1): der Führer behält höchstens 28,79 %, p-Median-Führer und Optimum fallen bei Knoten 3 zusammen. p = 2, r = 1: p-Median-Führer 66,67 %, optimaler Führer (3, 5) 71,21 %."""
    a = ev.analyse(_preset("🏃 Folger stärker"))
    assert _nodes(a["exact"].sites) == [3] and a["pct"]["exact"] == PCT(28.79, abs=0.005) and a["naive"].sites == a["exact"].sites
    b = ev.analyse(_preset("👑 Führer stärker"))
    assert _nodes(b["exact"].sites) == [3, 5] and (b["pct"]["naive"], b["pct"]["exact"]) == (PCT(66.67, abs=0.005), PCT(71.21, abs=0.005))


def test_preset_greedy_fails_on_a_street():
    """Straße mit 14 Knoten, p = r = 3: Greedy endet bei 21,43 %, die Swap-Lokalsuche erreicht das Optimum 53,57 % (7 Züge), der p-Median-Führer behält 50,00 %; 20 Gleichgewichte."""
    a = ev.analyse(_preset("🧲 Greedy versagt"))
    assert a["pct"]["greedy"] == PCT(21.43, abs=0.005) and a["pct"]["swap"] == a["pct"]["exact"] == PCT(53.57, abs=0.005) and len(a["swap"].moves) == 7 and a["pct"]["naive"] == PCT(50.0)
    assert len(a["nash"]) == 20


def test_preset_swap_gets_stuck():
    """Seed 6: p-Median-Führer (7, 14) 37,21 %, Greedy und Swap enden bei 39,53 % (Swap ohne Zug), das Optimum (5, 7) liegt bei 51,16 %."""
    a = ev.analyse(_preset("🪤 Swap steckt fest"))
    assert _nodes(a["naive"].sites) == [7, 14] and _nodes(a["exact"].sites) == [5, 7] and a["swap"].moves == () and a["pct"]["naive"] == PCT(37.21, abs=0.005)
    assert a["pct"]["greedy"] == a["pct"]["swap"] == PCT(39.53, abs=0.005) and a["pct"]["exact"] == PCT(51.16, abs=0.005)


# --- Verteilungen über 40 feste Netze ------------------------------------------------------------------------------------------------------

def test_two_sites_each_over_40_nets():
    """40 Netze (14 Knoten, p = r = 2): p-Median-Führer im Mittel 46,1 % (28,6 bis 63,6), optimaler Führer 51,4 % (45,3 bis 63,6): Vorwegnehmen bringt 5,3 Punkte; zufällige Führer 26,7 %, die schlechtesten 6,2 %; der p-Median-Führer ist in 14 Netzen
    optimal; der optimale Führer behält in 26 Netzen mindestens die Hälfte, in 24 mehr; Greedy 49,2 % (optimal in 21, schlechtester Rückstand 11,7 Punkte), Swap 50,9 % (optimal in 34, schlechtester Rückstand 4,7)."""
    s = _dist(p=2, r=2)
    assert (s["naive"], s["exact"], s["random"], s["worst"]) == (PCT(46.1, abs=0.05), PCT(51.4, abs=0.05), PCT(26.7, abs=0.05), PCT(6.2, abs=0.05)) and s["gain"] == PCT(5.3, abs=0.05)
    assert (s["naive_min"], s["naive_max"], s["exact_min"], s["exact_max"]) == (PCT(28.6, abs=0.05), PCT(63.6, abs=0.05), PCT(45.3, abs=0.05), PCT(63.6, abs=0.05))
    assert (s["naive_is_opt"], s["leader_half"], s["leader_majority"]) == (14, 26, 24)
    assert (s["greedy"], s["greedy_is_opt"], s["greedy_gap_max"]) == (PCT(49.2, abs=0.05), 21, PCT(11.7, abs=0.05)) and (s["swap"], s["swap_is_opt"], s["swap_gap_max"]) == (PCT(50.9, abs=0.05), 34, PCT(4.7, abs=0.05))


def test_one_site_each_over_40_nets():
    """p = r = 1: p-Median-Führer 51,2 %, optimaler Führer 52,9 % (nur 1,7 Punkte mehr; der p-Median-Führer ist in 31 Netzen optimal), Greedy und Swap optimal in 40 von 40; Gleichgewichte in 21 von 40 Netzen (im Mittel 0,65, höchstens 3)."""
    s = _dist(p=1, r=1)
    assert (s["naive"], s["exact"], s["gain"]) == (PCT(51.2, abs=0.05), PCT(52.9, abs=0.05), PCT(1.7, abs=0.05)) and s["naive_is_opt"] == 31 and s["greedy_is_opt"] == s["swap_is_opt"] == 40
    assert (s["nash_nets"], s["nash_mean"], s["nash_max"]) == (21, PCT(0.65), 3)


def test_three_sites_each_over_40_nets():
    """p = r = 3: p-Median-Führer 47,7 %, optimaler Führer 53,5 % (5,7 Punkte mehr; optimal nur in 10 Netzen), Greedy 50,5 % (optimal in 20, Rückstand bis 15,7), Swap 52,8 % (optimal in 34, bis 6,7); Gleichgewichte in 10 von 40 Netzen (höchstens 6)."""
    s = _dist(p=3, r=3)
    assert (s["naive"], s["exact"], s["gain"]) == (PCT(47.7, abs=0.05), PCT(53.5, abs=0.05), PCT(5.7, abs=0.05)) and s["naive_is_opt"] == 10
    assert (s["greedy"], s["greedy_is_opt"], s["greedy_gap_max"]) == (PCT(50.5, abs=0.05), 20, PCT(15.7, abs=0.05)) and (s["swap"], s["swap_is_opt"], s["swap_gap_max"]) == (PCT(52.8, abs=0.05), 34, PCT(6.7, abs=0.05))
    assert (s["nash_nets"], s["nash_max"]) == (10, 6)


def test_equilibria_are_rare_and_the_best_replies_mostly_cycle():
    """Reine Gleichgewichte in 21 / 8 / 10 von 40 Netzen (p = r = 1 / 2 / 3); die abwechselnden Bestantworten ab dem p-Median-Führer kommen in 18 / 6 / 5 Netzen zur Ruhe und laufen in 22 / 34 / 34 im Kreis."""
    got = [(_dist(p=k, r=k)["nash_nets"], _dist(p=k, r=k)["stable"], _dist(p=k, r=k)["cycles"]) for k in (1, 2, 3)]
    assert got == [(21, 18, 22), (8, 6, 34), (10, 5, 34)]


@pytest.mark.parametrize("p, r, naive, exact, greedy_opt, swap_opt", [(2, 1, 68.9, 72.4, 14, 31), (1, 2, 18.8, 23.5, 40, 40)])
def test_asymmetric_cases_over_40_nets(p, r, naive, exact, greedy_opt, swap_opt):
    """p = 2, r = 1: p-Median-Führer 68,9 %, optimaler Führer 72,4 %, der Führer behält in allen 40 Netzen mehr als die Hälfte; p = 1, r = 2: 18,8 % und 23,5 %, in keinem Netz mindestens die Hälfte."""
    s = _dist(p=p, r=r)
    assert (s["naive"], s["exact"]) == (PCT(naive, abs=0.05), PCT(exact, abs=0.05)) and (s["greedy_is_opt"], s["swap_is_opt"]) == (greedy_opt, swap_opt)
    assert s["leader_majority"] == (40 if p > r else 0) and (s["leader_half"] == 40 if p > r else s["leader_half"] == 0)


def test_cluster_nets_over_40_nets():
    """Vier Cluster (14 Knoten, p = r = 2): p-Median-Führer 45,4 %, optimaler Führer 51,6 %; Gleichgewichte in 13 von 40 Netzen."""
    s = _dist(kind="cluster", p=2, r=2)
    assert (s["naive"], s["exact"]) == (PCT(45.4, abs=0.05), PCT(51.6, abs=0.05)) and s["nash_nets"] == 13


def test_equilibria_get_rarer_with_the_size_of_the_net():
    """p = r = 2, gleichverteilt, 20 feste Netze: Gleichgewichte in 16 / 8 / 2 / 0 Netzen bei 8 / 10 / 18 / 22 Knoten."""
    counts = []
    for n in (8, 10, 18, 22):
        counts.append(sum(1 for seed in C.GRID_SEEDS if ev.one_net(P(n=n), seed)["nash"] > 0))
    assert counts == [16, 8, 2, 0]


def test_grid_over_leader_and_follower_sites():
    """Mittlerer Anteil des p-Median-Führers / optimalen Führers (20 Netze, 14 Knoten), Zeilen p = 1, 2, 3, Spalten r = 1, 2, 3: (49,6 / 51,9, 20,5 / 24,6, 10,4 / 14,0), (68,5 / 71,7, 44,1 / 50,3, 30,0 / 36,1), (75,3 / 80,4, 58,5 / 65,5, 47,1 / 53,4)."""
    g = ev.pr_grid(P())
    expected = {(1, 1): (49.6, 51.9), (1, 2): (20.5, 24.6), (1, 3): (10.4, 14.0), (2, 1): (68.5, 71.7), (2, 2): (44.1, 50.3), (2, 3): (30.0, 36.1), (3, 1): (75.3, 80.4), (3, 2): (58.5, 65.5), (3, 3): (47.1, 53.4)}
    for key, (naive, exact) in expected.items():
        assert (g["cells"][key]["naive"], g["cells"][key]["exact"]) == (PCT(naive, abs=0.05), PCT(exact, abs=0.05)), key
    assert all(g["cells"][k]["exact"] >= g["cells"][k]["naive"] for k in g["cells"])


# --- Straße ---------------------------------------------------------------------------------------------------------------------------------

def test_a_street_always_has_an_equilibrium():
    """Straße, 8 bis 24 Knoten, p = r = 1 / 2 / 3: in jedem der 51 Fälle mindestens ein reines Gleichgewicht (auf der Karte in 21 / 8 / 10 von 40 Netzen)."""
    for n in range(8, 25):
        for k in (1, 2, 3):
            assert ev.analyse(P(kind="street", n=n, p=k, r=k))["nash"], (n, k)


def test_street_with_two_sites_each_p_median_is_optimal_and_greedy_fails():
    """Straße mit 14 Knoten, p = r = 2: p-Median-Führer und Optimum 53,57 %, Greedy 39,29 %, Swap 53,57 %; sechs Gleichgewichte."""
    a = ev.analyse(P(kind="street", n=14, p=2, r=2))
    assert a["pct"]["naive"] == a["pct"]["exact"] == a["pct"]["swap"] == PCT(53.57, abs=0.005) and a["pct"]["greedy"] == PCT(39.29, abs=0.005) and len(a["nash"]) == 6


# --- Gleichstandsregel -----------------------------------------------------------------------------------------------------------------------

class _LeaderKeepsTies(gm.Game):
    """Variante: bei Gleichstand behält der Führer die ganze Nachfrage (der Folger zählt nur echte Siege)."""

    def gain_vector(self, opp, k):
        combos, fmin, member = self.sets(k)
        dl = self.dist_to(opp)
        gain = ((fmin < dl) * 2) @ self.w
        return np.where(member[:, list(opp)].any(axis=1), -1, gain)


@pytest.mark.parametrize("k, naive, exact", [(2, 46.2, 51.5), (3, 47.8, 53.5)])
def test_tie_rule_hardly_changes_the_picture(k, naive, exact):
    """Bekommt der Führer bei Gleichstand die ganze Nachfrage statt der Hälfte (40 Netze, 14 Knoten): p = r = 2 46,2 % / 51,5 % (statt 46,1 / 51,4), p = r = 3 47,8 % / 53,5 % (statt 47,7 / 53,5) - die Aussage bleibt."""
    nv, ex = [], []
    for seed in C.SWEEP_SEEDS:
        g = _LeaderKeepsTies(sc.generate(14, "uniform", seed))
        best, _ = ld.exact(g, k, k)
        nv.append(g.pct(ld.naive(g, k, k).value))
        ex.append(g.pct(best.value))
    assert sum(nv) / 40 == PCT(naive, abs=0.05) and sum(ex) / 40 == PCT(exact, abs=0.05)
