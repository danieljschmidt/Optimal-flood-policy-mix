"""
Discrete-damage flood-policy model — MVPF core.

Household with wealth w faces a flood (prob p, damage d); subjective belief q ~ F.
Government subsidises insurance (rate s) and provides disaster relief (fraction a).
Belief distribution F = Beta parametrised by mean m and concentration nu:
    alpha = m*nu,  beta = (1-m)*nu,  sigma_q = sqrt(m(1-m)/(nu+1)).

Functions here are generic in (m, nu). The calibrated belief distribution is
fitted to (I_OBS, EPS) by `belief_identification.fit_beta`; the local MVPFs need
no belief distribution at all (`belief_identification.mvpf_local`). Parameters
live in `params.py`. MVPF formulas match draft.tex (value-function /
deep-parameter forms). The optimal-mix analysis (`mvpf_optimal_mix.py`) and the
secondary complementarity diagnostics (`mvpf_complementarity.py`, on the
`mvpf-complementarity` branch) build on this core; formulas and results:
`notes/mvpf_computations.md`.
"""
import numpy as np
from scipy.special import betaln, betainc

# ---------------- primitives (single source of truth: params.py) ---------------
from params import W, GAMMA, P, MEAN_D, S0, A0
D = MEAN_D                    # damage (= mean damage; = DBAR in the continuous module)

def u(c):  return c ** (1 - GAMMA) / (1 - GAMMA)
def up(c): return c ** (-GAMMA)

# ---------------- belief distribution: Beta by (mean, concentration) ----------
def ab(m, nu):         return m * nu, (1 - m) * nu
def sigma_of(m, nu):   return np.sqrt(m * (1 - m) / (nu + 1))
def nu_of_sigma(m, s): return m * (1 - m) / s ** 2 - 1
def f_pdf(q, m, nu):
    al, be = ab(m, nu)
    return np.exp((al - 1) * np.log(q) + (be - 1) * np.log(1 - q) - betaln(al, be))
def f_cdf(q, m, nu):
    al, be = ab(m, nu)
    return betainc(al, be, np.clip(q, 1e-12, 1 - 1e-12))

# ---------------- structural objects at (s,a) ---------------------------------
def struct(s, a):
    c_I, c_UN, c_UF = W - (1 - s) * P * D, W, W - (1 - a) * D
    Du = u(c_UN) - u(c_UF)
    qst = (u(c_UN) - u(c_I)) / Du
    return dict(c_I=c_I, c_UF=c_UF, Du=Du, qst=qst, upI=up(c_I), upUF=up(c_UF),
                V_I=u(c_I), V_U=(1 - P) * u(c_UN) + P * u(c_UF))

def take_up(s, a, m, nu): return 1 - f_cdf(struct(s, a)['qst'], m, nu)

# ---------------- MVPFs (draft eqs. mvpf_s_vf / mvpf_a_vf) ---------------------
def mvpf(s, a, m, nu):
    st = struct(s, a); qst, Du, pd = st['qst'], st['Du'], P * D
    I, f = 1 - f_cdf(qst, m, nu), f_pdf(qst, m, nu)
    dI_ds = f * pd * st['upI'] / Du
    dI_da = -f * qst * D * st['upUF'] / Du
    intern = (P - qst) * Du
    Ms = (intern * dI_ds + pd * st['upI'] * I) / (pd * I + pd * (s - a) * dI_ds)
    Ma = (intern * dI_da + pd * st['upUF'] * (1 - I)) / (pd * (1 - I) + pd * (s - a) * dI_da)
    return Ms, Ma

if __name__ == "__main__":
    import params, belief_identification as B
    import mvpf_discrete as _self
    print("mvpf_discrete — MVPF core module.")
    Ms, Ma = B.mvpf_local(_self, S0, A0, params.I_OBS, params.EPS)
    print(f"status-quo q* = {struct(S0, A0)['qst']:.5f}   "
          f"local MVPF = ({Ms:.3f}, {Ma:.3f})")
