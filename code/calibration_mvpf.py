"""
Compute MVPF_s and MVPF_a at current US flood policy parameters.

Empirical sources:
  I       = 0.30   FEMA NFIP penetration rate, high-risk areas
  epsilon = -0.17  price semi-elasticity of take-up (Mulder 2021)
  p       = 0.02   true flood probability (model calibration)
  s       = 0.47   current NFIP subsidy rate (GAO 2023)
  a       = 0.055  current relief fraction: avg FEMA IA grant / avg claim
  gamma   = 2.0    CRRA risk aversion (Chetty 2006)
  d/w     = 0.15   avg NFIP claim / avg home value (empirical)
  d/w     = 0.50   model calibration (for comparison)
"""

import numpy as np
from optimal_policy import u, u_prime, Parameters


def compute_mvpfs(s, a, I, epsilon, par):
    """
    Compute MVPF_s and MVPF_a at policy (s, a).

    Uses the ratio trick (eq. 7 in model notes) to recover dI/da from dI/ds.
    Assumes actuarially fair insurance: pi = p.
    """
    pd = par.p * par.d

    # Consumption levels
    c_I   = par.w - (1 - s) * pd
    c_U_N = par.w
    c_U_F = par.w - (1 - a) * par.d

    # Utility levels and gap
    Delta_u = u(c_U_N, par.gamma) - u(c_U_F, par.gamma)

    # Threshold belief q* (eq. 1)
    q_star = (u(c_U_N, par.gamma) - u(c_I, par.gamma)) / Delta_u

    # Internality correction: (p - q*) * Delta_u  (eq. 4)
    internality = (par.p - q_star) * Delta_u

    # Marginal utilities
    du_I   = u_prime(c_I, par.gamma)
    du_U_F = u_prime(c_U_F, par.gamma)

    # Behavioral responses
    dI_ds = -pd * I * epsilon                             # > 0 since epsilon < 0
    dI_da = -(q_star / par.p) * (du_U_F / du_I) * dI_ds  # < 0  (ratio trick, eq. 7)

    # Value functions (using true probability p)
    V_I = u(c_I, par.gamma)
    V_U = (1 - par.p) * u(c_U_N, par.gamma) + par.p * u(c_U_F, par.gamma)

    # MVPF_s  (eq. 5)
    num_s = internality * dI_ds + pd * du_I * I
    den_s = pd * I + pd * (s - a) * dI_ds
    MVPF_s = num_s / den_s

    # MVPF_a  (eq. 6)
    num_a = internality * dI_da + pd * du_U_F * (1 - I)
    den_a = pd * (1 - I) + pd * (s - a) * dI_da
    MVPF_a = num_a / den_a

    return dict(
        c_I=c_I, c_U_F=c_U_F,
        q_star=q_star, internality=internality,
        du_I=du_I, du_U_F=du_U_F,
        dI_ds=dI_ds, dI_da=dI_da,
        V_I=V_I, V_U=V_U,
        num_s=num_s, den_s=den_s, MVPF_s=MVPF_s,
        num_a=num_a, den_a=den_a, MVPF_a=MVPF_a,
    )


def print_results(label, res, s, a, p):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  c_I   = {res['c_I']:.5f}    c_U_F = {res['c_U_F']:.5f}")
    print(f"  q*    = {res['q_star']:.5f}    p     = {p:.5f}")
    print(f"  (p - q*) Δu = {res['internality']:.7f}")
    print(f"  u'(c_I)   = {res['du_I']:.5f}")
    print(f"  u'(c_U_F) = {res['du_U_F']:.5f}")
    print(f"  dI/ds = {res['dI_ds']:.7f}    dI/da = {res['dI_da']:.7f}")
    print(f"  V_I   = {res['V_I']:.6f}    V_U   = {res['V_U']:.6f}")
    print(f"  V_I - V_U = {res['V_I'] - res['V_U']:.7f}")
    print()
    print(f"  MVPF_s = {res['num_s']:.7f} / {res['den_s']:.7f} = {res['MVPF_s']:.4f}")
    print(f"  MVPF_a = {res['num_a']:.7f} / {res['den_a']:.7f} = {res['MVPF_a']:.4f}")
    if res['MVPF_a'] > res['MVPF_s']:
        print(f"\n  => MVPF_a > MVPF_s: marginal dollar should go to disaster relief")
    else:
        print(f"\n  => MVPF_s > MVPF_a: marginal dollar should go to insurance subsidy")


if __name__ == "__main__":

    # Shared policy and behavioral parameters
    s       = 0.47    # current NFIP subsidy rate (GAO 2023)
    a       = 0.055   # avg FEMA IA grant (~$3k) / avg claim (~$55k)
    I       = 0.30    # take-up rate in high-risk areas (FEMA)
    epsilon = -0.17   # semi-elasticity w.r.t. premium (Mulder 2021)
    p       = 0.02    # true flood probability
    gamma   = 2.0     # CRRA risk aversion (Chetty 2006)

    # Case 1: empirical damage-to-wealth ratio d/w = 0.15
    par_emp = Parameters(w=1.0, d=0.15, p=p, pi=p, gamma=gamma)
    res_emp = compute_mvpfs(s, a, I, epsilon, par_emp)
    print_results("Empirical calibration  (d/w = 0.15)", res_emp, s, a, p)

    # Case 2: model calibration d/w = 0.50
    par_mod = Parameters(w=1.0, d=0.50, p=p, pi=p, gamma=gamma)
    res_mod = compute_mvpfs(s, a, I, epsilon, par_mod)
    print_results("Model calibration      (d/w = 0.50)", res_mod, s, a, p)
