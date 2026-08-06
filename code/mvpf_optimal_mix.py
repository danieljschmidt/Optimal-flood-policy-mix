"""
Optimal policy mix (s*, a*) — the headline policy result, built on the MVPF core.

`welfare`, `cost`, and `optimal_mix` take the core model module `mod`
(`mvpf_discrete` or `mvpf_continuous`) as their first argument, so one implementation
serves both damage models. The MVPFs themselves live in the core (`mod.mvpf`); the
MCPF `lam` enters only the optimal mix. See `notes/mvpf_computations.md` §10.
"""
import numpy as np

LAM = 1.20                              # MCPF (G&S value)

# ---- welfare / cost (needed by the optimum) ----
def welfare(mod, s, a, m, nu):
    st = mod.struct(s, a); I = 1 - mod.f_cdf(st['qst'], m, nu)
    return st['V_I'] * I + st['V_U'] * (1 - I)

def cost(mod, s, a, m, nu):
    st = mod.struct(s, a); I = 1 - mod.f_cdf(st['qst'], m, nu)
    return mod.P * mod.MEAN_D * (s * I + a * (1 - I))

# ---- optimal policy mix (s*, a*) = argmax_{s,a} [ S - lam*cost ] ----
def optimal_mix(mod, m, nu, lam=LAM, ns=141, na=141):
    s_grid, a_grid = np.linspace(0, 0.98, ns), np.linspace(0, 0.98, na)
    Wg = np.array([[welfare(mod, s, a, m, nu) - lam * cost(mod, s, a, m, nu)
                    for a in a_grid] for s in s_grid])
    i, j = np.unravel_index(np.argmax(Wg), Wg.shape)
    s_star, a_star, W_both = s_grid[i], a_grid[j], Wg[i, j]
    W_sub = max(welfare(mod, s, 0, m, nu) - lam * cost(mod, s, 0, m, nu) for s in s_grid)
    W_rel = max(welfare(mod, 0, a, m, nu) - lam * cost(mod, 0, a, m, nu) for a in a_grid)
    I = mod.take_up(s_star, a_star, m, nu)
    denom = max(s_star * I + a_star * (1 - I), 1e-12)
    return dict(s_star=s_star, a_star=a_star, premium=W_both - max(W_sub, W_rel),
                relief_share=a_star * (1 - I) / denom)

if __name__ == "__main__":
    import mvpf_discrete as D, mvpf_continuous as C
    print(f"mvpf_optimal_mix — optimal policy mix (s*, a*) at MCPF lambda={LAM}, nu=25.")
    for mod, name in [(D, "discrete"), (C, "continuous")]:
        o = optimal_mix(mod, mod.M_REF, 25, lam=LAM, ns=101, na=101)
        reg = ("relief-only" if o["s_star"] < 1e-3 else
               "subsidy-only" if o["a_star"] < 1e-3 else "both")
        print(f"  {name:11s}: s*={o['s_star']:.2f}  a*={o['a_star']:.2f}  [{reg}]")
    print("Full sweep across nu and the figures: mvpf_reproduce.py")
