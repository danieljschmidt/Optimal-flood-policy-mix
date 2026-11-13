"""
Single source of truth for the model calibration (decisions of 2026-08-12).

Every parameter used by the MVPF modules lives here; the core modules re-export
the names so `D.S0`, `C.MEAN_D` etc. still resolve. Documentation and provenance:
`notes/model_parameters.md`.
"""

# ---- structural primitives ---------------------------------------------------
W = 1.0            # household wealth (normalisation)
GAMMA = 1.5        # CRRA risk aversion (decision 2026-11-07, paper §4 "Utility"; was 2).
                   #   Between Chetty (2006): mean gamma ~ 1 from labour supply, and
                   #   Szpiro (1986): 1.2-1.8 for the US from aggregate property insurance
                   #   (usually 1-2 across countries). Not calibrated from insurance
                   #   choices: deductible/coverage choices imply triple-digit RRA under EU
                   #   (Sydnor 2010; Collier et al. 2017), better explained by probability
                   #   distortions (Barseghyan et al. 2013). Robustness: 1 and 3.
                   #   gamma = 1 uses log utility (handled in u()/up()).
P = 0.02           # true annual flood probability.
                   #   DISCUSSION POINT: round modelling choice, not estimated.
                   #   G&S report an implied p ~ 0.055 for the NFIP-insured population
                   #   (WP 35408, printed p. 31, p. 105). Population is now SFHA
                   #   homeowners: TODO recompute as claims per policy-year in A/V zones,
                   #   with the same claim filter as the damage distribution (paper: 0.019).
MEAN_D = 0.15      # (mean) flood damage as share of wealth (G&S L_f anchor).
                   #   Used by the DISCRETE model. The continuous model overrides
                   #   dbar with the empirical FEMA bin mean (0.3044 main / 0.2517
                   #   excl. Katrina) via configure_damage(empirical=...) — so the
                   #   two damage models are no longer mean-matched (caveat recorded
                   #   in notes/model_parameters.md 1b).

# ---- FEMA claims-based damage distribution (fema_data_analysis/) -------------
# 20-bin discretizations of D = buildingDamageAmount / buildingPropertyValue,
# single-family SFHA claims since 2000; see fema_data_analysis/notes/notes.md.
import os as _os
_FEMA_OUT = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                          "..", "fema_data_analysis", "output")
FEMA_DIST_MAIN = _os.path.join(_FEMA_OUT, "damage_distribution_main.csv")
FEMA_DIST_EXCL_KATRINA = _os.path.join(_FEMA_OUT, "damage_distribution_excl_katrina.csv")

# ---- utility base: HOME VALUE incl. land (decision 2026-11-07, paper §4) ---------
# Damage relative to home value = damage/structure value x (1 - FHFA land share)
# (Davis et al. 2019, FHFA WP 19-01), from the *_home variants of
# fema_data_analysis/run_compute_damage_distribution.py on branch TacoPrins-patch-3.
# Equivalent to an income base with pass-through MPC = income/home value ~ 0.25.
# TODO: these files do not exist yet (needs the branch merged and run on fema.db).
# Once they exist, load FEMA_DIST_MAIN_HOME in mvpf_continuous (and use
# FEMA_DIST_EXCL_KATRINA_HOME in mvpf_reproduce), and set MEAN_D for the discrete
# model to the home-value mean. Until then the code still uses building value.
FEMA_DIST_MAIN_HOME = _os.path.join(_FEMA_OUT, "damage_distribution_main_home.csv")
FEMA_DIST_EXCL_KATRINA_HOME = _os.path.join(_FEMA_OUT, "damage_distribution_excl_katrina_home.csv")

# ---- status-quo policy (evaluation point) ------------------------------------
S0 = 0.22          # insurance subsidy rate = 1 - premium paid / EXPECTED CLAIMS
                   #   (decision 2026-11-07, paper §4; was 0.47). G&S's 1 - 944/1739 =
                   #   0.46 is measured against the RR2.0 full-risk premium, which
                   #   includes a ~30% WYO expense allowance plus loss-adjustment,
                   #   reinsurance and risk loads (GAO-23-105977, pp. 6, 16, 18).
                   #   Netting out the expense allowance: 1 - 944/(0.70*1739) = 0.22
                   #   (an upper bound). Bounds: ~0 (incl. separate fees) and 0.46.
A0 = 0.052         # disaster-relief fraction (decision 2026-11-07, paper §4).
                   #   Bottom-up: flood share (48.9%) of IHP grants + SBA home loans at
                   #   subsidy-equivalent value (~$1.75bn/yr), over uninsured residential
                   #   flood damage (82% of ~$20bn/yr). Range 0.010-0.095; G&S-based 0.12
                   #   is the upper-bound robustness value. National rate, applied to the
                   #   SFHA population (assumes aid per uninsured dollar is similar there).
                   #   Derivation: notes/calibration_a_two_methods.md.

# ---- population: SFHA homeowners (decision 2026-11-07) -------------------------
I_OBS = 0.484      # take-up = share of expected damages insured, SFHA homeowners
                   #   (Amornsiripanitch et al. 2025, 2023 data; 59.5% hold some policy).
                   #   Includes mandated AND voluntary demand.
PHI = 0.32         # share mandated to insure (federally backed mortgage in SFHA):
                   #   0.39 (Mulder 2024 survey) x 0.484/0.595 (same coverage share as
                   #   voluntary buyers). Voluntary take-up (I-PHI)/(1-PHI) = 0.24.
                   #   Enters take-up I = PHI + (1-PHI)(1-F(q*)) and the belief fit; the
                   #   local (sufficient-statistic) MVPFs do not depend on it.
                   #   Verified in Mulder App. F (p. 74); his "54% of purchasers" is
                   #   39/72 with his own 72% take-up, not a separate figure.
EPS = -0.25        # premium elasticity of TOTAL take-up (mandated + voluntary),
                   #   relative: eps = (pi/I) dI/dpi (decision 2026-11-07, paper §3.6/§4).
                   #   SFHA estimates: G&S RR2.0 renewals, SFHA subsample (-0.25) and
                   #   Wagner 2022 (-0.25) agree. Robustness bounds: -0.177 (Mulder 2024)
                   #   and -0.32 (G&S, all zones). Was -0.32.
                   #   Implied voluntary elasticity: eps * I/(I-PHI) = -0.74.

# ---- welfare -----------------------------------------------------------------
LAM = 1.2          # MCPF for the fixed-lambda ROBUSTNESS check only. The baseline
                   # optimal mix holds the budget fixed at current spending
                   # (mvpf_optimal_mix.optimal_mix with lam=None), so lambda is the
                   # shadow value of that budget, not an input.
                   # report lam in {1.1, 1.2}; lam = 1.0 is degenerate (corner).
