"""Standortwettbewerb - wer vorwegnimmt, gewinnt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo EIN Modell - Standortwettbewerb zwischen einem Führer und einem Folger ((r|p)-Centroid, Stackelberg) - und lässt stattdessen das Beispiel wachsen.
Neues Stück der Standortplanungs-Linie der "Konzepte"-Reihe, Kind des Standortproblems ohne Kapazität (Wurzel): dieselben Knoten als Standorte, aber ein Gegenspieler antwortet auf die Wahl.
Siehe README für die Einordnung.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import cmp_constants as C
import cmp_evaluation as ev
from cmp_presets import (
    KEPT,
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    seed_widget,
    sync_query_params,
)
from cmp_visualization import build_grid, build_map, build_scatter, build_shares

st.set_page_config(page_title="Standortwettbewerb – Sebastian Hanisch", layout="wide")


def _f(x, digits=1):
    return "–" if x is None else f"{x:.{digits}f}".replace(".", ",")


def _pct(x, digits=1):
    return "–" if x is None else f"{x:.{digits}f} %".replace(".", ",")


def _int(x):
    return "–" if x is None else f"{int(round(x)):,}".replace(",", " ")


def _sites(group):
    return ", ".join(str(i + 1) for i in group) if group else "–"


@st.cache_resource(show_spinner=False, max_entries=32)
def _analysis(p):
    return ev.analyse(p)


@st.cache_resource(show_spinner=False, max_entries=8)
def _dist(p):
    return ev.distribution(p)


@st.cache_resource(show_spinner=False, max_entries=8)
def _grid(p):
    return ev.pr_grid(p)


st.title("♟️ Standortwettbewerb – wer vorwegnimmt, gewinnt")
st.markdown(
    """
Bisher wählte ein Planer Standorte allein. Jetzt **zieht ein Führer zuerst** ($p$ Standorte), und ein **Folger antwortet** ($r$ Standorte): jeder Kunde geht zum **näheren** Standort, bei Gleichstand teilen sich beide seine Nachfrage.
Wer zuerst zieht, muss die **Antwort vorwegnehmen** – wer nur „gute“ Standorte wählt (die Summe der Wege minimieren), verschenkt Nachfrage. Die Demo zeigt, **wie viel** das Vorwegnehmen bringt, wie die Verfahren dafür abschneiden
und warum es ohne Reihenfolge **meist kein Gleichgewicht** gibt.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren vergleichen, zeigt diese Demo - ein Stück der Standortplanungs-Linie der \"Konzepte\"-Reihe - **ein** Modell an einem wachsenden Beispiel. "
    "Verwandt: das Standortproblem ohne Kapazität (ein Planer allein), die Stackelberg-Demo (Führer und Folger bei der Torwahl von Lkw) und die Nash-Demo (Gleichgewichte), die Rettungsdienst-Demo (Überdeckung)."
)

with st.expander("So funktioniert das Modell", expanded=True):
    st.markdown(
        r"""
1. **Spiel:** $n$ Knoten mit Nachfrage $w_j$; Standorte können nur an Knoten eröffnet werden. Der Führer wählt $L$ ($|L|=p$), der Folger antwortet mit $F$ ($|F|=r$, andere Knoten). Kunde $j$ geht zum näheren Standort, bei gleichem Abstand teilt sich die Nachfrage.
2. **Antwort des Folgers:** exakt – alle $r$-Mengen werden aufgezählt, die mit dem größten Anteil gewinnt. Damit ist das Ergebnis für den Führer eindeutig bewertbar: was **bleibt ihm nach der besten Antwort?**
3. **Führer:** *naiv* = der Führer, der den Folger ignoriert (kleinste gewichtete Wegesumme, $p$-Median); *Greedy* und *Swap-Lokalsuche* rechnen gegen die exakte Antwort; *exakt* zählt alle $p$-Mengen auf.
4. **Gleichgewicht:** ein Paar aus Führer- und Folgermenge, in dem beide auf den anderen optimal antworten. Abwechselnde Bestantworten (Spieler 0, Spieler 1, …) laufen im Kreis, wenn es keines gibt.
        """
    )

st.caption("🎯 Schnellstart – ein Beispiel laden:")
names = list(C.PRESETS.keys())
for row in range(0, len(names), 4):
    preset_cols = st.columns(4)
    for col, name in zip(preset_cols, names[row:row + 4]):
        with col:
            st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name] or None)

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    net_key = st.selectbox("Netz", list(C.NETS), key="net_select", format_func=lambda k: C.NETS[k],
                           help="Ein Zufallsnetz (gleichverteilt oder in vier Clustern) oder die Straße: Knoten in gleichem Abstand auf einer Linie, alle mit gleicher Nachfrage (das klassische Hotelling-Beispiel).")
    n_nodes = st.slider("Knoten", *bounds("n_slider"), key="n_slider", help="Wie viele Knoten das Netz hat: jeder ist Kunde mit einer Nachfrage und möglicher Standort.")
    p_val = st.slider("Standorte des Führers (p)", *bounds("p_slider"), key="p_slider", help="Wie viele Standorte der Führer als Erster eröffnet.")
    r_val = st.slider("Standorte des Folgers (r)", *bounds("r_slider"), key="r_slider", help="Wie viele Standorte der Folger danach eröffnet (auf anderen Knoten).")
    if net_key in C.FIXED_NETS:
        seed = int(st.session_state.get(KEPT["seed_input"], C.DEFAULT_SEED))
        st.caption("Die Straße ist fest - der Seed gehört zu den Zufallsnetzen.")
    else:
        seed_widget("seed_input")
        seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
        st.session_state[KEPT["seed_input"]] = seed
        st.button("🎲 Neues Netz generieren", width="stretch", on_click=randomize_seed, help="Würfelt einen neuen Zufalls-Seed. Die Verteilungen über feste Netze weiter unten ändern sich dabei nicht.")

sync_query_params({"net_select": net_key, "n_slider": int(n_nodes), "p_slider": int(p_val), "r_slider": int(r_val), "seed_input": int(seed)})

params = ev.Params(net_key, int(n_nodes), int(p_val), int(r_val), int(seed))
with st.spinner("Rechne..."):
    a = _analysis(params)
net, game = a["net"], a["game"]
p, r = params.p, params.r
pc = a["pct"]

st.markdown(
    f"Das Netz hat **{net.n} Knoten** mit der Gesamtnachfrage **{net.total}**. Der Führer wählt **{p}** Standort{'e' if p > 1 else ''}, der Folger antwortet mit **{r}**. "
    f"Wer den Wettbewerb ignoriert (kleinste Wegesumme), behält nach der besten Antwort **{_pct(pc['naive'])}** der Nachfrage; der **optimale** Führer behält **{_pct(pc['exact'])}**."
)

# --- Selbst probieren ---------------------------------------------------------------------------------------------------------------

st.markdown("## ♟️ Selbst probieren: Sie sind der Führer")
if st.session_state.get("cmp_pick_owner") != params:
    st.session_state["pick_multi"] = list(a["naive"].sites)
    st.session_state["cmp_pick_owner"] = params
chosen = st.multiselect(f"Ihre {p} Standort{'e' if p > 1 else ''}", list(range(net.n)), key="pick_multi", format_func=lambda i: net.names[i], max_selections=p,
                        help="Voreingestellt ist der Führer, der den Folger ignoriert (kleinste gewichtete Wegesumme). Der Folger antwortet exakt; jeder Knoten geht zum näheren Standort, bei Gleichstand wird geteilt.")
cl, cr = st.columns([5, 4])
if len(chosen) == p:
    t = ev.try_sites(game, tuple(sorted(chosen)), r)
    with cl:
        st.plotly_chart(build_map(net, game, tuple(sorted(chosen)), t["reply"], height=460), width="stretch", key="pick_map")
    with cr:
        m1, m2 = st.columns(2)
        m1.metric("Ihr Anteil", _pct(t["leader"]), delta=f"{_f(t['leader'] - pc['exact'])} Pkt." if t["leader"] < pc["exact"] - 1e-9 else "Optimum", delta_color="normal" if t["leader"] < pc["exact"] - 1e-9 else "off",
                  help="Prozentpunkte gegenüber dem optimalen Führer.")
        m2.metric("Folger-Anteil", _pct(t["follower"]))
        m3, m4 = st.columns(2)
        m3.metric("Optimum", _pct(pc["exact"]), help="Was der beste Führer nach der besten Antwort behält (alle Mengen aufgezählt).")
        m4.metric("Folger-Antwort", _sites(t["reply"]), help="Knotennummern der besten Antwort (bei gleich guten Antworten die lexikografisch kleinste).")
else:
    with cl:
        st.info(f"Wählen Sie genau {p} Knoten ({len(chosen)} von {p} gewählt).")
st.caption("Blau: gehört zum Führer; rot: zum Folger; violett: Gleichstand (geteilt). Quadrate: Standorte (dunkelblau Führer, dunkelrot Folger, Nummer = Knotennummer); Größe nach Nachfrage.")

st.markdown("---")

# --- Führer-Verfahren ----------------------------------------------------------------------------------------------------------------

st.markdown("## ♟️ Wie gut sind die Führer-Verfahren?")
methods = [("Optimal (alle Mengen aufgezählt)", a["exact"], "exact"), ("Swap-Lokalsuche (ab Greedy)", a["swap"], "swap"), ("Greedy", a["greedy"], "greedy"), ("Naiv: p-Median (ignoriert den Folger)", a["naive"], "naive")]
st.plotly_chart(build_shares([(m[0], pc[m[2]]) for m in methods] + [("Zufällige Standorte (Mittel)", a["random"]), ("Schlechteste Standorte", a["worst"])]), width="stretch", key="shares_chart")
st.table({"Verfahren": [m[0] for m in methods], "Standorte des Führers": [_sites(m[1].sites) for m in methods], "Antwort des Folgers": [_sites(m[1].reply) for m in methods],
          "Anteil des Führers": [_pct(pc[m[2]]) for m in methods], "unter dem Optimum": [_pct(pc["exact"] - pc[m[2]]) if pc[m[2]] < pc["exact"] - 1e-9 else "–" for m in methods]})
st.caption(f"Bewertete Führermengen: Greedy {_int(a['greedy'].evals)}, Swap {_int(a['swap'].evals)} (davon {len(a['swap'].moves)} Züge), exakt {_int(a['exact'].evals)}. Vorwegnehmen bringt {_f(pc['exact'] - pc['naive'])} Prozentpunkte gegenüber dem naiven Führer; "
           "die Antwort des Folgers ist immer exakt gerechnet.")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**Naiv** (p-Median): {_pct(pc['naive'])}")
    st.plotly_chart(build_map(net, game, a["naive"].sites, a["naive"].reply, height=380), width="stretch", key="map_naive")
with c2:
    st.markdown(f"**Optimal**: {_pct(pc['exact'])}")
    st.plotly_chart(build_map(net, game, a["exact"].sites, a["exact"].reply, height=380), width="stretch", key="map_exact")
if pc["swap"] < pc["exact"] - 1e-9:
    st.warning(f"⚠️ Die Swap-Lokalsuche endet bei {_pct(pc['swap'])}, das Optimum ist {_pct(pc['exact'])}: kein einzelner Tausch führt dorthin.")
elif pc["greedy"] < pc["exact"] - 1e-9:
    st.info(f"Greedy endet bei {_pct(pc['greedy'])}; erst die Swap-Lokalsuche erreicht das Optimum ({_pct(pc['exact'])}).")

st.markdown("---")

# --- Zug um Zug ----------------------------------------------------------------------------------------------------------------------

st.markdown("## ♟️ Zug um Zug: gibt es ein Gleichgewicht?")
if p != r:
    st.info("Für ein Gleichgewicht müssen beide Seiten gleich viele Standorte haben: stellen Sie p und r gleich ein.")
else:
    trace = a["trace"]
    owner = (params,)
    if st.session_state.get("cmp_step_owner") != owner:
        st.session_state["cmp_step"] = len(trace) - 1
        st.session_state["cmp_step_owner"] = owner
    view_slot = st.empty()
    step_col, play_col = st.columns([5, 2])
    with step_col:
        step = st.slider("Zug", 0, len(trace) - 1, key="cmp_step", help="Zug 0: der Führer steht bei der p-Median-Lösung. Danach antwortet abwechselnd Spieler 1 und Spieler 0 mit der Bestantwort (wer schon eine Bestantwort hält, bleibt).")
    with play_col:
        auto_play = st.button("▶️ Abspielen", width="stretch")

    def _render(k):
        pos = [None, None]
        for who, sites_k, _gain in trace[:k + 1]:
            pos[who] = sites_k
        with view_slot.container():
            c_map, c_txt = st.columns([3, 2])
            with c_map:
                st.plotly_chart(build_map(net, game, pos[0], pos[1], height=380), width="stretch", key=f"dyn_map_{k}")
            with c_txt:
                who, sites_k, gain = trace[k]
                if k == 0:
                    st.markdown(f"**Zug 0:** Spieler 0 (blau) steht bei {_sites(sites_k)} (p-Median-Lösung).")
                else:
                    st.markdown(f"**Zug {k}:** Spieler {who} ({'rot' if who == 1 else 'blau'}) antwortet mit {_sites(sites_k)} und erobert {_pct(game.pct(gain))} der Nachfrage.")
                if pos[0] and pos[1]:
                    share0, share1 = game.split(pos[0], pos[1])
                    st.metric("Anteil Spieler 0 / Spieler 1", f"{_pct(game.pct(share0))} / {_pct(game.pct(share1))}")

    if auto_play:
        for k in range(len(trace)):
            _render(k)
            time.sleep(min(0.6, 6.0 / max(len(trace), 1)))
    else:
        _render(step)
    nash = a["nash"]
    if a["outcome"] == "Gleichgewicht":
        final = [None, None]
        for who, sites_k, _gain in trace:
            final[who] = sites_k
        share0 = game.split(final[0], final[1])[0]
        st.success(f"✅ Nach {len(trace) - 1} Zügen bleibt jeder bei seiner Bestantwort: ein Gleichgewicht (Spieler 0 behält {_pct(game.pct(share0))}).")
    elif a["outcome"] == "Zyklus":
        st.warning(f"⚠️ Nach {len(trace) - 1} Zügen kehrt ein Zustand wieder: die Bestantworten laufen im Kreis.")
    else:
        st.info("Die Bestantwort-Dynamik ist nach 40 Zügen nicht zur Ruhe gekommen.")
    if nash:
        pairs = "; ".join(f"({_sites(x)} | {_sites(y)})" for x, y, _s in nash[:4])
        st.markdown(f"Es gibt **{len(nash)}** reine Gleichgewichte (Menge des einen | Menge des anderen)" + (f", z. B. {pairs}." if pairs else "."))
        if a["outcome"] != "Gleichgewicht":
            st.caption("Es gibt Gleichgewichte, aber die abwechselnden Bestantworten ab der p-Median-Lösung finden keines - die Dynamik ist kein Rechenverfahren für Gleichgewichte.")
    else:
        st.markdown("Es gibt **kein** reines Gleichgewicht: zu jedem Paar findet mindestens ein Spieler eine bessere Antwort. Deshalb braucht das Spiel die Reihenfolge - der Führer legt sich fest, der Folger antwortet.")

st.markdown("---")

# --- Experimente ----------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Gilt das in jedem Netz?")
st.caption(f"40 feste Netze (Art {C.NETS[params.kind].lower()}, {params.n} Knoten, p = {p}, r = {r}): p-Median-Führer, Greedy, Swap und der optimale Führer" + (", dazu die Gleichgewichte." if p == r else "."))
if net_key == "street":
    st.caption("Die Straße ist ein einziges Netz (der Seed spielt keine Rolle): alle 40 Netze wären gleich.")
if st.button("40 Netze durchrechnen (dauert einige Sekunden)", key="dist_start", disabled=net_key == "street", help="Nicht für die Straße (ein einziges Netz)." if net_key == "street" else None):
    st.session_state["dist_on"] = True
if st.session_state.get("dist_on") and net_key != "street":
    with st.spinner("Rechne 40 Netze..."):
        dist = _dist(params)
    s = dist["summary"]
    st.plotly_chart(build_scatter(dist["rows"]), width="stretch", key="dist_chart")
    st.table({"Größe": ["p-Median-Führer (ignoriert den Folger)", "Greedy", "Swap-Lokalsuche", "Optimaler Führer", "Zufällige Standorte", "Schlechteste Standorte"],
              "Anteil im Mittel": [_pct(s[k]) for k in ("naive", "greedy", "swap", "exact", "random", "worst")],
              "genau optimal in": [f"{s['naive_is_opt']} von {s['count']}", f"{s['greedy_is_opt']} von {s['count']}", f"{s['swap_is_opt']} von {s['count']}", "–", "–", "–"]})
    st.caption(f"Vorwegnehmen bringt im Mittel {_f(s['gain'])} Prozentpunkte. Der optimale Führer behält in {s['leader_half']} von {s['count']} Netzen mindestens die Hälfte, in {s['leader_majority']} mehr als die Hälfte "
               f"(zwischen {_pct(s['exact_min'])} und {_pct(s['exact_max'])}); der schlechteste Swap-Rückstand beträgt {_f(s['swap_gap_max'])} Prozentpunkte.")
    if "nash_nets" in s:
        st.caption(f"Reine Gleichgewichte gibt es in {s['nash_nets']} von {s['count']} Netzen (im Mittel {_f(s['nash_mean'], 2)}, höchstens {s['nash_max']}). Abwechselnde Bestantworten ab der p-Median-Lösung kommen in {s['stable']} Netzen zur Ruhe und laufen in {s['cycles']} im Kreis.")

st.subheader("🔬 Wie viel bringt Vorwegnehmen bei welcher Größe?")
st.caption("Mittlerer Anteil des optimalen Führers (und des p-Median-Führers) über 20 feste Netze für alle Kombinationen von p und r (Netzart und Knotenzahl wie eingestellt).")
if st.button("Raster durchrechnen (dauert einige Sekunden)", key="grid_start", disabled=net_key == "street"):
    st.session_state["grid_on"] = True
if st.session_state.get("grid_on") and net_key != "street":
    with st.spinner("Rechne 9 Kombinationen × 20 Netze..."):
        gr = _grid(params)
    st.plotly_chart(build_grid(gr), width="stretch", key="grid_chart")
    st.caption("Zeile: Standorte des Führers, Spalte: Standorte des Folgers; Zahl in der Zelle: p-Median-Führer / optimaler Führer (in %). Wer mehr Standorte hat als der andere, gewinnt; gleiche Zahl heißt ungefähr die Hälfte.")

st.markdown("---")

# --- Grenzen ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist - und wer ansetzt |
|---|---|
| **Standorte nur an Knoten** | Im kontinuierlichen Raum (Hotelling auf der Linie oder in der Ebene) sind Gleichgewichte und Optima anders; hier zieht jeder Spieler Knoten. |
| **Nächster Standort gewinnt, Gleichstand halbe-halbe** | Keine Preise, keine Attraktivität, kein Gravitationsmodell (Huff); die Gleichstandsregel ändert die Aussagen nicht (gemessen: Führer ohne Gleichstandsanteil verhält sich fast gleich), aber die Modellwelt bleibt einfach. |
| **Genau ein Folger, eine Antwort** | Mehrere Folger, mehrere Runden oder Rückantworten des Führers (Mehrstufigkeit) sind nicht gebaut; die abwechselnden Bestantworten sind nur eine Veranschaulichung. |
| **Kein Fixkostenkalkül** | Standorte kosten nichts, die Zahl p bzw. r ist fest; die Standortplanung mit Kosten behandeln die anderen Stücke der Linie. |
| **Aufzählung** | Die exakte Antwort und das Führer-Optimum zählen alle Mengen auf (bis 24 Knoten und 3 Standorte je Seite); für größere Netze braucht es Bilevel-Löser oder Heuristiken mit Prüfung. |
| **Erzeugte Netze** | Gleichverteilte oder geclusterte Knoten und die Straße, keine Fremddaten. |
"""
)
st.caption("Die Standortplanungs-Linie ist damit vollständig: das Standortproblem ohne Kapazität als Wurzel, kapazitierte Standortplanung, p-Center, Standort mit Bestand, dieses Stück (Wettbewerb) und Hub-Standorte.")

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Spiel.** Knoten $V$, $|V|=n$, Nachfrage $w_j\in\mathbb N$, Abstände $d_{ij}$. Führer $L\subseteq V$ ($|L|=p$), Folger $F\subseteq V\setminus L$ ($|F|=r$). Mit $d_L(j)=\min_{i\in L}d_{ij}$ und $d_F(j)$ analog erobert der Folger
$$\Pi_F(L,F)=\sum_j w_j\Big(\mathbb 1[d_F(j)<d_L(j)]+\tfrac12\,\mathbb 1[d_F(j)=d_L(j)]\Big),$$
der Führer $W-\Pi_F$. Alle Anteile werden in Halbeinheiten gezählt (Ganzzahlen).

**Bestantwort und Führer-Optimum.** $F^*(L)\in\arg\max_F\Pi_F(L,F)$; der Führer maximiert $\Pi_L(L)=W-\max_F\Pi_F(L,F)$ (max-min, Stackelberg; das $(r|p)$-Centroid-Problem von Hakimi). Beide werden durch Aufzählung gelöst.

**Naiv, Greedy, Swap.** Naiv: $\arg\min_L\sum_jw_jd_L(j)$ (p-Median). Greedy: Standort für Standort gegen die exakte Antwort. Swap: ein Führerstandort gegen einen anderen Knoten, solange $\Pi_L$ steigt.

**Reines Gleichgewicht** ($p=r$): $(A,B)$ mit $B\in\arg\max_{B'}\Pi(A,B')$ und $A\in\arg\max_{A'}\Pi(B,A')$. Aufgezählt über die Matrix aller Antworten. **Abwechselnde Bestantworten:** jeder Spieler bleibt, wenn er schon eine Bestantwort hält, sonst wechselt er zur kleinsten Bestantwort; ein wiederkehrender Zustand heißt Zyklus.

Implementiert in `cmp_scenario.py` (Netze, Zufallsgenerator), `cmp_game.py` (Anteile, Bestantwort), `cmp_leader.py` (Führer-Verfahren), `cmp_equilibrium.py` (Gleichgewichte, Dynamik), `cmp_evaluation.py` (Vergleiche, Verteilungen, Raster).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
