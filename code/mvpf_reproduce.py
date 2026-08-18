"""
Reproduce ALL tables and figures in notes/ for the flood-policy MVPF analysis.

    python code/mvpf_reproduce.py

Structure:
  LOCAL  (headline)  — sufficient-statistic MVPFs from (I_OBS, EPS); no belief
                       distribution, no MCPF.
  GLOBAL (secondary) — belief Beta fitted to the same (I_OBS, EPS); survey
                       validation checks; optimal mix at lambda in {1.1, 1.2}.
                       Bounds/regions over the calibration set: TODO.

Figures (per damage spec):
    notes/figures/                            discrete
    notes/figures_continuous/                 continuous, FEMA empirical (main)
    notes/figures_continuous_excl_katrina/    continuous, FEMA excl. Katrina (robustness)
  figD  — segmentation: fitted belief density, who each instrument reaches
  figE  — optimal-mix regime map over the belief space (global robustness object)
(No sweep over the fitted belief parameters: (m, nu) are exactly identified by
(I_OBS, EPS), so sensitivity runs over the inputs — the bounds TODO.)

Runtime is dominated by the three phase diagrams — budget ~10-20 min.
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import params
import belief_identification as B
import mvpf_discrete as D
import mvpf_continuous as C
import mvpf_optimal_mix as A    # optimal_mix, welfare, cost

REPO  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD    = os.path.join(REPO, "notes", "figures")
FC    = os.path.join(REPO, "notes", "figures_continuous")
FCX   = os.path.join(REPO, "notes", "figures_continuous_excl_katrina")
BLUE, RED = "#2166ac", "#b2182b"
LAMS = [1.1, 1.2]                       # lambda = 1.0 is degenerate (corner: both -> max)

S0, A0, I_OBS, EPS = params.S0, params.A0, params.I_OBS, params.EPS


def calibrate(mod):
    """Fitted belief Beta + validation for a module in its current damage config."""
    al, be = B.fit_beta(mod, S0, A0, I_OBS, EPS)
    v = B.validation(mod, al, be)
    return dict(al=al, be=be, **v)


# ---------------------------------------------------------------- tables
def table_local(specs):
    print("=" * 78)
    print(f"  LOCAL (headline): sufficient-statistic MVPFs at status quo "
          f"(s={S0}, a={A0}; I={I_OBS}, eps={EPS})")
    print("=" * 78)
    print(f"  {'spec':22s} {'q*':>8} {'Delta_u':>8} {'f_hat':>7} {'MVPF_s':>7} {'MVPF_a':>7} {'ratio':>6}")
    for name, mod in specs:
        st = mod.struct(S0, A0)
        fhat = B.recover_fqstar(mod, S0, A0, I_OBS, EPS)
        Ms, Ma = B.mvpf_local(mod, S0, A0, I_OBS, EPS)
        print(f"  {name:22s} {st['qst']:8.5f} {st['Du']:8.5f} {fhat:7.3f} "
              f"{Ms:7.3f} {Ma:7.3f} {Ma/Ms:6.2f}")
    print()


def table_global(specs):
    print("=" * 78)
    print(f"  GLOBAL (secondary): fitted belief Beta + optimal mix   [bounds: TODO]")
    print("=" * 78)
    for name, mod in specs:
        cal = calibrate(mod)
        print(f"  {name}:  Beta(alpha={cal['al']:.4f}, beta={cal['be']:.4f})"
              f"   m={cal['m']:.5f} ({cal['mean_over_p']:.2f}p)   nu={cal['nu']:.2f}")
        print(f"    validation vs surveys (NOT calibration inputs):")
        print(f"      fitted mean/p = {cal['mean_over_p']:.2f}   (B-B k_R = 0.57)")
        print(f"      share 10yr-belief<=5% = {cal['share_10yr_below_5pct']:.2f}   (B-B: 0.35)")
        print(f"      mass below p = {cal['mass_below_p']:.2f}   median/p = {cal['median_over_p']:.3f}")
        for lam in LAMS:
            o = A.optimal_mix(mod, cal['m'], cal['nu'], lam=lam, ns=101, na=101)
            reg = ("relief-only" if o["s_star"] < 1e-3 else
                   "subsidy-only" if o["a_star"] < 1e-3 else "both")
            print(f"    optimal mix (lambda={lam}):  s*={o['s_star']:.2f}  a*={o['a_star']:.2f}  [{reg}]")
        print()


# ---------------------------------------------------------------- figures
def figD(mod, outdir, tag):
    """Segmentation at the FITTED belief distribution (lambda-independent)."""
    os.makedirs(outdir, exist_ok=True)
    cal = calibrate(mod)
    m, nu = cal['m'], cal['nu']
    QSTAR = mod.struct(S0, A0)["qst"]; q_un = mod.struct(0.999, A0)["qst"]
    q = np.linspace(1e-4, 0.05, 800)
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    dens = mod.f_pdf(q, m, nu); ax.plot(q, dens, color="0.2", lw=1.6)
    ax.fill_between(q, dens, where=(q <= QSTAR), color=RED,  alpha=0.35, label="uninsured — relief")
    ax.fill_between(q, dens, where=(q > QSTAR),  color=BLUE, alpha=0.30, label="insured — subsidy")
    ax.axvline(QSTAR, color="k", lw=1, ls="--"); ax.axvline(mod.P, color="green", lw=1, ls=":")
    ax.axvspan(0, q_un, color=RED, alpha=0.15)
    ax.text(QSTAR * 1.05, ax.get_ylim()[1] * 0.9, r"$q^*$", fontsize=9)
    ax.text(mod.P * 1.02, ax.get_ylim()[1] * 0.8, r"$p$", color="green", fontsize=9)
    ax.set_title(f"Fitted beliefs Beta({cal['al']:.2f}, {cal['be']:.1f}) — "
                 f"unreachable tail $F(q^*_{{s=1}})={mod.f_cdf(q_un, m, nu):.2f}$", fontsize=10)
    ax.set_xlabel(r"subjective belief $q$"); ax.set_ylabel("density $f(q)$")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.suptitle(f"Who each instrument reaches — relief serves the low-belief tail  {tag}",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(f"{outdir}/figD_segmentation.png", dpi=150)
    plt.close(fig); print(f"  figD   {tag}")


def figE(mod, outdir, tag):
    """Optimal-mix regime map over (mean underperception, sigma_q), at lambda=1.2."""
    os.makedirs(outdir, exist_ok=True)
    cal = calibrate(mod)
    kk = np.linspace(0.2, 1.5, 28); ss = np.linspace(0.002, 0.065, 26)
    REG = np.full((len(ss), len(kk)), np.nan)
    for j, kfac in enumerate(kk):
        mj = kfac * mod.P
        for i, sg in enumerate(ss):
            nu = mod.nu_of_sigma(mj, sg)
            if nu <= 0.2:
                continue
            o = A.optimal_mix(mod, mj, nu, lam=1.2, ns=45, na=45)
            REG[i, j] = 0 if o["a_star"] < 1e-3 else (2 if o["s_star"] < 1e-3 else 1)
    fig, axe = plt.subplots(figsize=(7.4, 5.2))
    im = axe.pcolormesh(kk, ss, np.ma.masked_invalid(REG),
                        cmap=ListedColormap([BLUE, "#9970ab", RED]), vmin=-0.5, vmax=2.5, shading="auto")
    cb = fig.colorbar(im, ticks=[0, 1, 2]); cb.ax.set_yticklabels(["subsidy-only", "both", "relief-only"])
    sig_fit = mod.sigma_of(cal['m'], cal['nu'])
    axe.plot(cal['mean_over_p'], sig_fit, marker="*", ms=16, mec="k", mfc="yellow", zorder=5)
    axe.text(cal['mean_over_p'] + 0.03, sig_fit, "fitted $F$", fontsize=8, va="center")
    axe.axvline(0.57, color="green", ls=":", lw=1.2)
    axe.text(0.585, ss.min() + 0.002, r"B–B $k_R$ (validation)", color="green", fontsize=8,
             bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1))
    axe.set_xlabel(r"mean underperception  $\mathbb{E}[q]/p$")
    axe.set_ylabel(r"belief heterogeneity  $\sigma_q$")
    axe.set_title(f"Optimal-mix regimes over the belief space (MCPF $\\lambda=1.2$)\n{tag}", fontsize=10)
    fig.tight_layout(); fig.savefig(f"{outdir}/figE_phase.png", dpi=150); plt.close(fig)
    print(f"  figE   {tag}")


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    print("\n########## TABLES ##########\n")
    C.configure_damage(empirical=params.FEMA_DIST_MAIN)         # FEMA baseline
    table_local([("DISCRETE", D), ("CONTINUOUS FEMA", C)])
    table_global([("DISCRETE", D), ("CONTINUOUS FEMA", C)])

    print("\n########## FIGURES ##########\n")
    for mod, outdir, tag in [(D, FD, "[discrete]"), (C, FC, "[continuous, FEMA]")]:
        figD(mod, outdir, tag); figE(mod, outdir, tag)

    C.configure_damage(empirical=params.FEMA_DIST_EXCL_KATRINA) # tail robustness
    print()
    table_local([("CONT. EXCL-KATRINA", C)])
    table_global([("CONT. EXCL-KATRINA", C)])
    figD(C, FCX, "[continuous, excl. Katrina]"); figE(C, FCX, "[continuous, excl. Katrina]")
    C.configure_damage(empirical=params.FEMA_DIST_MAIN)         # reset to FEMA baseline

    print("\nDONE. Figures in notes/figures{,_continuous,_continuous_excl_katrina}/")
