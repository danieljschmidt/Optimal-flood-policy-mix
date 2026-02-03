"""
Optimal Flood Insurance Policy Solver

Solves for optimal subsidy (s) and disaster relief (a) given:
- CRRA utility: u(c) = c^(1-γ) / (1-γ)
- Beta-distributed subjective beliefs: q ~ Beta(α, β)
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import beta
from dataclasses import dataclass


@dataclass
class Parameters:
    """Model parameters"""
    w: float = 100_000      # wealth
    d: float = 50_000       # flood damage
    p: float = 0.02         # true flood probability
    mu: float = 0.3         # insurance loading factor
    gamma: float = 2.0      # CRRA risk aversion
    B: float = 100          # government budget (per capita)
    alpha: float = 0.5      # Beta distribution parameter
    beta_param: float = 50.0  # Beta distribution parameter (mean ≈ α/(α+β))
    
    @property
    def pi(self):
        """Loaded insurance premium rate"""
        return (1 + self.mu) * self.p


def u(c, gamma):
    """CRRA utility function"""
    if gamma == 1:
        return np.log(np.maximum(c, 1e-10))
    return np.maximum(c, 1e-10) ** (1 - gamma) / (1 - gamma)


def u_prime(c, gamma):
    """Marginal utility"""
    return np.maximum(c, 1e-10) ** (-gamma)


def q_star(s, a, par):
    """Insurance purchase threshold"""
    c_ins = par.w - (1 - s) * par.pi * par.d
    c_unins_flood = par.w - (1 - a) * par.d
    
    num = u(par.w, par.gamma) - u(c_ins, par.gamma)
    denom = u(par.w, par.gamma) - u(c_unins_flood, par.gamma)
    
    if abs(denom) < 1e-12:
        return 0.5
    return np.clip(num / denom, 0.001, 0.999)


def V_ins(s, par):
    """Expected utility if insured"""
    c = par.w - (1 - s) * par.pi * par.d
    return u(c, par.gamma)


def V_unins(a, par):
    """True expected utility if uninsured"""
    return (1 - par.p) * u(par.w, par.gamma) + par.p * u(par.w - (1 - a) * par.d, par.gamma)


def dq_ds(s, a, par):
    """Derivative of threshold w.r.t. subsidy"""
    c_ins = par.w - (1 - s) * par.pi * par.d
    c_unins_flood = par.w - (1 - a) * par.d
    denom = u(par.w, par.gamma) - u(c_unins_flood, par.gamma)
    if abs(denom) < 1e-12:
        return 0.0
    return par.pi * par.d * u_prime(c_ins, par.gamma) / denom


def dq_da(s, a, par):
    """Derivative of threshold w.r.t. disaster relief"""
    q = q_star(s, a, par)
    c_unins_flood = par.w - (1 - a) * par.d
    denom = u(par.w, par.gamma) - u(c_unins_flood, par.gamma)
    if abs(denom) < 1e-12:
        return 0.0
    return q * par.d * u_prime(c_unins_flood, par.gamma) / denom


def dV_ins_ds(s, par):
    """Derivative of insured utility w.r.t. subsidy"""
    c = par.w - (1 - s) * par.pi * par.d
    return par.pi * par.d * u_prime(c, par.gamma)


def dV_unins_da(a, par):
    """Derivative of uninsured utility w.r.t. relief"""
    c = par.w - (1 - a) * par.d
    return par.p * par.d * u_prime(c, par.gamma)


def social_welfare(s, a, par):
    """Compute social welfare for given policy"""
    q = q_star(s, a, par)
    F_q = beta.cdf(q, par.alpha, par.beta_param)
    return V_unins(a, par) * F_q + V_ins(s, par) * (1 - F_q)


def budget_spent(s, a, par):
    """Compute budget expenditure"""
    q = q_star(s, a, par)
    F_q = beta.cdf(q, par.alpha, par.beta_param)
    return a * par.p * par.d * F_q + s * par.pi * par.d * (1 - F_q)


def solve_optimal_policy(par, x0=None):
    """Solve for optimal (s, a) using constrained optimization"""
    
    def neg_welfare(x):
        s, a = x
        return -social_welfare(s, a, par)
    
    def budget_constraint(x):
        s, a = x
        return par.B - budget_spent(s, a, par)
    
    if x0 is None:
        x0 = [0.3, 0.3]
    
    # Bounds: s and a in [0, 1]
    bounds = [(0.01, 0.99), (0.01, 0.99)]
    
    # Budget constraint: spending <= B
    constraints = {'type': 'eq', 'fun': budget_constraint}
    
    result = minimize(
        neg_welfare, x0, method='SLSQP',
        bounds=bounds, constraints=constraints,
        options={'ftol': 1e-10, 'maxiter': 1000}
    )
    
    s_opt, a_opt = result.x
    
    # Compute shadow value numerically
    eps = 1e-6
    par_plus = Parameters(
        w=par.w, d=par.d, p=par.p, mu=par.mu, gamma=par.gamma,
        B=par.B + eps, alpha=par.alpha, beta_param=par.beta_param
    )
    result_plus = minimize(
        lambda x: -social_welfare(x[0], x[1], par_plus),
        [s_opt, a_opt], method='SLSQP',
        bounds=bounds,
        constraints={'type': 'eq', 'fun': lambda x: par_plus.B - budget_spent(x[0], x[1], par_plus)}
    )
    welfare_plus = -result_plus.fun
    welfare_base = -result.fun
    lam_opt = (welfare_plus - welfare_base) / eps
    
    return s_opt, a_opt, lam_opt, result.success


def compute_outcomes(s, a, par):
    """Compute equilibrium outcomes"""
    q = q_star(s, a, par)
    F_q = beta.cdf(q, par.alpha, par.beta_param)
    
    welfare = V_unins(a, par) * F_q + V_ins(s, par) * (1 - F_q)
    spending = a * par.p * par.d * F_q + s * par.pi * par.d * (1 - F_q)
    
    return {
        'q_star': q,
        'frac_uninsured': F_q,
        'frac_insured': 1 - F_q,
        'welfare': welfare,
        'spending': spending,
        'mean_belief': par.alpha / (par.alpha + par.beta_param)
    }


def main():
    # Baseline parameters
    par = Parameters()
    
    print("=" * 60)
    print("OPTIMAL FLOOD INSURANCE POLICY")
    print("=" * 60)
    print(f"\nParameters:")
    print(f"  Wealth (w):           ${par.w:,.0f}")
    print(f"  Damage (d):           ${par.d:,.0f}")
    print(f"  True flood prob (p):  {par.p:.2%}")
    print(f"  Loading factor (μ):   {par.mu:.0%}")
    print(f"  Risk aversion (γ):    {par.gamma}")
    print(f"  Budget (B):           ${par.B:,.0f}")
    print(f"  Belief dist:          Beta({par.alpha}, {par.beta_param})")
    print(f"  Mean belief:          {par.alpha/(par.alpha+par.beta_param):.2%}")
    
    # Solve
    s_opt, a_opt, lam_opt, converged = solve_optimal_policy(par)
    outcomes = compute_outcomes(s_opt, a_opt, par)
    
    print(f"\n{'SOLUTION':=^60}")
    print(f"  Optimal subsidy (s):      {s_opt:.1%}")
    print(f"  Optimal relief (a):       {a_opt:.1%}")
    print(f"  Shadow value (λ):         {lam_opt:.6f}")
    print(f"  Converged:                {converged}")
    
    print(f"\n{'OUTCOMES':=^60}")
    print(f"  Insurance threshold (q*): {outcomes['q_star']:.2%}")
    print(f"  Fraction insured:         {outcomes['frac_insured']:.1%}")
    print(f"  Fraction uninsured:       {outcomes['frac_uninsured']:.1%}")
    print(f"  Social welfare:           {outcomes['welfare']:.6f}")
    print(f"  Total spending:           ${outcomes['spending']:.2f}")
    
    # Comparative statics
    print(f"\n{'COMPARATIVE STATICS':=^60}")
    
    # Vary risk aversion
    print("\nRisk aversion (γ):")
    print(f"  {'γ':>6} | {'s*':>8} | {'a*':>8} | {'Insured':>8}")
    print("-" * 40)
    for gamma in [1.5, 2.0, 3.0, 5.0]:
        par_temp = Parameters(gamma=gamma)
        s, a, _, conv = solve_optimal_policy(par_temp)
        out = compute_outcomes(s, a, par_temp)
        print(f"  {gamma:>6.1f} | {s:>7.1%} | {a:>7.1%} | {out['frac_insured']:>7.1%}")
    
    # Vary budget
    print("\nBudget (B):")
    print(f"  {'B':>8} | {'s*':>8} | {'a*':>8} | {'Welfare':>12}")
    print("-" * 45)
    for B in [50, 100, 200, 500]:
        par_temp = Parameters(B=B)
        s, a, _, conv = solve_optimal_policy(par_temp)
        out = compute_outcomes(s, a, par_temp)
        print(f"  ${B:>6} | {s:>7.1%} | {a:>7.1%} | {out['welfare']:>12.6f}")
    
    # Vary mean belief (via alpha)
    print("\nMean subjective belief:")
    print(f"  {'E[q]':>8} | {'s*':>8} | {'a*':>8} | {'Insured':>8}")
    print("-" * 40)
    for alpha in [0.1, 0.2, 0.5, 1.0]:
        par_temp = Parameters(alpha=alpha)  # beta_param=50, so mean = α/(α+50)
        mean_q = alpha / (alpha + par_temp.beta_param)
        s, a, _, conv = solve_optimal_policy(par_temp)
        out = compute_outcomes(s, a, par_temp)
        print(f"  {mean_q:>7.2%} | {s:>7.1%} | {a:>7.1%} | {out['frac_insured']:>7.1%}")


if __name__ == "__main__":
    main()