"""Auswertungen: eine Analyse für das eingestellte Netz, Verteilungen über feste Netze und das Raster der Standortzahlen (p, r)."""

import statistics
from dataclasses import dataclass

import cmp_constants as C
import cmp_equilibrium as eq
import cmp_game as gm
import cmp_leader as ld
import cmp_scenario as sc


@dataclass(frozen=True)
class Params:
    kind: str = C.DEFAULT_NET
    n: int = C.DEFAULT_N
    p: int = C.DEFAULT_P
    r: int = C.DEFAULT_R
    seed: int = C.DEFAULT_SEED


def build(params, seed=None):
    net = sc.generate(params.n, params.kind, params.seed if seed is None else seed)
    return net, gm.Game(net)


def analyse(params, seed=None):
    """Alle Führer-Verfahren, das Führer-Optimum mit allen Werten und (bei p = r) die reinen Gleichgewichte samt Dynamik ab dem p-Median-Führer."""
    net, game = build(params, seed)
    p, r = params.p, params.r
    naive = ld.naive(game, p, r)
    best, values = ld.exact(game, p, r)
    gre = ld.greedy(game, p, r)
    swp = ld.swap(game, p, r, start=gre.sites)
    out = {"net": net, "game": game, "naive": naive, "greedy": gre, "swap": swp, "exact": best, "values": values}
    out["pct"] = {k: game.pct(v.value) for k, v in (("naive", naive), ("greedy", gre), ("swap", swp), ("exact", best))}
    out["random"] = game.pct(sum(int(v) for v in values) / len(values))
    out["worst"] = game.pct(int(values.min()))
    if p == r:
        out["nash"] = eq.nash_pairs(game, p)
        out["trace"], out["outcome"] = eq.dynamics(game, naive.sites, p)
    else:
        out["nash"], out["trace"], out["outcome"] = None, None, None
    return out


def try_sites(game, sites, r):
    """Der Führer wählt `sites` selbst: exakte Antwort des Folgers und die Anteile in Prozent (Führer, Folger)."""
    gain, reply = game.best_reply(sites, r)
    return {"reply": reply, "leader": game.pct(2 * game.total - gain), "follower": game.pct(gain)}


def one_net(params, seed):
    a = analyse(params, seed)
    row = {"seed": seed, **{k: a["pct"][k] for k in ("naive", "greedy", "swap", "exact")}, "random": a["random"], "worst": a["worst"]}
    row["naive_is_opt"] = a["naive"].value == a["exact"].value
    row["greedy_is_opt"] = a["greedy"].value == a["exact"].value
    row["swap_is_opt"] = a["swap"].value == a["exact"].value
    row["nash"] = None if a["nash"] is None else len(a["nash"])
    row["outcome"] = a["outcome"]
    return row


def summarize(rows):
    f = lambda k: statistics.fmean(r[k] for r in rows)
    s = {"count": len(rows), **{k: f(k) for k in ("naive", "greedy", "swap", "exact", "random", "worst")},
         "exact_min": min(r["exact"] for r in rows), "exact_max": max(r["exact"] for r in rows), "naive_min": min(r["naive"] for r in rows), "naive_max": max(r["naive"] for r in rows),
         "naive_is_opt": sum(r["naive_is_opt"] for r in rows), "greedy_is_opt": sum(r["greedy_is_opt"] for r in rows), "swap_is_opt": sum(r["swap_is_opt"] for r in rows),
         "gain": f("exact") - f("naive"), "swap_gap_max": max(r["exact"] - r["swap"] for r in rows), "greedy_gap_max": max(r["exact"] - r["greedy"] for r in rows),
         "leader_half": sum(1 for r in rows if r["exact"] >= 50 - 1e-9), "leader_majority": sum(1 for r in rows if r["exact"] > 50 + 1e-9)}
    if rows[0]["nash"] is not None:
        s["nash_nets"] = sum(1 for r in rows if r["nash"] > 0)
        s["nash_mean"] = statistics.fmean(r["nash"] for r in rows)
        s["nash_max"] = max(r["nash"] for r in rows)
        s["cycles"] = sum(1 for r in rows if r["outcome"] == "Zyklus")
        s["stable"] = sum(1 for r in rows if r["outcome"] == "Gleichgewicht")
    return s


def distribution(params, seeds=C.SWEEP_SEEDS):
    rows = [one_net(params, s) for s in seeds]
    return {"rows": rows, "summary": summarize(rows)}


def pr_grid(params, ps=C.GRID_P, rs=C.GRID_R, seeds=C.GRID_SEEDS):
    """Mittlerer Anteil des optimalen und des p-Median-Führers über feste Netze je (p, r)."""
    out = {}
    for p in ps:
        for r in rs:
            rows = [one_net(Params(params.kind, params.n, p, r, params.seed), s) for s in seeds]
            out[(p, r)] = {"exact": statistics.fmean(x["exact"] for x in rows), "naive": statistics.fmean(x["naive"] for x in rows)}
    return {"ps": tuple(ps), "rs": tuple(rs), "cells": out}
