# Model Parameters — what we need to calibrate

*The **Value** column is what the **current findings actually use**; **Value (G&S)** is the
Gruber–Solomon (NBER WP 35408) estimate where one exists; **Source (G&S)** is how G&S identify it;
**Reasoning** says whether we adopt G&S and, if not, why. Continuous-damage parameters are folded
into §1b, tagged **[cont]**. §2 lists quantities that are **not model inputs** but are useful
consistency checks. G&S page refs are printed pages (PDF page = printed + 2). Cross-refs:
`draft/draft.tex`, `code/params.py` (single source of truth), `code/belief_identification.py`,
`lit/gruber_solomon.md`.

---

## 1a. Structural / preference parameters
| Symbol | Meaning | Value | Source | Value (G&S) | Source (G&S) | Reasoning |
|---|---|---|---|---|---|---|
| $\gamma$ | CRRA risk aversion | 2 | Chetty (2006) | CARA $5\times10^{-4}$ | deductible-choice lit (Cohen–Einav, Sydnor), calibrated | **Not using G&S** — different functional form (CARA vs CRRA); implies implausibly high RRA at annual scale (flagged fragile in project notes). |
| $w$ | household wealth | 1 (normalized) | SCF/AHS | — | not estimated | **No G&S value.** Normalization; dollar scale cross-checked by G&S $\bar P,\,L_f$ ($w\approx\$195$k at $\bar d/w=0.15$). |

## 1b. Flood-risk / loss primitives  (discrete baseline + [cont] additions)
| Symbol | Meaning | Value | Source | Value (G&S) | Source (G&S) | Reasoning |
|---|---|---|---|---|---|---|
| $p$ | true annual flood probability | 0.02 | modelling choice (see below) | ≈ 0.055 | $p_f=\sigma_{PDD}\bar P/L_f$, §9.1 p. 31, App. B.22 p. 105 | **Not using G&S (yet)** — their implied value (≫ SFHA nominal 1%) reflects the higher-risk NFIP-insured sample. Kept 0.02; flagged for reconciliation (discussion point below). |
| $\bar d=\mathbb{E}[D]$ | (mean) flood damage, share of wealth | 0.15 | NFIP claims / home value | \$29,267 ($L_f$) | NFIP loss data (loss given flood) | **Partially G&S** — $\bar d/w=0.15$ consistent with $L_f$ at $w\approx\$195$k. In the discrete model this scalar *is* the damage; in the continuous model it is the mean of $G$. |
| CV **[cont]** | coeff. of variation of $D$ ($=\sigma_D/\bar d$) | 0.86 (also ran 1.3) | **placeholder** | — | not estimated | **No G&S value** — the dispersion dial; relief's tail-insurance value scales with it. **Placeholder until the FEMA claims-based distribution arrives (Daniel delivering).** |
| $D_{\max}$ **[cont]** | damage cap (share of wealth) | 1.0 (0.9 for CV=1.3) | modelling choice | — | not estimated | **No G&S value** — keeps CRRA marginal utility finite for heavy tails; max loss ≈ home value. |
| family **[cont]** | functional form of $G$ | Beta$(\alpha,\beta)$ on $[0,D_{\max}]$ | assumed (see below) | — | only scalar $L_f$ | **No G&S value** — G&S give the mean loss only; the *distribution* needs NFIP claims microdata. |

![Flood-damage distribution](figures/damage_distribution.png)

**Reading the y-axis (density).** $g(D)$ is a *probability density*, not a probability: the **area**
under the curve between two damage levels is the probability that damage falls in that range (total
area = 1). Height itself can exceed 1 (as here near $D=0$) because $D$ is measured in fine units
(share of wealth) — only *areas* are probabilities.

**Shape vs. CV — how the two relate, and where the numbers come from.** The *shape* is the full
functional form of $G$ (the whole density, including skew and tail); the *CV* is a single summary of
its spread. They are **not independent**: once we fix the **family** (Beta), the **support**
$[0,D_{\max}]$, and the **mean** $\bar d$, the CV pins down the two Beta parameters $(\alpha,\beta)$ —
so CV is the free *dial* and the shape is *derived*. Concretely CV = 0.86 ⇒ Beta$(1,5.67)$;
CV = 1.3 ⇒ Beta$(0.33,1.63)$ scaled to $[0,0.9]$. **The entire specification is a placeholder:
Daniel is delivering a FEMA claims-based damage distribution**, which will replace it (via
`configure_damage`); until then treat the CV values as illustrative.

**Why a Beta for damages?** (i) It lives on a **bounded** interval — damage is a non-negative share of
wealth that cannot exceed total loss, matching $[0,D_{\max}]$; (ii) two parameters flexibly span
monotone, hump-shaped, and right-skewed forms; (iii) it maps cleanly onto (mean, CV), our two economic
targets; (iv) it has finite moments and a closed-form density, so the quadratures are stable.
*Caveat:* real NFIP claims may be fatter-tailed than a Beta allows — a lognormal, Gamma, or the raw
empirical distribution are natural robustness swaps.

**⚠ DISCUSSION POINT — how $p$ is calibrated, and the target population.** Currently $p = 0.02$ is
a **round modelling choice**, set above the 1% SFHA floor (the SFHA is the ≥1%-annual floodplain) to
represent a somewhat-higher-risk insured population — it is *not* yet rigorously estimated. Cleaner
options, in increasing order of rigour: (a) NFIP **claim frequency** (paid claims per policy-year)
in the target zone; (b) **First Street / FEMA flood-hazard-layer** return periods; (c) adopt G&S's
directly reported $p_f = \sigma_{PDD}\bar P/L_f \approx 0.055$ for the NFIP-insured population. All
three point *above* 0.02, so $p$ is a live reconciliation item (and it rescales everything
downstream: premiums, the belief fit, $q^*/p$). Options on the table: switch to the SFHA population
($p \approx 0.055$, higher take-up, mandate modelled — "P1") or a two-zone model ("P3"); both are
optional TODOs, to be decided **before** the next calibration pass.

## 1c. Policy parameters (status-quo evaluation point)
| Symbol | Meaning | Value | Source | Value (G&S) | Source (G&S) | Reasoning |
|---|---|---|---|---|---|---|
| $s$ | insurance subsidy rate | 0.47 | GAO (2023)/RR2.0 | ≈ 0.47 current ($s^*=52\%$) | NFIP premium data / sufficient-stat optimization | **Consistent with G&S** — current level matches ($1-944/1739 \approx 0.46$); used 0.47. |
| $a$ | disaster-relief fraction | **0.10** | interim decision 2026-08-12 | 0.133 ($f$) | App. B.22 p. 105: $f=|\beta_{cond}|/(\sigma_{PDD}\bar P)$; IV spillover $-\$216$/house/1pp | **Interim value** — see below; final choice TODO. |

**Why not G&S's $a=0.133$ (yet) — interim 0.10.** Two problems with plugging 0.133 straight in:
**(i) it bundles four programs** — IHP (FEMA Individuals & Households grants; IA is its
Individual-Assistance part), SBA disaster **loans**, HMGP (Hazard Mitigation Grant Program), and GSE
(Fannie/Freddie forbearance) — whereas the IA-only count is 0.055. **(ii) It mixes benefit- vs
cost-rate:** an SBA *loan* costs the government ~13¢ per dollar (subsidy cost) but delivers far less
than face value to the household (they repay it), so the *fiscal cost rate* and the *household
benefit rate* diverge. Our model's single $a$ is **both at once** (household benefit = fiscal cost),
so 0.133 — a fiscal-cost number — cannot serve as the household-benefit rate. Hence "**reconciled,
not averaged**": model each channel's benefit and cost rate separately rather than splitting the
difference (the $a_{benefit} \ne a_{cost}$ wedge — an open TODO). Two further candidates sharpen the
range: **≈0.09** (spillover-implied: $\beta_{cond}$ ÷ application rate ÷ $L_f$) and **≈0.14**
(damage-weighted IHP-only: G&S fn. 4, p. 7 — \$20k average IHP payout against \$144k damage, well
above the unweighted IA figure). **Decision 2026-08-12: work with $a = 0.10$** (inside the candidate
range) and postpone the final choice.

## 1d. Behavioural / belief inputs

| Symbol | Meaning | Value | Source | Value (G&S) | Source (G&S) | Reasoning |
|---|---|---|---|---|---|---|
| $I$ | insurance take-up rate | 0.30 | FEMA / Dixon (high-risk) | 0.18 (risk-wtd); 0.05 (nat'l) | NFIP coverage counts | **⚠ Discussion point** — 0.30 has a real but dated source (Dixon, high-risk penetration); alternatives: 0.18 risk-weighted (G&S), 0.50–0.60 SFHA (Amornsiripanitch et al. 2025, cited in our draft). Depends on the modeled population (§1b). Voluntary-segment correction (mandate share ≈54%, Mulder App. F): TODO. |
| $\varepsilon$ | premium elasticity of take-up | −0.32 | **G&S $\eta_q$**, Reading A | −0.32 (−0.25 SFHA) | FOIA policy-level panel; within-policy variation from 18%/yr cap, contract FE (§5 p. 19, Table 3) | **Using G&S** under the *relative-elasticity* reading ("Reading A"): their renewal semi-elasticity equals $\varepsilon$ through the threshold model. The alternative level reading ("Reading B", how G&S apply it in their own §9 fiscal arithmetic) would be a different object. Dual-report with Mulder (−0.177; voluntary −0.37): TODO. |
| $F(q)$ | belief distribution | Beta **fitted to $(I,\varepsilon)$** | draft.tex two-moment strategy | — | no belief distribution (uniform wedge only) | **Decision 2026-08-12** — the two Beta parameters are exactly identified by (take-up level, density at margin). Surveys are *validation targets, not calibration inputs*. |

**The fitted belief distribution (decision 2026-08-12).** The density at the take-up margin is
recovered as $\hat f = -\varepsilon\,(I/\pi)\,(\Delta u/u'(c_I))$ with $\pi=(1-s)p\bar d$, and the
Beta is fitted to the two moments $F(q^*) = 1-I$ and $f(q^*) = \hat f$
(`code/belief_identification.py`). Because $q^*$ and $\Delta u$ differ across damage models, the
fit is per-module. At the status quo $(s,a)=(0.47,0.10)$:

| damage model | $\hat f$ | fitted Beta$(\alpha,\beta)$ | mean $m$ ($\times p$) | $\nu=\alpha+\beta$ | $\sigma_q$ |
|---|---|---|---|---|---|
| discrete | 9.39 | (0.143, 5.69) | 0.0245 (1.22$p$) | 5.83 | 0.059 |
| continuous CV=0.86 | 11.03 | (0.143, 6.63) | 0.0211 (1.05$p$) | 6.78 | 0.052 |
| continuous CV=1.3 | 14.54 | (0.143, 8.65) | 0.0163 (0.81$p$) | 8.79 | 0.041 |

**Survey validation (checks, not inputs) — current results, reported honestly.** Bakkensen–Barrage
(2022; RI door-to-door elicitation, $N=187$; 10-year horizon; *the paper itself is not in `lit/`
— verify the table refs before external use*) provides two checks:

- **Mean check ($k_R$):** B–B's mean under-perception ratio is $k_R = 0.57$ (adopted by G&S). Our
  fitted mean is **0.81$p$–1.22$p$** — the mean check *fails*: a thin upper tail (≈7% of households
  above $q=0.10$) drags the fitted mean up, even though 77–81% of the mass lies below $p$ and the
  median is ≈0.03$p$–0.05$p$. Under-perception as a *premise* survives; $k_R$ as a *mean target*
  does not — which is precisely why the mean was demoted from calibration input to check.
- **Quantile check:** B–B report 35% of respondents perceive a 10-year flood probability ≤ 5%. The
  fitted distributions put **64–68%** below that threshold — more low-belief mass than the
  elicitation. Both failures point the same way: the revealed-preference fit implies *more*
  dispersed, more extreme beliefs than the survey; whether that reflects non-belief frictions in
  $(I,\varepsilon)$ (liquidity, distrust, salience) or survey noise is exactly the identification
  discussion (Mulder over-identification test, contamination share — open TODOs).

*(Local MVPFs need only $(I,\varepsilon)$ — no distribution at all; the fitted Beta is used only by
the global optimal-mix exercise. The former presentation — imposing $m=0.57p$ and sweeping the
concentration $\nu$ — is retired; the old sweep figures/tables are superseded.)*

## 1e. Government / welfare
| Symbol | Meaning | Value | Source | Value (G&S) | Source (G&S) | Reasoning |
|---|---|---|---|---|---|---|
| $\lambda$ | marginal cost of public funds | 1.1–1.2 | **G&S** robustness (Hendren–Sprung-Keyser) | 1.2 | robustness check (their baseline is lump-sum, MVPF = 1) | **Using G&S's robustness value**, reported as a small sensitivity axis. |

**On $\lambda$.** The MCPF is the welfare cost of raising \$1 of public revenue (the deadweight loss
of taxation); standard values run ~1.0–1.5. We adopt **G&S's 1.2**, reported alongside 1.1 as a
small sensitivity axis. Note $\lambda$ enters **only** the optimal-mix / phase-diagram exercises;
the **MVPF status-quo results are $\lambda$-independent**. A higher $\lambda$ concentrates optimal
spending in the higher-MVPF instrument (relief): at the fitted beliefs the optimum is relief-only or
relief-heavy at both reported values (see `mvpf_computations.md` §8). $\lambda = 1.0$ is degenerate
in our setting (both instruments' MVPFs exceed 1 at the status quo, so the optimum runs to the grid
corner) and is noted only as a footnote.

---

## 2. Consistency checks (not model inputs)

Quantities we do **not** feed into the model, but that let us test whether the calibrated
$(p,\bar d,s,a,I,\ldots)$ imply realistic magnitudes.

| Symbol | Meaning | Value (G&S) | Model analog | Model value | Verdict |
|---|---|---|---|---|---|
| $\bar P$ | average annual premium | \$1,739 | $p\,\bar d$ | **\$585** ($=0.02\times\$29{,}267$) | **~3× low** — matches G&S only at $p\approx0.06$; this *is* the $p$ discussion point (§1b). |
| $\beta$ | FEMA ex-post \$ saved / house / 1pp coverage (cond. flood) | −\$216 (IV); −\$1,192/unit uncond. | $0.01\,L_f\,a$ (cond.) | **\$29** ($a{=}0.10$) / **\$39** ($a{=}0.133$) | **5–7× low** — flat-fraction relief misses channels G&S capture (NFIP-payout offsets, GSE, correlated triggers), or units differ (per-house vs per-switcher). If the gap survives, the model **understates** relief's fiscal savings ⇒ *strengthens* the case for relief. |

Both checks come out **low**, and in instructive ways: the $\bar P$ gap is exactly the
$p=0.02$-vs-G&S tension (it closes at $p\approx0.06$), and the $\beta$ gap says our simple
"relief = fraction $a$ of own damage" understates the true federal spillover. Neither is a model
input — $\beta$ in particular is the *source* G&S use to back out $f\approx0.133$, so feeding both
it and $a$ would double-count.

---

## Appendix — G&S values available for potential extensions
(not in the current model, ready to slot into roadmap extensions)

| Symbol | Meaning | Value (G&S) | Source (G&S) | Use |
|---|---|---|---|---|
| $\eta_m$ | mitigation/adaptation elasticity | 0.30–0.38 (FL); ≈0.075 reweighted | Florida Elevation Certificates, DiD | adaptation instrument $b$ (new-build margin) |
| $\eta_x$ | location/migration elasticity | −0.0077 | USPS tract-address panel, event study | sorting bound (defers two-region model) |
| admin loads | NFIP vs FEMA overhead | 30% of premiums vs 13% of assistance | NFIP / FEMA program accounts | benefit/cost wedge; tilts MVPF toward relief |
| $k_F$ | aid over-perception | 1.5 | Bakkensen–Barrage elicitation | perceived-vs-actual relief wedge $a_{\text{perc}}\ne a$ |
| intensive margin | coverage-amount elasticity | ≈ 0 (~1%) | FOIA policy-level panel | justifies binary insurance choice |
| reclassification risk | premium-risk SD (2070) | \$1,842; 50%-subsidy value \$207 | NFIP universe × 40 climate scenarios | a channel we deliberately do **not** model |
