"""
Continuous-damage flood-policy model — MVPF core.

Only the DAMAGE side changes vs the discrete module:
  * insured premium uses the mean:  c_I  = w - (1-s) p dbar
  * uninsured flood loss is random: c_UF = w - (1-a) D,   D ~ G
  * Delta_u(a) = u(w) - E[u(w-(1-a)D)]                    (Jensen: larger than discrete)
  * relief marginal-utility factor  u'(c_UF) -> Dubar(a)/dbar,  Dubar = E[D u'(c_UF)]
The belief distribution F(q) is unchanged; discrete = degenerate G at dbar.
G = right-skewed Beta on [0, DMAX] with mean dbar (CV set by `configure_damage`).

Provides structural objects, take-up, and the two MVPFs; functions are generic in
(m, nu) — the calibrated belief Beta comes from `belief_identification.fit_beta`
and the local MVPFs from `belief_identification.mvpf_local` (parameters:
`params.py`). The optimal-mix analysis (`mvpf_optimal_mix.py`) and the secondary
complementarity diagnostics (`mvpf_complementarity.py`, on the branch) build on
this core; see `notes/mvpf_computations.md`.
"""
import numpy as np
from scipy.special import betaln, betainc
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator

# ---------------- primitives (single source of truth: params.py) ---------------
from params import W, GAMMA, P, MEAN_D, S0, A0
DBAR = MEAN_D                 # mean damage (uniform name shared with the discrete module)

def u(c):  return c ** (1 - GAMMA) / (1 - GAMMA)
def up(c): return c ** (-GAMMA)

# ---------------- damage distribution G (configurable) ------------------------
# PLACEHOLDER: the Beta spec below (CV = 0.86 default, 1.3 robustness) stands in
# until the FEMA claims-based damage distribution arrives; swap via configure_damage.
# D = DMAX * B, with B ~ Beta(DMG_ALPHA, DMG_BETA) on [0,1], mean(D) = DBAR.
# DMAX caps damage below total wealth loss so CRRA marginal utility stays finite
# (needed once the tail is heavy: CV >= ~1.3). CV is scale-invariant, so the cap
# does not distort it.
DMAX = 1.0
DMG_ALPHA = 1.0
DMG_BETA = 5.66667
DMG_CV = None
_agrid = np.linspace(0.0, 0.985, 220)
_Eu_interp = None
_Du_interp = None

def _beta_from_mean_cv(mu, cv):
    nu = (1 - mu) / (mu * cv ** 2) - 1
    return mu * nu, (1 - mu) * nu

def g_pdf(b):                                     # pdf of B on [0,1]
    return np.exp((DMG_ALPHA - 1) * np.log(b) + (DMG_BETA - 1) * np.log(1 - b)
                  - betaln(DMG_ALPHA, DMG_BETA))

def _Eu_cUF(a):     # E[u(w-(1-a)D)],  D = DMAX*b
    return quad(lambda b: u(W - (1 - a) * DMAX * b) * g_pdf(b), 0, 1, limit=200)[0]
def _Dubar(a):      # E[D u'(w-(1-a)D)] = overline{Du'}
    return quad(lambda b: (DMAX * b) * up(W - (1 - a) * DMAX * b) * g_pdf(b), 0, 1, limit=200)[0]

def configure_damage(cv=None, dmax=1.0, alpha=None, beta=None):
    """Set the damage distribution and rebuild the a-interpolators.
    Either give cv (Beta pinned to mean DBAR, that CV) or explicit alpha,beta."""
    global DMAX, DMG_ALPHA, DMG_BETA, DMG_CV, _Eu_interp, _Du_interp
    DMAX = dmax
    muB = DBAR / DMAX
    if cv is not None:
        DMG_ALPHA, DMG_BETA = _beta_from_mean_cv(muB, cv)
    else:
        DMG_ALPHA, DMG_BETA = alpha, beta
    DMG_CV = np.sqrt((1 - muB) / (muB * (DMG_ALPHA + DMG_BETA + 1)))
    _Eu_interp = PchipInterpolator(_agrid, np.array([_Eu_cUF(a) for a in _agrid]))
    _Du_interp = PchipInterpolator(_agrid, np.array([_Dubar(a) for a in _agrid]))

def Eu_cUF(a): return _Eu_interp(a)
def Dubar(a):  return _Du_interp(a)

configure_damage(alpha=1.0, beta=5.66667, dmax=1.0)   # default: CV = 0.86, uncapped

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
    c_I = W - (1 - s) * P * DBAR
    Du = u(W) - Eu_cUF(a)                              # E[u]; Jensen => > discrete
    qst = (u(W) - u(c_I)) / Du
    return dict(c_I=c_I, Du=float(Du), qst=float(qst), upI=up(c_I),
                upUF_eff=float(Dubar(a) / DBAR),        # effective u' for relief numerator
                Dubar=float(Dubar(a)),
                V_I=u(c_I), V_U=(1 - P) * u(W) + P * float(Eu_cUF(a)))

def take_up(s, a, m, nu): return 1 - f_cdf(struct(s, a)['qst'], m, nu)

# ---------------- MVPFs (draft eqs. mvpf_s_cont / mvpf_a_cont) -----------------
def mvpf(s, a, m, nu):
    st = struct(s, a); qst, Du, pdb = st['qst'], st['Du'], P * DBAR
    I, f = 1 - f_cdf(qst, m, nu), f_pdf(qst, m, nu)
    dI_ds = f * pdb * st['upI'] / Du
    dI_da = -f * qst * st['Dubar'] / Du                # -f q* overline{Du'}/Du
    intern = (P - qst) * Du
    Ms = (intern * dI_ds + pdb * st['upI'] * I) / (pdb * I + pdb * (s - a) * dI_ds)
    Ma = (intern * dI_da + P * st['Dubar'] * (1 - I)) / (pdb * (1 - I) + pdb * (s - a) * dI_da)
    return Ms, Ma

if __name__ == "__main__":
    import params, belief_identification as B
    import mvpf_continuous as _self
    print("mvpf_continuous — MVPF core module.")
    print(f"Damage G = Beta({DMG_ALPHA}, {DMG_BETA:.3f}), mean={DBAR}, CV={DMG_CV:.3f}")
    Ms, Ma = B.mvpf_local(_self, S0, A0, params.I_OBS, params.EPS)
    print(f"local MVPF = ({Ms:.3f}, {Ma:.3f})")

