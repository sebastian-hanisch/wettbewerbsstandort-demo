"""Spiel: Anteile in Halbeinheiten von Hand, Gleichstand, Bestantwort gegen Aufzählung in reinem Python, Zulässigkeit."""

import pytest

import cmp_game as gm
from helpers import line, slow_best_reply, slow_gain, tiny


def test_split_on_a_five_node_line_by_hand():
    """Knoten bei 0/10/20/30/40, Führer bei 0, Folger bei 20: Knoten 1 liegt genau dazwischen (geteilt). Führer: 2 (Knoten 0) + 1 (Hälfte von Knoten 1) = 3 von 5."""
    g = gm.Game(line([0, 10, 20, 30, 40]))
    lead, foll = g.split((0,), (2,))
    assert (lead, foll) == (2 * 1 + 1, 2 * 3 + 1) and lead + foll == 2 * g.total
    assert list(g.owner((0,), (2,))) == [0, 2, 1, 1, 1]


def test_pct_is_percent_of_the_total_demand():
    g = gm.Game(line([0, 10, 20, 30, 40]))
    assert g.pct(g.split((0,), (2,))[0]) == pytest.approx(30.0)


def test_best_reply_is_never_on_a_leader_node_and_takes_the_lexicographically_smallest_tie():
    g = gm.Game(line([0, 10, 20, 30, 40, 50, 60]))
    gain, reply = g.best_reply((3,), 1)
    assert 3 not in reply and gain == 2 * 3 and reply == (2,)          # Knoten 2 und 4 sind gleich gut (je drei Knoten), kleinste Menge gewinnt
    vec = g.gain_vector((3,), 1)
    assert vec[3] == -1 and (vec[[i for i in range(7) if i != 3]] >= 0).all()


@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("k", [1, 2, 3])
def test_best_reply_equals_plain_python_enumeration(seed, k):
    net = tiny(seed, n=8)
    g = gm.Game(net)
    opp = (seed % 8, (seed + 3) % 8)
    assert g.best_reply(opp, k) == slow_best_reply(net, opp, k)


@pytest.mark.parametrize("seed", range(6))
def test_shares_of_both_players_always_add_up_to_the_whole(seed):
    net = tiny(seed, n=9)
    g = gm.Game(net)
    for a, b in (((0, 1), (2, 3)), ((4,), (5, 6, 7)), ((8,), (0,))):
        x, y = g.split(a, b)
        assert x + y == 2 * g.total and y == slow_gain(net, a, b)


def test_a_reply_set_that_overlaps_the_leader_is_not_allowed_even_for_the_best_gain():
    g = gm.Game(line([0, 10, 20, 30]))
    combos = g.sets(2)[0]
    vec = g.gain_vector((1, 2), 2)
    assert all(vec[i] == -1 for i, c in enumerate(combos) if {1, 2} & set(c)) and vec.max() >= 0
