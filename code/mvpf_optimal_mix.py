"""
Optimal policy mix (s*, a*) — the headline policy result, built on the MVPF core.

Baseline (paper Sec. 3.3 / 4.2.3): the planner splits a FIXED budget B between the
subsidy s and disaster aid a; B defaults to current spending at (S0, A0). lambda is
then the shadow value of the budget, an outcome rather than an input.

Robustness: pass `lam` to fix the marginal cost of public funds instead and let total
spending adjust, (s*, a*) = argmax [S - lam * cost].

`welfare`, `cost`, and `optimal_mix` take the core model module `mod`
(`mvpf_discrete` or `mvpf_continuous`) as their first argument, so one implementation
serves both damage models. The MVPFs themselves live in the core (`mod.mvpf`).
"""
import numpy as np
from scipy.optimize import brentq

from params import S0, A0, LAM          # status quo; LAM = MCPF for the robustness check

# ---- welfare / cost -------------------------------------------------------------
# I = mod.take_up includes the mandated share PHI (paper eqs. welfare_prog / budget_prog).
def welfare(mod, s, a, m, nu):
    st = mod.struct(s, a); I = mod.take_up(s, a, m, nu)
    return st['V_I'] * I + st['V_U'] * (1 - I)

def cost(mod, s, a, m, nu):
    """Government spending p*dbar*[s I + a (1-I)] = the budget B in eq. budget_prog."""
    I = mod.take_up(s, a, m, nu)
    return mod.P * mod.MEAN_D * (s * I + a * (1 - I))

def current_budget(mod, m, nu, s0=S0, a0=A0):
    """B0: spending at current policy (at the fitted beliefs take_up(s0,a0) = I_OBS)."""
    return cost(mod, s0, a0, m, nu)

def aid_for_budget(mod, s, B, m, nu):
    """Aid rate a in [0, 1] that exhausts the budget B given s; None if infeasible."""
    g = lambda a: cost(mod, s, a, m, nu) - B
    if g(0.0) > 0:                       # s alone already exceeds the budget
        return None
    if g(1.0) < 0:                       # budget cannot be spent even with full aid
        return 1.0
    return brentq(g, 0.0, 1.0, xtol=1e-10)

# ---- optimal policy mix ----------------------------------------------------------
def optimal_mix(mod, m, nu, budget=None, lam=None, ns=141, na=141):
    """(s*, a*) at belief parameters (m, nu).

    lam is None  -> BASELINE: fixed budget (budget=None means current spending B0);
                    grid over s, a solved from the budget constraint.
    lam given    -> ROBUSTNESS: fixed MCPF, total spending free; grid over (s, a).
    Returns s*, a*, take-up I, q*/p (sign of the internality), the aid share of
    spending, and the welfare gain over the status quo (s0, a0) in utility units.
    """
    if lam is None:
        B = current_budget(mod, m, nu) if budget is None else budget
        best = None
        for s in np.linspace(0, 0.98, ns):
            a = aid_for_budget(mod, s, B, m, nu)
            if a is None:
                break                    # larger s is infeasible too (cost(s,0) rises in s)
            W = welfare(mod, s, a, m, nu)
            if best is None or W > best[0]:
                best = (W, s, a)
        W_star, s_star, a_star = best
        mode = f"fixed budget B={B:.3g}"
    else:
        s_grid, a_grid = np.linspace(0, 0.98, ns), np.linspace(0, 0.98, na)
        Wg = np.array([[welfare(mod, s, a, m, nu) - lam * cost(mod, s, a, m, nu)
                        for a in a_grid] for s in s_grid])
        i, j = np.unravel_index(np.argmax(Wg), Wg.shape)
        s_star, a_star = s_grid[i], a_grid[j]
        W_star = welfare(mod, s_star, a_star, m, nu)
        mode = f"fixed lambda={lam}"
    I = mod.take_up(s_star, a_star, m, nu)
    spend = max(s_star * I + a_star * (1 - I), 1e-12)
    return dict(s_star=s_star, a_star=a_star, I=I,
                qstar_over_p=mod.struct(s_star, a_star)['qst'] / mod.P,
                relief_share=a_star * (1 - I) / spend,
                welfare_gain=W_star - welfare(mod, S0, A0, m, nu),
                cost=cost(mod, s_star, a_star, m, nu), mode=mode)

def regime(o, tol=1e-3):
    return ("relief-only" if o["s_star"] < tol else
            "subsidy-only" if o["a_star"] < tol else "both")

if __name__ == "__main__":
    import params, belief_identification as B
    import mvpf_discrete as D, mvpf_continuous as C
    print("mvpf_optimal_mix — optimal policy mix at the fitted beliefs")
    for mod, name in [(D, "discrete"), (C, "continuous")]:
        al, be = B.fit_beta(mod, params.S0, params.A0, params.I_OBS, params.EPS)
        m, nu = al / (al + be), al + be
        o = optimal_mix(mod, m, nu, ns=99)
        print(f"  {name:11s} BASELINE  {o['mode']}: s*={o['s_star']:.2f} a*={o['a_star']:.3f} "
              f"[{regime(o)}]  I={o['I']:.3f}  q*/p={o['qstar_over_p']:.2f}  "
              f"aid share={o['relief_share']:.2f}  gain={o['welfare_gain']:.2e}")
        for lam in (1.1, LAM):
            o = optimal_mix(mod, m, nu, lam=lam, ns=99, na=99)
            print(f"  {name:11s} robustness {o['mode']}: s*={o['s_star']:.2f} a*={o['a_star']:.2f} "
                  f"[{regime(o)}]  q*/p={o['qstar_over_p']:.2f}")
    print("All tables and the figures: mvpf_reproduce.py")
