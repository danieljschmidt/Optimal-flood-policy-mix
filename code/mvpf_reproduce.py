"""
Reproduce ALL tables and figures in notes/ for the flood-policy MVPF analysis.

    python code/mvpf_reproduce.py

Prints the tables that appear in `notes/mvpf_computations.md` (MVPF tables and the optimal
policy mix), and regenerates the figures (MCPF lambda = 1.2):
    notes/figures/                  discrete
    notes/figures_continuous/       continuous, CV = 0.86
    notes/figures_continuous_cv13/  continuous, CV = 1.3

Uses the two core modules plus mvpf_optimal_mix; this is the single, canonical entry point.
Runtime is dominated by the three phase diagrams (a 2-D optimisation per grid cell) — budget
~10-20 min depending on machine load. Lower the `ns`/grid sizes in figE() to speed it up.
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import mvpf_discrete as D
import mvpf_continuous as C
import mvpf_optimal_mix as A    # optimal_mix, welfare, cost

REPO  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD    = os.path.join(REPO, "notes", "figures")
FC    = os.path.join(REPO, "notes", "figures_continuous")
FC13  = os.path.join(REPO, "notes", "figures_continuous_cv13")
BLUE, RED = "#2166ac", "#b2182b"
LAM = 1.20                                  # G&S MCPF
M   = D.M_REF                               # mean belief 0.0114 = 0.57 p
SIG_LO, SIG_HI = D.sigma_of(M, 41), D.sigma_of(M, 15)   # empirical sigma_q band
NUS_TABLE = [5, 15, 25, 41, 100, 500]

# ---------------------------------------------------------------- tables
def tables(mod, name):
    st = mod.struct(mod.S0, mod.A0)
    print("=" * 78)
    print(f"  {name}   (mean m={M}, status quo s={mod.S0}, a={mod.A0}, MCPF lambda={LAM})")
    print("=" * 78)
    print(f"  structural (all nu):  q*={st['qst']:.5f}  Delta_u={st['Du']:.5f}")
    print(f"  {'nu':>5} {'sigma_q':>8} {'I':>6} {'MVPF_s':>7} {'MVPF_a':>7} {'ratio':>6}   optimal (s*,a*)")
    for nu in NUS_TABLE:
        I = mod.take_up(mod.S0, mod.A0, M, nu)
        Ms, Ma = mod.mvpf(mod.S0, mod.A0, M, nu)
        o = A.optimal_mix(mod, M, nu, lam=LAM, ns=101, na=101)
        reg = "relief-only" if o["s_star"] < 1e-3 else ("subsidy-only" if o["a_star"] < 1e-3 else "both")
        print(f"  {nu:5d} {mod.sigma_of(M, nu):8.4f} {I:6.3f} {Ms:7.3f} {Ma:7.3f} {Ma/Ms:6.2f}   "
              f"s*={o['s_star']:.2f} a*={o['a_star']:.2f} [{reg}]")
    print()

# ---------------------------------------------------------------- figures
def figBC(mod, outdir, tag):
    """MVPFs (left) and optimal mix (right) vs belief heterogeneity, at lambda=1.2."""
    os.makedirs(outdir, exist_ok=True)
    nus = np.logspace(np.log10(5), np.log10(200), 30)      # cap nu<=200: avoids MVPF_a denom pole
    sig = np.array([mod.sigma_of(M, nu) for nu in nus])
    Ms  = np.array([mod.mvpf(mod.S0, mod.A0, M, nu)[0] for nu in nus])
    Ma  = np.array([mod.mvpf(mod.S0, mod.A0, M, nu)[1] for nu in nus])
    oms = [A.optimal_mix(mod, M, nu, lam=LAM, ns=61, na=61) for nu in nus]
    ss  = np.array([o["s_star"] for o in oms]); aa = np.array([o["a_star"] for o in oms])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    ax[0].axvspan(SIG_LO, SIG_HI, color="0.85", label=r"empirical $\sigma_q$ (B–B)")
    ax[0].plot(sig, Ms, color=BLUE, lw=2.3, label=r"$\mathrm{MVPF}_s$ (subsidy)")
    ax[0].plot(sig, Ma, color=RED,  lw=2.3, label=r"$\mathrm{MVPF}_a$ (relief)")
    ax[0].axhline(LAM, color="green", ls=":", lw=1.2)
    ax[0].text(sig.min() * 1.05, LAM * 1.01, r"$\lambda=1.2$", color="green", fontsize=8)
    ax[0].set_xscale("log"); ax[0].set_xlabel(r"belief heterogeneity $\sigma_q$ (log)")
    ax[0].set_ylabel("MVPF"); ax[0].set_title("Relief has the higher MVPF throughout")
    ax[0].legend(frameon=False, fontsize=8, loc="upper right")
    ax[1].axvspan(SIG_LO, SIG_HI, color="0.85")
    ax[1].plot(sig, ss, color=BLUE, lw=2.3, marker="o", ms=3, label=r"$s^\ast$ (subsidy)")
    ax[1].plot(sig, aa, color=RED,  lw=2.3, marker="s", ms=3, label=r"$a^\ast$ (relief)")
    ax[1].set_xscale("log"); ax[1].set_xlabel(r"belief heterogeneity $\sigma_q$ (log)")
    ax[1].set_ylabel("optimal rate"); ax[1].set_ylim(-0.03, 1.0)
    ax[1].set_title(f"Optimal mix (MCPF $\\lambda={LAM}$) — relief-heavy")
    ax[1].legend(frameon=False, fontsize=9, loc="upper right")
    fig.suptitle(f"MVPFs and optimal mix vs belief heterogeneity  {tag}", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(f"{outdir}/figBC_optimalmix.png", dpi=150)
    plt.close(fig); print(f"  figBC  {tag}")

def figD(mod, outdir, tag):
    """Segmentation: which belief segment each instrument serves (lambda-independent)."""
    os.makedirs(outdir, exist_ok=True)
    QSTAR = mod.struct(mod.S0, mod.A0)["qst"]; q_un = mod.struct(0.999, mod.A0)["qst"]
    q = np.linspace(1e-4, 0.05, 800)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for k, (nu, ttl) in enumerate([(15, "High heterogeneity (empirical)"),
                                   (500, "Low heterogeneity (concentrated)")]):
        dens = mod.f_pdf(q, M, nu); ax[k].plot(q, dens, color="0.2", lw=1.6)
        ax[k].fill_between(q, dens, where=(q <= QSTAR), color=RED,  alpha=0.35, label="uninsured — relief")
        ax[k].fill_between(q, dens, where=(q > QSTAR),  color=BLUE, alpha=0.30, label="insured — subsidy")
        ax[k].axvline(QSTAR, color="k", lw=1, ls="--"); ax[k].axvline(mod.P, color="green", lw=1, ls=":")
        ax[k].axvspan(0, q_un, color=RED, alpha=0.15)
        ax[k].text(QSTAR * 1.05, ax[k].get_ylim()[1] * 0.9, r"$q^*$", fontsize=9)
        ax[k].set_title(ttl + f"\nunreachable tail $F(q^*_{{s=1}})={mod.f_cdf(q_un, M, nu):.2f}$", fontsize=10)
        ax[k].set_xlabel(r"subjective belief $q$"); ax[k].set_ylabel("density $f(q)$")
        ax[k].legend(frameon=False, fontsize=8, loc="upper right")
    fig.suptitle(f"Who each instrument reaches — relief serves the low-belief tail  {tag}", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(f"{outdir}/figD_segmentation.png", dpi=150)
    plt.close(fig); print(f"  figD   {tag}")

def figE(mod, outdir, tag):
    """Optimal-mix regime map over (mean underperception, sigma_q), at lambda=1.2."""
    os.makedirs(outdir, exist_ok=True)
    kk = np.linspace(0.2, 1.5, 28); ss = np.linspace(0.002, 0.055, 24)
    REG = np.full((len(ss), len(kk)), np.nan)
    for j, kfac in enumerate(kk):
        mj = kfac * mod.P
        for i, sg in enumerate(ss):
            nu = mod.nu_of_sigma(mj, sg)
            if nu <= 0.2:
                continue
            o = A.optimal_mix(mod, mj, nu, lam=LAM, ns=45, na=45)
            REG[i, j] = 0 if o["a_star"] < 1e-3 else (2 if o["s_star"] < 1e-3 else 1)
    fig, axe = plt.subplots(figsize=(7.4, 5.2))
    im = axe.pcolormesh(kk, ss, np.ma.masked_invalid(REG),
                        cmap=ListedColormap([BLUE, "#9970ab", RED]), vmin=-0.5, vmax=2.5, shading="auto")
    cb = fig.colorbar(im, ticks=[0, 1, 2]); cb.ax.set_yticklabels(["subsidy-only", "both", "relief-only"])
    axe.axhline(SIG_LO, color="k", ls="--", lw=1); axe.axhline(SIG_HI, color="k", ls="--", lw=1)
    axe.axvline(0.57, color="green", ls=":", lw=1.2)
    axe.text(0.59, ss.max() * 0.95, "our $m/p$", color="green", fontsize=8)
    axe.set_xlabel(r"mean underperception  $\mathbb{E}[q]/p$")
    axe.set_ylabel(r"belief heterogeneity  $\sigma_q$")
    axe.set_title(f"Optimal-mix regimes over the belief distribution (MCPF $\\lambda={LAM}$)\n{tag}", fontsize=10)
    fig.tight_layout(); fig.savefig(f"{outdir}/figE_phase.png", dpi=150); plt.close(fig)
    print(f"  figE   {tag}")

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    print("\n########## TABLES ##########\n")
    tables(D, "DISCRETE")
    tables(C, "CONTINUOUS  CV=0.86")

    print("\n########## FIGURES ##########\n")
    for mod, outdir, tag in [(D, FD, "[discrete]"), (C, FC, "[continuous, CV=0.86]")]:
        figBC(mod, outdir, tag); figD(mod, outdir, tag); figE(mod, outdir, tag)

    C.configure_damage(cv=1.3, dmax=0.9)                    # heavy-tail robustness
    print()
    tables(C, "CONTINUOUS  CV=1.3")
    figBC(C, FC13, "[continuous, CV=1.3]"); figD(C, FC13, "[continuous, CV=1.3]"); figE(C, FC13, "[continuous, CV=1.3]")
    C.configure_damage(alpha=1.0, beta=5.66667, dmax=1.0)   # reset to CV=0.86

    print("\nDONE. Figures in notes/figures{,_continuous,_continuous_cv13}/")
