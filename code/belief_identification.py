"""
Belief identification (decisions of 2026-08-12): sufficient statistics + Beta fit.

The LOCAL (headline) results need no belief distribution at all: `mvpf_local`
computes both MVPFs directly from the observed take-up I and premium elasticity
eps via the recovered density at the margin,
    f_hat = -eps * (I / pi) * (Delta_u / u'(c_I)),        pi = (1-s) p dbar.
The GLOBAL (secondary) results use `fit_beta`: the two Beta parameters are
exactly identified by the two moments (CDF at q* = 1 - voluntary take-up,
pdf at q* = f_hat). A share PHI of households is mandated to insure
(`params.PHI`); the Beta describes beliefs of the voluntary segment.
Surveys are VALIDATION targets, not calibration inputs: `validation` reports the
fitted mean against Bakkensen-Barrage's k_R = 0.57 and the fitted low-belief
share against their "35% perceive a 10-year flood probability <= 5%".

Units convention ("Reading A", adopted 2026-11-07 in paper and code): eps is the
RELATIVE elasticity of total take-up, eps = d ln I / d ln pi. A within-policy
renewal coefficient d Pr(renew)/d ln P (G&S) equals this under the threshold
model, since Pr(renew) = I(pi')/I(pi). Baseline eps = -0.25 (SFHA: G&S subsample
and Wagner 2022); robustness bounds -0.177 (Mulder) and -0.32 (G&S, all zones).
TODO: run Mulder's information effect (+17-30pp) as the over-identification test.

All functions take a core model module (`mvpf_discrete` or `mvpf_continuous`)
as their first argument, like `mvpf_optimal_mix`.
"""
import numpy as np
from scipy.optimize import brentq, fsolve
from scipy.special import betainc, betaln

Q10 = 1.0 - 0.95 ** 0.1   # annual belief whose 10-year flood probability is 5%


def premium(mod, s):
    return (1.0 - s) * mod.P * mod.MEAN_D


def recover_fqstar(mod, s, a, I, eps):
    """Belief density of the VOLUNTARY segment at the take-up margin implied by (I, eps).

    Total take-up I = PHI + (1-PHI)(1-F(q*)), so dI/dq* = -(1-PHI) f(q*); the
    observed response of total take-up therefore identifies (1-PHI) f(q*), and
    we divide by (1-PHI) to get f (paper eq. for f(q*) in sec. 3.6).
    """
    st = mod.struct(s, a)
    return -eps * (I / premium(mod, s)) * (st['Du'] / st['upI']) / (1 - mod.PHI)


def mvpf_local(mod, s, a, I, eps):
    """Sufficient-statistic MVPFs at (s, a): need only (I, eps), no belief Beta.

    PHI cancels: the (1-PHI) below undoes the division in `recover_fqstar`.
    """
    st = mod.struct(s, a)
    f = (1 - mod.PHI) * recover_fqstar(mod, s, a, I, eps)   # take-up density at the margin
    pd_ = mod.P * mod.MEAN_D
    dI_ds = f * pd_ * st['upI'] / st['Du']
    intern = (mod.P - st['qst']) * st['Du']
    if 'Dubar' in st:                                   # continuous damage
        dI_da = -f * st['qst'] * st['Dubar'] / st['Du']
        benefit_a = mod.P * st['Dubar']
        upUF_eff = st['upUF_eff']
    else:                                               # discrete damage
        dI_da = -f * st['qst'] * mod.D * st['upUF'] / st['Du']
        benefit_a = pd_ * st['upUF']
        upUF_eff = st['upUF']
    Ms = (intern * dI_ds + pd_ * st['upI'] * I) / (pd_ * I + pd_ * (s - a) * dI_ds)
    Ma = (intern * dI_da + benefit_a * (1 - I)) / (pd_ * (1 - I) + pd_ * (s - a) * dI_da)
    return Ms, Ma


def fit_beta(mod, s, a, I, eps):
    """Fit Beta(alpha, beta) to the two moments (take-up level, density at margin).

    The Beta is the belief distribution of the voluntary segment (share 1-PHI):
    solves  F_Beta(q*) = 1 - (I-PHI)/(1-PHI)  and  f_Beta(q*) = f_hat.
    Returns (alpha, beta). Raises if the solver does not converge or I <= PHI.
    """
    st = mod.struct(s, a)
    qst, fhat = st['qst'], recover_fqstar(mod, s, a, I, eps)
    if I <= mod.PHI:
        raise ValueError(f"take-up I={I} must exceed the mandated share PHI={mod.PHI}")
    I_vol = (I - mod.PHI) / (1 - mod.PHI)               # voluntary take-up

    def resid(x):
        al, be = np.exp(x)                              # positivity via log-params
        cdf = betainc(al, be, qst)
        pdf = np.exp((al - 1) * np.log(qst) + (be - 1) * np.log(1 - qst) - betaln(al, be))
        return [cdf - (1.0 - I_vol), pdf - fhat]

    x, info, ier, msg = fsolve(resid, [np.log(0.2), np.log(8.0)], full_output=True)
    if ier != 1 or max(abs(r) for r in resid(x)) > 1e-8:
        raise RuntimeError(f"Beta fit did not converge: {msg}")
    al, be = np.exp(x)
    return float(al), float(be)


def validation(mod, al, be):
    """Survey validation checks for a fitted Beta (surveys are NOT inputs).

    k_R check: fitted mean belief / p vs Bakkensen-Barrage's 0.57.
    Quantile check: fitted share with 10-yr belief <= 5% vs B-B's 0.35.
    """
    m = al / (al + be)
    return dict(
        mean_over_p=m / mod.P,                          # B-B k_R = 0.57
        share_10yr_below_5pct=float(betainc(al, be, Q10)),  # B-B: 0.35
        mass_below_p=float(betainc(al, be, mod.P)),
        median_over_p=brentq(lambda q: betainc(al, be, q) - 0.5, 1e-9, 0.9) / mod.P,
        m=m, nu=al + be,
    )


if __name__ == "__main__":
    import params
    import mvpf_discrete as D, mvpf_continuous as C
    print("belief_identification — sufficient statistics and Beta fit.")
    for mod, name in [(D, "discrete"), (C, "continuous")]:
        Ms, Ma = mvpf_local(mod, params.S0, params.A0, params.I_OBS, params.EPS)
        al, be = fit_beta(mod, params.S0, params.A0, params.I_OBS, params.EPS)
        v = validation(mod, al, be)
        print(f"  {name:10s}: local MVPF=({Ms:.3f},{Ma:.3f})  Beta({al:.3f},{be:.3f})"
              f"  m={v['m']:.4f} ({v['mean_over_p']:.2f}p)  nu={v['nu']:.2f}")
