"""
Plotting and table helpers for the baseline flood policy model.
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from dataclasses import replace
from scipy import optimize, stats
from typing import Tuple

from baseline_model import (
    Params, q_star,
    take_up, density_at_margin,
    welfare, fiscal_cost, mvpf_decompose,
    optimize_policy_numerical,
)


# ── Shared style constants ────────────────────────────────────────────────────

_COLORS = {
    "direct_benefit":     "#4878CF",
    "internality":        "#6ACC65",
    "direct_cost":        "#D65F5F",
    "fiscal_externality": "#B47CC7",
}
_LABELS = {
    "direct_benefit":     "Direct benefit",
    "internality":        "Internality",
    "direct_cost":        "Direct cost",
    "fiscal_externality": "Fiscal externality",
}
_NUM_KEYS = ["direct_benefit", "internality"]
_DEN_KEYS = ["direct_cost",    "fiscal_externality"]


# ── Budget frontier helper ────────────────────────────────────────────────────

_A_MAX = 1.0 - 1e-4  # a=1 makes delta_u=0 → ZeroDivisionError in q_star; stay just below


def _budget_frontier(par: Params, B: float, n: int = 300) -> Tuple[np.ndarray, np.ndarray]:
    """Return (s_vals, a_vals) along the iso-budget curve fiscal_cost(s, a(s)) = B."""
    s_vals, a_vals = [], []
    for s in np.linspace(0.0, 1.0, n):
        def eq(a_val: float, _s=s) -> float:
            p_ = replace(par, s=float(_s), a=float(a_val))
            return fiscal_cost(p_, take_up(p_)) - B
        try:
            lo, hi = eq(0.0), eq(_A_MAX)
            if lo * hi <= 0.0:
                a_ = optimize.brentq(eq, 0.0, _A_MAX, xtol=1e-10)
                s_vals.append(float(s))
                a_vals.append(float(a_))
        except Exception:
            pass
    return np.array(s_vals), np.array(a_vals)


# ── Table ─────────────────────────────────────────────────────────────────────

def print_mvpf_table(par: Params, I: float, fqs: float) -> None:
    dec = mvpf_decompose(par, I, fqs)
    print(f"{'':30s}  {'Subsidy s':>12}  {'Relief a':>12}")
    print("-" * 58)
    for key, label in [("direct_benefit", "Direct benefit"),
                       ("internality",    "Internality correction")]:
        print(f"  {label:28s}  {dec['s'][key]:+12.6f}  {dec['a'][key]:+12.6f}")
    print(f"  {'Numerator (total)':28s}  "
          f"{dec['s']['direct_benefit']+dec['s']['internality']:+12.6f}  "
          f"{dec['a']['direct_benefit']+dec['a']['internality']:+12.6f}")
    print()
    for key, label in [("direct_cost",       "Direct cost"),
                       ("fiscal_externality", "Fiscal externality")]:
        print(f"  {label:28s}  {dec['s'][key]:+12.6f}  {dec['a'][key]:+12.6f}")
    print(f"  {'Denominator (total)':28s}  "
          f"{dec['s']['direct_cost']+dec['s']['fiscal_externality']:+12.6f}  "
          f"{dec['a']['direct_cost']+dec['a']['fiscal_externality']:+12.6f}")
    print("-" * 58)
    print(f"  {'MVPF':28s}  {dec['s']['mvpf']:+12.4f}  {dec['a']['mvpf']:+12.4f}")


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_beta(par: Params, ax=None) -> plt.Figure:
    """Calibrated belief distribution with q* and p marked."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))
    else:
        fig = ax.get_figure()

    q_max  = min(0.05, par.p * 5)
    q_grid = np.linspace(0, q_max, 500)
    pdf    = stats.beta.pdf(q_grid, par.alpha, par.beta_)
    qs     = q_star(par)

    ax.plot(q_grid, pdf, color="black", lw=1.5)
    ax.axvline(qs,    color="black", lw=1, ls="--")
    ax.axvline(par.p, color="grey",  lw=1, ls=":")
    ylim = ax.get_ylim()
    ax.text(qs    + q_max * 0.01, ylim[1] * 0.95, r"$q^*$", ha="left", fontsize=11)
    ax.text(par.p + q_max * 0.01, ylim[1] * 0.80, r"$p$",   ha="left", fontsize=11, color="grey")
    ax.set_xlabel("Subjective flood probability $q$")
    ax.set_ylabel("Density")
    ax.set_title(rf"Belief distribution  Beta($\alpha$={par.alpha:.2f}, $\beta$={par.beta_:.2f})")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    return fig


def plot_mvpf_decomp(par: Params, I: float, fqs: float) -> plt.Figure:
    """Stacked-bar MVPF decomposition for subsidy and relief at a single policy."""
    dec = mvpf_decompose(par, I, fqs)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5), sharey=True)

    for inst, title, ax in [("s", "Subsidy  $s$", axes[0]),
                             ("a", "Relief  $a$",  axes[1])]:
        d = dec[inst]
        for xi, gkeys in enumerate([_NUM_KEYS, _DEN_KEYS]):
            bottom_pos = bottom_neg = 0.0
            for k in gkeys:
                val = d[k]
                bot = bottom_pos if val >= 0 else bottom_neg
                ax.bar(xi, val, bottom=bot, color=_COLORS[k],
                       width=0.5, edgecolor="white", linewidth=0.5)
                if val >= 0:
                    bottom_pos += val
                else:
                    bottom_neg += val
            total = sum(d[k] for k in gkeys)
            ax.scatter(xi, total, marker="D", color="black", zorder=5, s=45,
                       label="Total" if xi == 0 else "_")
        ax.axhline(0, color="black", lw=0.8)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Numerator", "Denominator"])
        ax.set_title(f"{title}\n(MVPF = {d['mvpf']:.3f})", fontsize=11)
        ax.set_ylabel("Value")

    legend_handles = [
        mpatches.Patch(color=_COLORS[k], label=_LABELS[k])
        for k in [*_NUM_KEYS, *_DEN_KEYS]
    ] + [plt.Line2D([0], [0], marker="D", color="black", ls="none",
                    markersize=7, label="Total")]
    fig.legend(handles=legend_handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.08), fontsize=9, frameon=False)
    fig.suptitle("MVPF decomposition at current policy", fontsize=12, y=1.01)
    fig.tight_layout()
    return fig


def plot_welfare_frontier(par: Params, B: float, n: int = 300) -> plt.Figure:
    """Welfare along the iso-budget frontier, with the optimal policy marked."""
    s_arr, a_arr = _budget_frontier(par, B, n)
    W = np.array([
        welfare(replace(par, s=float(s), a=float(a)),
                take_up(replace(par, s=float(s), a=float(a))))
        for s, a in zip(s_arr, a_arr)
    ])
    s_star, a_star = optimize_policy_numerical(par, B)
    par_opt = replace(par, s=s_star, a=a_star)
    W_star  = welfare(par_opt, take_up(par_opt))

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(s_arr, W, color="black", lw=1.5)
    ax.axvline(s_star, color="grey", lw=1, ls="--")
    ax.scatter([s_star], [W_star], color="black", zorder=5, s=60, marker="D",
               label=f"Optimum  $s^*={s_star:.3f}$, $a^*={a_star:.3f}$")
    ax.set_xlabel("Subsidy rate $s$  (relief $a$ adjusts to hold budget $B$ fixed)")
    ax.set_ylabel("Social welfare")
    ax.set_title("Welfare along iso-budget frontier")
    ax.legend(fontsize=10)
    fig.tight_layout()
    return fig


def plot_mvpf_frontier(par: Params, B: float, n: int = 300) -> plt.Figure:
    """
    Three-panel figure along the iso-budget frontier:
      top          — MVPF_s and MVPF_a (crossing = optimum)
      bottom-left  — MVPF component values for subsidy s
      bottom-right — MVPF component values for relief a
    """
    s_arr, a_arr = _budget_frontier(par, B, n)
    dec_list = []
    for s, a in zip(s_arr, a_arr):
        p_   = replace(par, s=float(s), a=float(a))
        I_   = take_up(p_)
        fqs_ = density_at_margin(p_)
        dec_list.append(mvpf_decompose(p_, I_, fqs_))

    mvpf_s = np.array([d["s"]["mvpf"] for d in dec_list])
    mvpf_a = np.array([d["a"]["mvpf"] for d in dec_list])
    s_star, a_star = optimize_policy_numerical(par, B)

    fig = plt.figure(figsize=(11, 8))
    gs  = gridspec.GridSpec(2, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    ax1.plot(s_arr, mvpf_s, color="#4878CF", lw=1.5, label=r"$\mathrm{MVPF}_s$")
    ax1.plot(s_arr, mvpf_a, color="#D65F5F", lw=1.5, label=r"$\mathrm{MVPF}_a$")
    ax1.axvline(s_star, color="grey", lw=1, ls="--",
                label=f"Optimum  $s^*={s_star:.3f}$, $a^*={a_star:.3f}$")
    ax1.set_ylabel("MVPF")
    ax1.set_title("MVPFs along iso-budget frontier")
    ax1.legend(fontsize=10)

    for ax, inst, title in [(ax2, "s", "Subsidy $s$"), (ax3, "a", "Relief $a$")]:
        for k in [*_NUM_KEYS, *_DEN_KEYS]:
            vals = np.array([d[inst][k] for d in dec_list])
            ax.plot(s_arr, vals, color=_COLORS[k], lw=1.5, label=_LABELS[k])
        ax.axvline(s_star, color="grey", lw=1, ls="--")
        ax.axhline(0, color="black", lw=0.5)
        ax.set_xlabel("Subsidy rate $s$")
        ax.set_ylabel("Component value")
        ax.set_title(f"MVPF components — {title}")
        ax.legend(fontsize=8)

    fig.tight_layout(h_pad=3.0)
    return fig
