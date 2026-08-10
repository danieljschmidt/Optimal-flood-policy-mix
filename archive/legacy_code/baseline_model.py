"""
Baseline one-region flood policy model (draft/draft.tex).

Calibration workflow:
  1. Build Params with structural parameters and current policy (s, a).
  2. Call calibrate() to fit the Beta belief distribution.
  3. Use mvpf_decompose() for local policy evaluation or
     optimize_policy_*() for global optimisation.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, replace
from scipy import optimize, stats
from typing import Optional, Tuple


# ── Parameters ────────────────────────────────────────────────────────────────

@dataclass
class Params:
    gamma: float = 2.0          # CRRA coefficient
    w: float = 1.0              # household wealth (normalised to 1)
    p: float = 0.01             # true flood probability (SFHA threshold)
    d: float = 0.15             # avg damage as share of house value (NFIP)
    s: float = 0.0              # insurance subsidy rate
    a: float = 0.0              # disaster relief fraction
    alpha: Optional[float] = None
    beta_: Optional[float] = None   # named beta_ to avoid shadowing scipy.stats.beta


# ── Utility (CRRA) ────────────────────────────────────────────────────────────

def u(c: float, gamma: float) -> float:
    return float(np.log(c)) if gamma == 1.0 else float(c ** (1.0 - gamma) / (1.0 - gamma))


def u_prime(c: float, gamma: float) -> float:
    return float(c ** (-gamma))


# ── Consumption levels ────────────────────────────────────────────────────────

def c_I(par: Params) -> float:
    return par.w - (1.0 - par.s) * par.p * par.d


def c_UN(par: Params) -> float:
    return par.w


def c_UF(par: Params) -> float:
    return par.w - (1.0 - par.a) * par.d


# ── Structural quantities ─────────────────────────────────────────────────────

def delta_u(par: Params) -> float:
    return u(c_UN(par), par.gamma) - u(c_UF(par), par.gamma)


def q_star(par: Params) -> float:
    return (u(c_UN(par), par.gamma) - u(c_I(par), par.gamma)) / delta_u(par)


def premium(par: Params) -> float:
    return (1.0 - par.s) * par.p * par.d


def value_insured(par: Params) -> float:
    return u(c_I(par), par.gamma)


def value_uninsured(par: Params) -> float:
    return u(c_UN(par), par.gamma) - par.p * delta_u(par)


def internality(par: Params) -> float:
    """V_I - V_U = (p - q*) · Δu."""
    return (par.p - q_star(par)) * delta_u(par)


def welfare(par: Params, I: float) -> float:
    return value_insured(par) * I + value_uninsured(par) * (1.0 - I)


def fiscal_cost(par: Params, I: float) -> float:
    return par.p * par.d * (par.s * I + par.a * (1.0 - I))


# ── Belief distribution ───────────────────────────────────────────────────────

def _check_beta(par: Params) -> None:
    if par.alpha is None or par.beta_ is None:
        raise ValueError("alpha and beta_ not set — call calibrate() first.")


def take_up(par: Params) -> float:
    _check_beta(par)
    return float(1.0 - stats.beta.cdf(q_star(par), par.alpha, par.beta_))


def density_at_margin(par: Params) -> float:
    _check_beta(par)
    return float(stats.beta.pdf(q_star(par), par.alpha, par.beta_))


# ── Take-up responses ─────────────────────────────────────────────────────────

def dI_ds(par: Params, fqs: Optional[float] = None) -> float:
    if fqs is None:
        fqs = density_at_margin(par)
    return fqs * par.p * par.d * u_prime(c_I(par), par.gamma) / delta_u(par)


def dI_da(par: Params, fqs: Optional[float] = None) -> float:
    if fqs is None:
        fqs = density_at_margin(par)
    return -fqs * q_star(par) * par.d * u_prime(c_UF(par), par.gamma) / delta_u(par)


# ── MVPF ─────────────────────────────────────────────────────────────────────

def mvpf_decompose(par: Params, I: float, fqs: float) -> dict:
    """
    Decompose MVPF_s and MVPF_a into their four components (eqs. mvpf_s_vf,
    mvpf_a_vf in draft). Returns {'s': {...}, 'a': {...}}, each sub-dict with
    keys direct_benefit, internality, direct_cost, fiscal_externality, mvpf.
    """
    du    = delta_u(par)
    qs    = q_star(par)
    up_I  = u_prime(c_I(par),  par.gamma)
    up_UF = u_prime(c_UF(par), par.gamma)
    gap   = (par.p - qs) * du      # V_I - V_U
    pd    = par.p * par.d
    sa    = par.s - par.a

    dIds = fqs * pd * up_I / du
    dIda = -fqs * qs * par.d * up_UF / du

    def _pack(db, intr, dc, fe):
        return {"direct_benefit": db, "internality": intr,
                "direct_cost": dc, "fiscal_externality": fe,
                "mvpf": (db + intr) / (dc + fe)}

    return {
        "s": _pack(pd * up_I  * I,       gap * dIds,  pd * I,        pd * sa * dIds),
        "a": _pack(pd * up_UF * (1 - I), gap * dIda,  pd * (1 - I),  pd * sa * dIda),
    }


def mvpf_subsidy(par: Params, I: float, fqs: float) -> float:
    return mvpf_decompose(par, I, fqs)["s"]["mvpf"]


def mvpf_relief(par: Params, I: float, fqs: float) -> float:
    return mvpf_decompose(par, I, fqs)["a"]["mvpf"]


# ── Calibration ───────────────────────────────────────────────────────────────

def recover_fqstar(I: float, epsilon: float, par: Params) -> float:
    return -epsilon * (I / premium(par)) * (delta_u(par) / u_prime(c_I(par), par.gamma))


def fit_beta(I: float, epsilon: float, par: Params) -> Tuple[float, float]:
    """
    Fit Beta(α, β) to simultaneously match observed take-up I and elasticity
    epsilon by solving the system (eqs. beta_cdf, beta_pdf in draft):
        F_Beta(q*; α, β) = 1 - I
        f_Beta(q*; α, β) = f_hat
    """
    qs    = q_star(par)
    f_hat = recover_fqstar(I, epsilon, par)

    def residuals(x: np.ndarray) -> np.ndarray:
        a_, b_ = x
        if a_ <= 0.0 or b_ <= 0.0:
            return np.array([1e10, 1e10])
        return np.array([
            float(stats.beta.cdf(qs, a_, b_)) - (1.0 - I),
            float(stats.beta.pdf(qs, a_, b_)) - f_hat,
        ])

    # Coarse grid search for a robust starting point
    grid = np.linspace(0.5, 20.0, 30)
    best_x0, best_norm = np.array([2.0, 2.0]), np.inf
    for a0 in grid:
        for b0 in grid:
            n = float(np.linalg.norm(residuals(np.array([a0, b0]))))
            if n < best_norm:
                best_norm, best_x0 = n, np.array([a0, b0])

    sol = optimize.fsolve(residuals, best_x0, full_output=True)
    alpha_hat, beta_hat = sol[0]

    if not np.allclose(residuals(sol[0]), 0.0, atol=1e-8):
        raise RuntimeError(f"Beta fitting did not converge. Residuals: {residuals(sol[0])}")
    if alpha_hat <= 0.0 or beta_hat <= 0.0:
        raise RuntimeError(f"Invalid Beta parameters: α={alpha_hat:.4f}, β={beta_hat:.4f}")

    return float(alpha_hat), float(beta_hat)


def calibrate(d: float, p: float, I_obs: float, epsilon: float,
              s: float, a: float, gamma: float = 2.0, w: float = 1.0) -> Params:
    """Return fully calibrated Params with Beta distribution fitted to (I_obs, epsilon)."""
    par = Params(gamma=gamma, w=w, p=p, d=d, s=s, a=a)
    alpha, beta_ = fit_beta(I_obs, epsilon, par)
    return replace(par, alpha=alpha, beta_=beta_)


# ── Policy optimisation ───────────────────────────────────────────────────────

def optimize_policy_numerical(par: Params, B: float) -> Tuple[float, float]:
    """Maximise welfare subject to fiscal_cost = B using SLSQP."""
    _check_beta(par)

    def neg_welfare(x: np.ndarray) -> float:
        p_ = replace(par, s=float(x[0]), a=float(x[1]))
        return -welfare(p_, take_up(p_))

    def budget_eq(x: np.ndarray) -> float:
        p_ = replace(par, s=float(x[0]), a=float(x[1]))
        return fiscal_cost(p_, take_up(p_)) - B

    result = optimize.minimize(
        neg_welfare, x0=np.array([0.1, 0.05]), method="SLSQP",
        bounds=[(0.0, 1.0), (0.0, 1.0)],
        constraints=[{"type": "eq", "fun": budget_eq}],
        options={"ftol": 1e-12, "maxiter": 1000},
    )
    if not result.success:
        raise RuntimeError(f"Numerical optimisation did not converge: {result.message}")
    return float(result.x[0]), float(result.x[1])


def optimize_policy_mvpf(par: Params, B: float) -> Tuple[float, float]:
    """Find (s*, a*) from MVPF_s = MVPF_a and fiscal_cost = B using fsolve."""
    _check_beta(par)

    def system(x: np.ndarray) -> np.ndarray:
        p_  = replace(par, s=float(x[0]), a=float(x[1]))
        I   = take_up(p_)
        dec = mvpf_decompose(p_, I, density_at_margin(p_))
        return np.array([dec["s"]["mvpf"] - dec["a"]["mvpf"], fiscal_cost(p_, I) - B])

    sol = optimize.fsolve(system, np.array([0.1, 0.05]), full_output=True)
    if not np.allclose(system(sol[0]), 0.0, atol=1e-8):
        raise RuntimeError(f"MVPF optimisation did not converge. Residuals: {system(sol[0])}")
    return float(sol[0][0]), float(sol[0][1])
