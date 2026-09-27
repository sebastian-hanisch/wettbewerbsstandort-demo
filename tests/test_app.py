"""Rauchtests der Streamlit-Oberfläche per AppTest: Standard, jedes Preset, Randgrößen, asymmetrisches p/r, Permalink, Zug-um-Zug, Experimente auf Abruf."""

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import cmp_constants as C
from cmp_presets import PRESET_KEYS

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None, timeout=300):
    at = AppTest.from_file(str(APP), default_timeout=timeout)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    if setup is not None:
        setup(at)
        at.run()
        assert not at.exception, [e.value for e in at.exception]
    return at


def _apply(at, p):
    for key, state_key in PRESET_KEYS.items():
        at.session_state[state_key] = p[key]


def _metric(at, label):
    return [m.value for m in at.metric if m.label == label]


def _texts(at):
    return [e.value for e in list(at.success) + list(at.warning) + list(at.info) + list(at.error)]


def _button(at, key):
    return next(b for b in at.button if b.key == key)


def test_default_renders_and_names_the_headline_numbers():
    at = _run()
    assert any("**54,5 %**" in m.value for m in at.markdown)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders(name):
    at = _run(lambda a: _apply(a, C.PRESETS[name]))
    assert not at.error


def test_extreme_sizes_render():
    for vals in ((("n_slider", C.N_MIN), ("p_slider", C.P_MIN), ("r_slider", C.R_MIN)),
                 (("n_slider", C.N_MAX), ("p_slider", C.P_MAX), ("r_slider", C.P_MAX))):
        def setup(at, vals=vals):
            for key, value in vals:
                at.session_state[key] = value
        at = _run(setup)
        assert not at.error


def test_asymmetric_p_and_r_shows_a_notice_instead_of_the_dynamics():
    def setup(at):
        at.session_state["p_slider"] = 1
        at.session_state["r_slider"] = 2
    at = _run(setup)
    assert any("müssen beide Seiten gleich viele Standorte haben" in t for t in _texts(at))


def test_street_disables_the_seed_and_the_grid_size_experiments():
    def setup(at):
        at.session_state["net_select"] = "street"
    at = _run(setup)
    assert not [w for w in at.sidebar.number_input if w.key == "seed_input"]
    assert _button(at, "dist_start").disabled and _button(at, "grid_start").disabled


def test_selection_must_have_exactly_p_sites():
    at = _run()
    at.multiselect(key="pick_multi").set_value([0])
    at.run()
    assert not at.exception and any("Wählen Sie genau 2 Knoten" in t for t in _texts(at))
    at.multiselect(key="pick_multi").set_value([0, 1])
    at.run()
    assert not at.exception and _metric(at, "Optimum")


def test_selection_resets_when_p_changes():
    at = _run()
    at.multiselect(key="pick_multi").set_value([0, 1])
    at.run()
    at.sidebar.slider(key="p_slider").set_value(3)
    at.run()
    assert not at.exception and len(at.multiselect(key="pick_multi").value) == 3


def test_permalink_settings_are_loaded_and_clamped():
    at = AppTest.from_file(str(APP), default_timeout=300)
    at.query_params["net"] = "cluster"
    at.query_params["n"] = "999"
    at.query_params["p"] = "5"
    at.query_params["r"] = "2"
    at.run()
    assert not at.exception
    assert at.sidebar.selectbox(key="net_select").value == "cluster" and at.sidebar.slider(key="n_slider").value == C.N_MAX and at.sidebar.slider(key="p_slider").value == C.P_MAX


def test_invalid_permalink_values_fall_back_to_the_defaults():
    at = AppTest.from_file(str(APP), default_timeout=300)
    at.query_params["net"] = "nirgendwo"
    at.query_params["seed"] = "x"
    at.run()
    assert not at.exception and at.sidebar.selectbox(key="net_select").value == C.DEFAULT_NET


def test_step_slider_moves_through_the_dynamics_trace():
    at = _run()
    slider = next(s for s in at.slider if s.key == "cmp_step")
    for value in range(int(slider.min), int(slider.max) + 1):
        slider.set_value(value)
        at.run()
        assert not at.exception and slider.value == value


def test_experiments_run_on_demand(monkeypatch):
    import cmp_evaluation as ev
    d_o, g_o = ev.distribution, ev.pr_grid
    monkeypatch.setattr(ev, "distribution", lambda p: d_o(p, seeds=C.SWEEP_SEEDS[:4]))
    monkeypatch.setattr(ev, "pr_grid", lambda p: g_o(p, seeds=C.GRID_SEEDS[:3]))
    at = _run()
    for key in ("dist_start", "grid_start"):
        _button(at, key).click().run()
        assert not at.exception, key
    assert any("Vorwegnehmen bringt im Mittel" in c.value for c in at.caption)


def test_source_has_explicit_chart_keys_and_locked_axes():
    app = APP.read_text(encoding="utf-8")
    assert all(re.search(r"plotly_chart\(.*key=", line) for line in app.splitlines() if "st.plotly_chart(" in line)
    viz = (ROOT / "cmp_visualization.py").read_text(encoding="utf-8")
    assert viz.count("_base(fig") >= 4 and "def lock_axes" in viz
