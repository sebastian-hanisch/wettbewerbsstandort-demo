"""Plotly-Abbildungen: Karte mit Führer, Folger und der Aufteilung der Kunden, Anteile der Führer-Verfahren, Streudiagramm naiv gegen optimal, Wärmekarte über (p, r).
Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht zoomen. Karten haben gleichen Maßstab (scaleanchor) mit automatischem Bereich; der Rand kommt über zwei unsichtbare Punkte
(ein fest vorgegebener Bereich wird beim ersten Zeichnen in schmaler Breite eingefroren)."""

import plotly.graph_objects as go

import cmp_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_map(net, game, leader, follower=None, height=440):
    """Knoten (Farbe: geht zum Führer / zum Folger / geteilt, Größe nach Nachfrage) mit Linien zum nächsten Standort; Führerstandorte dunkelblau, Folgerstandorte dunkelrot (Quadrate mit Knotennummer)."""
    fig = go.Figure()
    owner = game.owner(leader, follower) if follower else None
    sites = list(leader) + (list(follower) if follower else [])
    site_of = lambda j, group: min(group, key=lambda i: (net.d[i][j], i))
    xs, ys = [], []
    for j in range(net.n):
        if j in sites:
            continue
        groups = [leader] if owner is None else ([leader] if owner[j] == 0 else [follower] if owner[j] == 1 else [leader, follower])
        for g in groups:
            i = site_of(j, g)
            xs += [net.pos[j][0], net.pos[i][0], None]
            ys += [net.pos[j][1], net.pos[i][1], None]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLORS["line"], width=1), hoverinfo="skip", showlegend=False))
    labels = (("geht zum Führer", 0, C.COLORS["leader"]), ("geht zum Folger", 1, C.COLORS["follower"]), ("geteilt", 2, C.COLORS["tie"]))
    if owner is None:
        rest = [j for j in range(net.n) if j not in sites]
        fig.add_trace(go.Scatter(x=[net.pos[j][0] for j in rest], y=[net.pos[j][1] for j in rest], mode="markers", name="Kunde", marker=dict(color="#7f8c8d", size=[6 + 2 * net.w[j] for j in rest], opacity=0.8),
                                 text=[f"{net.names[j]}: Nachfrage {net.w[j]}" for j in rest], hoverinfo="text"))
    else:
        for name, code, color in labels:
            nodes = [j for j in range(net.n) if j not in sites and owner[j] == code]
            if nodes:
                fig.add_trace(go.Scatter(x=[net.pos[j][0] for j in nodes], y=[net.pos[j][1] for j in nodes], mode="markers", name=name, marker=dict(color=color, size=[6 + 2 * net.w[j] for j in nodes], opacity=0.8),
                                         text=[f"{net.names[j]}: Nachfrage {net.w[j]}" for j in nodes], hoverinfo="text"))
    for group, name, color in ((leader, "Führer", C.COLORS["site_leader"]), (follower, "Folger", C.COLORS["site_follower"])):
        if group:
            fig.add_trace(go.Scatter(x=[net.pos[i][0] for i in group], y=[net.pos[i][1] for i in group], mode="markers+text", name=name,
                                     marker=dict(symbol="square", color=color, size=[14 + 2 * net.w[i] for i in group], line=dict(color="#111111", width=1)),
                                     text=[str(i + 1) for i in group], textposition="top center", textfont=dict(size=10), hovertext=[f"{net.names[i]} ({name}): Nachfrage {net.w[i]}" for i in group], hoverinfo="text"))
    pad = 6
    if net.kind == "street":
        fig.add_trace(go.Scatter(x=[-pad, 99 + pad], y=[25, 75], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    else:
        fig.add_trace(go.Scatter(x=[-pad, 99 + pad], y=[-pad, 99 + pad], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    return _base(fig, height if net.kind != "street" else min(height, 260))


def build_shares(rows, height=280):
    """Anteil des Führers nach der besten Antwort des Folgers je Verfahren. `rows`: [(Beschriftung, Prozent)]."""
    colors = [C.COLORS["leader"]] * len(rows)
    fig = go.Figure(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h", marker_color=colors, text=[f"{r[1]:.1f} %".replace(".", ",") for r in rows], textposition="outside",
                           hovertemplate="%{y}: %{x:.1f} %<extra></extra>"))
    fig.add_vline(x=50, line=dict(color="#111111", dash="dash"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(title="Anteil der Nachfrage, den der Führer nach der Antwort behält (%)", range=[0, 100])
    return _base(fig, height)


def build_scatter(rows, height=340):
    """Je Netz ein Punkt: Anteil des p-Median-Führers (x) gegen den optimalen Führer (y); auf der Diagonalen ist der p-Median-Führer optimal."""
    fig = go.Figure()
    lo = min(min(r["naive"] for r in rows), min(r["exact"] for r in rows)) - 2
    hi = max(max(r["naive"] for r in rows), max(r["exact"] for r in rows)) + 2
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color="#7f8c8d", dash="dot"), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[r["naive"] for r in rows], y=[r["exact"] for r in rows], mode="markers", name="Netz", marker=dict(color=C.COLORS["leader"], size=8, opacity=0.8),
                             text=[f"Seed {r['seed']}" for r in rows], hovertemplate="%{text}: p-Median %{x:.1f} %, optimal %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title="Anteil des p-Median-Führers (%)")
    fig.update_yaxes(title="Anteil des optimalen Führers (%)")
    return _base(fig, height)


def build_grid(grid, height=300):
    """Mittlerer Anteil des optimalen Führers je (Führer p, Folger r); Beschriftung: p-Median / optimal."""
    ps, rs = grid["ps"], grid["rs"]
    z = [[grid["cells"][(p, r)]["exact"] for r in rs] for p in ps]
    text = [[f"{grid['cells'][(p, r)]['naive']:.1f} / {grid['cells'][(p, r)]['exact']:.1f}".replace(".", ",") for r in rs] for p in ps]
    fig = go.Figure(go.Heatmap(x=[f"r = {r}" for r in rs], y=[f"p = {p}" for p in ps], z=z, text=text, texttemplate="%{text}", colorscale="RdBu", zmid=50, zmin=0, zmax=100,
                               hovertemplate="%{y}, %{x}: optimal %{z:.1f} %<extra></extra>", colorbar=dict(title="%", thickness=12)))
    fig.update_xaxes(title="Standorte des Folgers")
    fig.update_yaxes(title="Standorte des Führers", autorange="reversed")
    return _base(fig, height)
