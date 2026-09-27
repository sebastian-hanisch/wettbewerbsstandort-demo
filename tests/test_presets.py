"""Presets: vollständig, in den Grenzen, und jedes Beispiel zeigt, was sein Name verspricht (die Zahlen selbst belegt test_claims.py)."""

import pytest

import cmp_constants as C
import cmp_evaluation as ev
import cmp_presets as P

KEYS = set(P.PRESET_KEYS)


def _params(pr):
    d = dict(pr)
    d["kind"] = d.pop("net")
    return ev.Params(**d)


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP) and len(C.PRESETS) == 8
    assert all(C.PRESET_HELP[name].strip() for name in C.PRESETS)
    for name, p in C.PRESETS.items():
        assert set(p) == KEYS, name


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_preset_values_are_inside_the_bounds(name):
    p = C.PRESETS[name]
    assert p["net"] in C.NETS
    for key, state_key in P.PRESET_KEYS.items():
        spec = P.SETTING_SPECS[state_key]
        if spec.lo is not None:
            assert spec.lo <= p[key] <= spec.hi, (name, key)


def test_setting_specs_have_room_to_move():
    """Ein Regler mit lo == hi würde Streamlit abstürzen lassen."""
    assert all(spec.lo < spec.hi for spec in P.SETTING_SPECS.values() if spec.lo is not None)


def test_each_preset_shows_the_effect_its_name_promises():
    a = {name: ev.analyse(_params(p)) for name, p in C.PRESETS.items()}
    assert a["🗺️ Standardnetz"]["outcome"] == "Zyklus" and a["🗺️ Standardnetz"]["nash"] == []
    middle = a["🛣️ Die Mitte gewinnt"]
    assert middle["exact"].sites == middle["naive"].sites and middle["outcome"] == "Gleichgewicht"
    no_ant = a["🙈 Ohne Vorwegnahme"]
    assert no_ant["pct"]["exact"] > no_ant["pct"]["naive"] + 5
    one_eq = a["⚖️ Ein Gleichgewicht"]
    assert len(one_eq["nash"]) == 1 and one_eq["outcome"] == "Gleichgewicht"
    weaker = a["🏃 Folger stärker"]
    assert weaker["pct"]["exact"] < 50
    stronger = a["👑 Führer stärker"]
    assert stronger["pct"]["exact"] > 50
    greedy_fail = a["🧲 Greedy versagt"]
    assert greedy_fail["pct"]["greedy"] < greedy_fail["pct"]["swap"] == greedy_fail["pct"]["exact"]
    swap_stuck = a["🪤 Swap steckt fest"]
    assert swap_stuck["swap"].moves == () and swap_stuck["pct"]["swap"] < swap_stuck["pct"]["exact"]


def test_the_standard_preset_is_the_default_configuration():
    assert C.PRESETS["🗺️ Standardnetz"] == {"net": C.DEFAULT_NET, "n": C.DEFAULT_N, "p": C.DEFAULT_P, "r": C.DEFAULT_R, "seed": C.DEFAULT_SEED}
    assert ev.Params() == _params(C.PRESETS["🗺️ Standardnetz"])
