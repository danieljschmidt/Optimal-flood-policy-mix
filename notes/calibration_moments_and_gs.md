# Calibration Moments Needed, and Where Gruber & Solomon Helps

*Summary note. Sources read: `draft/draft.tex`, `notes/daniel_notes/` (`gruber_solomon.md`,
`project_state_and_next_steps.md`), `notes/empirical_counterparts/empirical_counterparts.tex`.*

## Question

Which empirical moments does the calibration need, and which of them can the Gruber &
Solomon (G&S, NBER WP 35408, July 2026) paper supply?

## Short answer

G&S resolves most of the **behavioral, loss, policy-cost, and extension** moments with
well-identified US estimates. It contributes **nothing** to the belief *distribution*
$F(q)$ — the project's central object — because its entire behavioral content is a single
uniform scalar wedge in an appendix. It also does not supply the structural preference
parameters, wealth, the damage distribution, or the mandate/heterogeneous-$p$ corrections.

---

## The moments the calibration needs

Grouped by role, because the role determines whether G&S can substitute for another source.
References are to `draft.tex` (calibration table lines 186–203; belief recovery 217–238).

### A. Structural / preference parameters
| Moment | Symbol | Role | Current source |
|---|---|---|---|
| Risk aversion | $\gamma$ | curvature of $u$; drives $u'(c_I)$ vs $u'(c_{U,F})$ | Chetty (2006), lit range [1,4] → $\gamma=2$ |
| Household wealth | $w$ | normalization; sets $d/w$ | SCF, AHS |
| Shadow value of budget | $\lambda$ | MVPF benchmark at optimum | Hendren–Sprung-Keyser (2020) |

### B. Flood-risk / loss primitives
| Moment | Symbol | Role | Current source |
|---|---|---|---|
| True flood probability | $p$ | planner welfare weight; internality $(p-q^*)$ | SFHA def. (0.01) / First Street |
| Flood damage (share of value) | $d,\bar d$ | loss size; premium $(1-s)pd$ | NFIP claims |
| Damage-to-wealth ratio | $d/w$ | drives $c_{U,F}$ and the MVPF gap | NFIP claims / home values |
| **Damage distribution** | $G(D)$ | needed for continuous-damage baseline | NFIP claims distribution |

### C. Policy parameters (status quo)
| Moment | Symbol | Role | Current source |
|---|---|---|---|
| Current subsidy rate | $s$ | evaluation point (≈0.47) | GAO (2023), RR2.0 |
| Current relief fraction | $a$ | evaluation point (≈4–7%) | FEMA IA grant / claim |
| Insurance take-up | $I$ | pins mass below $q^*$; $1-I=F(q^*)$ | FEMA penetration rates |

### D. Behavioral / belief moments (the identification core)
| Moment | Symbol | Role | Current source |
|---|---|---|---|
| Price semi-elasticity of take-up | $\varepsilon$ | **single input** to recover $f(q^*)$ (eq. `fqstar`) | Mulder, Gourevitch, Browne–Hoyt |
| Density at margin | $f(q^*)$ | all behavioral MVPF terms | derived from $\varepsilon,I$ |
| Belief distribution | $F(q)=\text{Beta}(\alpha,\beta)$ | global counterfactuals | fitted to $(I,\varepsilon)$; validated on surveys |
| Crowd-out | $\partial I/\partial a$ | relief moral hazard | Kousky et al. (2018) / ratio trick |
| Mandate share | — | corrects contamination of $F(q)$ recovery | Mulder |

### E. Extension moments (adaptation / sorting / admin)
| Moment | Symbol | Role | Current source |
|---|---|---|---|
| Mitigation elasticity | $\eta_m$ | adaptation instrument $b$ | (was missing → G&S) |
| Adaptation costs | $k$ | annualized user cost | Aerts et al. (2019), July note |
| Location/migration elasticity | $\eta_x$ | sorting bound | (was to be built → G&S) |
| Admin-cost asymmetry | — | MVPF wedge; tilts toward relief | (was missing → G&S) |

---

## Where G&S helps

### Resolves directly (adopt as inputs, with attribution)
| Moment | G&S value | Note |
|---|---|---|
| $\varepsilon$ / $\eta_q$ | **−0.32** overall, **−0.25** in SFHA | Best-identified: FOIA'd within-property billed-vs-full-risk premium variation. Adopt as baseline, retiring −0.17. SFHA/overall split quantifies mandate attenuation. |
| $d$ (avg. loss $L_f$) | **\$29,267** | Direct loss magnitude |
| Premium $\bar P$ | **\$1,739** | Anchors the $(1-s)pd$ scale |
| Relief fraction $a$ / $f$ | **$f\approx13.3\%$** (\$173–216/house per 1pp coverage, IV'd) | First credible insurance→relief fiscal offset. **Reconcile, do not average**, with the IA-based 4–7% (theirs bundles SBA+HMGP+GSE). Motivates a benefit-rate ≠ cost-rate split. |
| Intensive margin ≈ 0 | ~1% | Independently justifies the binary insurance choice |
| $\eta_m$ (mitigation) | **0.30–0.38** (FL), ≈0.075 reweighted nationally | Adaptation module. Maps to the *new-construction* margin (elevation certs filed pre-build). |
| $\eta_x$ (location) | **−0.0077** (\$0.04/house-yr) | Bound sorting in one paragraph instead of building the spatial model → defer two-region note. |
| Admin-cost asymmetry | NFIP ≈30% of premiums vs FEMA ≈13% of assistance | First-order in the MVPF comparison; tilts toward relief. |

### Helps *validate* (targets, not inputs)
| Moment | Value | Use |
|---|---|---|
| Mean underperception | $k_R=0.57$ (Bakkensen–Barrage, adopted by G&S) | Fitted $F(q)$'s implied mean $q/p$ should reproduce this — free credibility check |
| Aid over-perception | $k_F=1.5$ | Anchor for the perceived-vs-actual relief wedge $a_{\text{perc}}\ne a$ |

### G&S does NOT help — need other sources
- **$F(q)$, the belief distribution itself** — their behavioral content is one scalar $\lambda_i$
  for everyone, in an appendix. No marginal household, no density, no heterogeneity. This is the
  project's contribution; it must come from revealed-preference recovery $(I,\varepsilon)$ plus
  **Mulder's information effect** (floodplain designation raises take-up 17–30pp) as the
  over-identifying moment, and **Bakkensen–Barrage** cross-sectional dispersion.
- **$\gamma$** — they use CARA ($\gamma=5\times10^{-4}$) from the deductible literature, a fragile
  different functional form. Keep CRRA=2.
- **$\lambda$** — external (Hendren–Sprung-Keyser).
- **$w$** and **$G(D)$** (continuous-damage distribution) — SCF / NFIP claims.
- **Heterogeneous $p$ / mandate share** — SFHA definitions + Mulder, not G&S.
- **Adaptation costs $k$** — Aerts et al. (2019) via the July note; G&S estimates mitigation
  *responses* but has no adaptation *cost* or *instrument*.

---

## Caveat: the units error travels with the G&S elasticity

`empirical_counterparts.tex` currently plugs in $\varepsilon=-0.17$ and reports
$\partial I/\partial s = 0.000153$, MVPF$_s\approx1.003$, MVPF$_a\approx1.358$ (lines 140–155).
Daniel's §5 flags this as a **units error**: the note treats $\varepsilon$ as a level derivative
$(1/I)(\partial I/\partial\pi)$, but the literature number is a proper elasticity — a factor of
$1/\pi\approx600$ apart. The note's conclusion that the internality/fiscal terms are "negligibly
small" (line 155) must be **retracted** once corrected. When the calibration is rebuilt, the G&S
$\eta_q=-0.32$ and the units fix must be applied together. (See `mvpf_complementarity.md` for the
corrected numbers.)
