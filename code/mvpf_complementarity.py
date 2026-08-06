"""
Complements-vs-substitutes diagnostics (SECONDARY) — extends the MVPF core.

The headline result (relief-favored MVPFs and the optimal mix) lives in
`mvpf_optimal_mix.py` and `notes/mvpf_computations.md`. This module holds the demoted
complementarity diagnostics: the welfare cross-partial and the belief-density handles
behind the segmentation / incidence story. Each function takes the core model module
`mod` (`mvpf_discrete` or `mvpf_continuous`) as its first argument. Working notes:
`notes/mvpf_complementarity.md`.
"""
import numpy as np
from mvpf_optimal_mix import welfare

def cross_partial_S(mod, m, nu, s=None, a=None, h=1e-3):
    s = mod.S0 if s is None else s; a = mod.A0 if a is None else a
    return (welfare(mod, s + h, a + h, m, nu) - welfare(mod, s + h, a - h, m, nu)
            - welfare(mod, s - h, a + h, m, nu) + welfare(mod, s - h, a - h, m, nu)) / (4 * h * h)

def f_prime(mod, q, m, nu):             # analytic derivative of the belief Beta pdf
    al, be = mod.ab(m, nu)
    return mod.f_pdf(q, m, nu) * ((al - 1) / q - (be - 1) / (1 - q))

def beta_mode(mod, m, nu):
    al, be = mod.ab(m, nu)
    return (al - 1) / (al + be - 2) if al > 1 else 0.0

def driver(mod, m, nu, s=None, a=None):
    s = mod.S0 if s is None else s; a = mod.A0 if a is None else a
    qst = mod.struct(s, a)['qst']
    return (mod.P - qst) * f_prime(mod, qst, m, nu) - mod.f_pdf(qst, m, nu)

def unreachable_tail(mod, m, nu, a=None):
    """Mass below the threshold at a FREE subsidy (s->1): only relief reaches them."""
    a = mod.A0 if a is None else a
    return mod.f_cdf(mod.struct(0.999, a)['qst'], m, nu)
