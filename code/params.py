"""
Single source of truth for the model calibration (decisions of 2026-08-12).

Every parameter used by the MVPF modules lives here; the core modules re-export
the names so `D.S0`, `C.MEAN_D` etc. still resolve. Documentation and provenance:
`notes/model_parameters.md`.
"""

# ---- structural primitives ---------------------------------------------------
W = 1.0            # household wealth (normalisation)
GAMMA = 2.0        # CRRA risk aversion (Chetty 2006)
P = 0.02           # true annual flood probability.
                   #   DISCUSSION POINT: round modelling choice, not estimated.
                   #   G&S report an implied p ~ 0.055 for the NFIP-insured population
                   #   (WP 35408, printed p. 31, p. 105). Population switch (SFHA "P1",
                   #   two-zone "P3") is an optional TODO.
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

# ---- status-quo policy (evaluation point) ------------------------------------
S0 = 0.47          # insurance subsidy rate (GAO 2023 / RR2.0 transition)
A0 = 0.10          # disaster-relief fraction.
                   #   INTERIM VALUE (decision 2026-08-12): between IA-only 0.055 and
                   #   G&S's bundled f = 0.133. Final choice / benefit-vs-cost wedge: TODO.

# ---- calibration inputs for the belief fit -----------------------------------
I_OBS = 0.30       # observed take-up (FEMA / Dixon, high-risk).
                   #   DISCUSSION POINT: dated source; competing values 0.18 (G&S
                   #   risk-weighted) and 0.5-0.6 (Amornsiripanitch, SFHA).
                   #   Voluntary-segment correction (mandate share ~54%, Mulder): TODO.
EPS = -0.32        # premium elasticity of take-up, eps = (pi/I) dI/dpi.
                   #   G&S's within-policy renewal semi-elasticity imported under
                   #   "Reading A" (relative elasticity; the level reading would be a
                   #   different object). Dual-report with Mulder (-0.177 / vol. -0.37): TODO.

# ---- welfare -----------------------------------------------------------------
LAM = 1.2          # MCPF benchmark for the (secondary) optimal-mix exercise;
                   # report lam in {1.1, 1.2}; lam = 1.0 is degenerate (corner).
