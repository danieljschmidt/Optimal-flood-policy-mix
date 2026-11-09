# Calibration overview — parameters, values, and open issues


**Status key:** ✅ agreed and sourced · ⚠️ pending, or paper and code disagree.

**Contents:** 1 Calibration strategy · 2 Parameters · 3 Open issues and to-dos · 4 Results · Appendix: change log.

---

# 1. Calibration strategy

**Layer 1: current-policy MVPF (headline, local).** Paper eq. 7 (`mvpf_prog`) evaluates both MVPFs at the status quo $(s,a)$ from sufficient statistics only:
- **Policy:** $s$, $a$.
- **Flood risk:** $p$, $G(d)$ (with mean $\bar d$).
- **Preferences:** $\gamma$, and the utility base $w$ against which damages are measured.
- **Observed behaviour:** take-up $I$ and its premium elasticity $\varepsilon$, which maps into $\partial I/\partial s$.
- **Derived:** $\partial I/\partial a$ follows from $\partial I/\partial s$ through the model (paper eq. `insurancedemandwrta`; the code's `dI_da`).

This layer needs **no belief distribution $F(q)$, no mandate share $\phi$ and no budget or $\lambda$**. The density at the margin $f(q^*)$ is backed out from $(I,\varepsilon)$.

**Layer 2: optimal policy $(s^*,a^*)$ (secondary, global).** Away from the status quo the observed $I$ and $\partial I/\partial s$ no longer hold, so:
- **Belief distribution:** $F(q)$ is a Beta, exactly identified by take-up at $q^*$ and the density at $q^*$.
- **Mandate:** $\phi$ enters, because only the voluntary segment responds: $I=\phi+(1-\phi)(1-F(q^*))$.
- **Surveys:** validation benchmarks, not inputs (3.4).
- **Planner:** splits today's budget $B_0$ between the instruments; fixed $\lambda$ is a secondary exercise (§2.5).

---

# 2. Parameters

Grouped as in the paper's calibration section: §4.1 (current-policy MVPF: flooding process, utility, current policy, insurance take-up) and §4.2 (optimal policy: mandated share, belief distribution, budget). Table 1 at the end of §4 summarises the values.

## 2.1 The flooding process (§4.1.1)

| Param | Meaning | Paper | Code | Status |
|---|---|---|---|---|
| $p$ | annual flood probability | **0.019**: NFIP claims ÷ policies in force, "in floodplains" (`run_flood_arrival_rate.py`) | **0.02**, round modelling choice | ⚠️ recompute for A/V zones, matched with $G$ (3.1) |
| $G(d)$, $\bar d$ | damage distribution given a flood | building damage ÷ building value, single-family SFHA claims since 2000, n = 812,938, **mean ≈ 0.30** | discrete: **$\bar d=0.15$** (G&S anchor); continuous: **empirical 20 bins, mean 0.3044** (main) / 0.2517 (excl. Katrina) | ⚠️ home-value version pending (3.2) |

- **Damage distribution:** CV ≈ 1.0 in all variants; 7.5% of mass ≥ 0.9 (2.8% excl. Katrina).
- **Not mean-matched:** the discrete model uses 0.15, the continuous model 0.30.

## 2.2 Utility (§4.1.2)

| Param | Meaning | Paper | Code | Status |
|---|---|---|---|---|
| $\gamma$ | CRRA risk aversion | **1.5**; robustness 1 / 3 | **1.5** (log utility at 1) | ✅; tail issue (3.3) |
| $w$ | utility base | **home value incl. land** (MPC ≈ 0.25) | building value until the `_home` files exist | ✅; ⚠️ numbers pending (3.2) |

**Why $\gamma=1.5$:**
- It sits between Chetty (2006: labour supply, mean ≈ 1, values above 2 implausible) and Szpiro (1986: aggregate property insurance, 1.2–1.8 for the US, 1–2 in most countries).
- **Not from insurance choices:** deductible and coverage choices imply triple-digit relative risk aversion (Sydnor 2010; Collier et al. 2017), better explained by overweighting small probabilities (Barseghyan et al. 2013). In our model, the beliefs $q$ absorb such distortions.
- Higher $\gamma$ favours aid (section 4).

**Why home value including land:**
- Damage relative to home value = damage/structure value × (1 − FHFA land share), from Davis et al. (2019), matched by tract, ZIP, county or state. Equivalent to an income base with pass-through MPC ≈ income/home value ≈ 0.25 (mapping: `calibration_decisions.md`, App. A).
- **Options considered:** building value (MPC ≈ 0.24); **home value incl. land (chosen)**; total wealth; income × MPC (feasible only for MPC ≤ 0.25); income × MPC with a loss cap; no separate static calibration.
- **Feasibility:** with the empirical tail (top bin ≈ 0.99, $a=0.052$), flood consumption stays positive only for MPC below about 0.25. Higher MPCs (0.35–0.5) are left to the dynamic model.

## 2.3 Current policy $(s,a)$ (§4.1.3)

| Param | Meaning | Paper | Code | Status |
|---|---|---|---|---|
| $s$ | premium subsidy (premium paid vs expected claims) | **0.22**; robustness 0 / 0.46 | **0.22** | ✅; validate with FEMA data (3.1) |
| $a$ | disaster aid as share of uninsured damage | **0.052**; range 0.010–0.095; 0.12 as upper bound | **0.052** | ✅ |

**Why $s=0.22$:**
- The model's $s$ is the gap between the premium paid and expected claims. G&S's $1-944/1739=0.46$ compares pre-reform premiums with RR2.0 full-risk premiums, which contain loads (GAO-23-105977):
    - catastrophe-model losses "as well as provisions for WYO expense allowances, loss adjustment expenses, and the net cost of reinsurance and retained risk" (p. 16);
    - the expense allowance is "about 30 percent of the premium" (p. 6; fn. 56);
    - a risk load for catastrophic losses (p. 18);
    - fees are separate from the premium (Table 1): an 18% reserve fund assessment, an HFIAA surcharge and a federal policy fee.
- Netting out the expense allowance gives $1-944/(0.7\cdot1739)=0.22$, an **upper bound** since the other loads can't be netted out; counting fees gives about 0. Robustness: 0 and 0.46.
- **Other estimates:** Wagner 0.30 (ex post); Bakkensen–Ma ≈ 0.50.

**Why $a=0.052$:**
- **Bottom-up:** IHP grants plus SBA home loans at subsidy-equivalent value (about $1.75bn a year), 48.9% attributed to flooding, over uninsured residential flood damage (82% of about $20bn a year). Derivation in `calibration_a_two_methods.md`.
- **Why not G&S's 0.133:** it measures how total federal outlays respond to coverage, not the transfer per dollar of damage. Their own per-house aid amounts imply 0.031–0.036. Their IHP-and-SBA estimate, 0.12, is the upper bound for robustness.
- **Sources in the paper:** CRS (IHP), SBA disaster loan data (home loans averaged $1.57bn a year over 2003–2022), First Street Foundation (2021) for the $20bn, Wing et al. (2022) as an all-property comparison.
- **Population:** a national rate applied to SFHA homeowners; the paper states the assumption.

## 2.4 Insurance take-up (§4.1.4) and beliefs (§4.2.1–4.2.2)

| Param | Meaning | Paper | Code | Status |
|---|---|---|---|---|
| $I$ | take-up (share of expected damage insured) | **0.484** (Amornsiripanitch et al. 2025, SFHA) | **0.484** | ✅ |
| $\phi$ | mandated share | **0.32** = 0.39 (Mulder) × 0.484/0.595 | **0.32** | ✅ |
| $\varepsilon$ | premium elasticity of total take-up (relative) | **−0.25**; bounds −0.177 / −0.32; $\partial I/\partial s=0.16$ | **−0.25** | ✅ |
| $F(q)$ | belief distribution (voluntary segment) | Beta, two-moment fit (§3.6, §4.2.2) | `fit_beta`: Beta(0.313, 26.1) discrete / (0.314, 66.3) continuous | ⚠️ survey check only partly met (3.4) |

**Population and $I$:** SFHA homeowners. G&S's national 0.18 stays only in the $a$ calculation, whose denominator is national.

**$\phi$, verified against Mulder (2024):**
- **The 39% (App. F, p. 74):** "39% of homeowners inside the floodplain reported being subject to a mandatory purchase requirement". Only insured mortgage holders were asked, so these households are all insured, as our $\phi$ requires.
- **The "54%":** 39/72 with Mulder's own 72% take-up, not a separate figure (`lit/response_insurance_to_premium.tex` corrected).
- **Mandated households perceive higher risk:** 53% would insure anyway (p. 16), with about 50% higher willingness to pay (App. D); paper footnote in §4. No effect on the calibration, since $F$ is identified from non-mandated households, but it matters for survey comparisons.
- **In the code:** take-up $I=\phi+(1-\phi)(1-F(q^*))$; take-up density $(1-\phi)f(q^*)$; the Beta fit targets voluntary take-up $\frac{I-\phi}{1-\phi}$ and density $\hat f/(1-\phi)$; also in welfare and cost. With $\phi=0$ and old inputs the code reproduces the old outputs; the local MVPFs don't depend on $\phi$.

**Why $\varepsilon=-0.25$ (relative):**
- Two SFHA estimates agree: the G&S SFHA subsample and Wagner (2022; confirmed in his online appendix E, p. 17, A/V zones). G&S's −0.32 covers all zones; Mulder's "0.29" cites Wagner's 2021 working paper.
- **Bounds:** −0.177 (Mulder) and −0.32 (G&S, all zones).
- **Consistency with $\phi$:** implied voluntary elasticity $\varepsilon\,I/(I-\phi)=-0.74$; Mulder's −0.177 on the same base gives −0.52, so $\phi$ and $\varepsilon$ pass the check Mulder applies. The gap to his −0.37 comes from his 72% take-up and lower total elasticity.

**Fitted beliefs:** mean 0.59$p$ (discrete) / 0.24$p$ (continuous), against the survey benchmarks 0.57$p$ (Bakkensen–Barrage) and ≈ 1.6$p$ (Mulder). Details in 4.5.

## 2.5 Planner: budget framing (§3.3, §4.2.3)

| Param | Meaning | Paper | Code | Status |
|---|---|---|---|---|
| $B$ / $\lambda$ | budget framing | **fixed budget $B_0$** (§3.3, eq. 6) | fixed $\lambda$: `LAM = 1.2` | ✅; ⚠️ code pending |

- **Framing:** the planner reallocates today's spending $B_0=p\bar d[s_0I+a_0(1-I)]$ between subsidy and aid. $\lambda$ is the multiplier on that budget, an outcome rather than an input.
- **Secondary exercise:** fixed $\lambda$ = 1.1 / 1.2 answers whether total spending should change. Keep it if the paper says so.

---

# 3. Open issues and to-dos

Ordered by priority. Each item: status · problem · options · recommendation · next step.

## 3.1 TODO (needs `fema.db`) — matched $(p, G)$, premium–damage identity, validation of $s$

**Problem 1, $(p,G)$ not matched:**
- **Samples:** `run_flood_arrival_rate.py` counts *all* claims (any occupancy, no positive-damage filter) by rated zone; $G$ uses single-family A/V claims with a building-value band. The model's expected loss $p\cdot\mathbb E[d]$ drives premiums, the subsidy cost and the belief fit, so $p$ and $G$ must describe the same claims.
- **Years:** policies exist only from 2009, so the pooled rate covers 2009–2025; $G$ covers 2000+ including Katrina, where most of the tail mass comes from. Check that partial-coverage years (e.g. 2008) don't inflate the rate.
- **Which number is 1.9%:** the paper says "in floodplains", but the script reports A, V and X/B/C separately.
- **Sampling:** the script uses the full `policies` table, so the denominator isn't undercounted; but the paper's sentence about a "random sample version" of the policies data is misleading (that 1-in-100 sample is only for the adaptation analysis).
- **Smaller checks:** condo (RCBAP) records cover several units (`policyCount`); policies cancelled before 1 July might pass the `policyTerminationDate` filter.

**Problem 2, premium–damage identity vs dollar levels:**
- The model sets $\bar P=(1-s)\,p\,\bar d$. G&S's full-risk premium is $1,739 and their loss given flood $L_f=\$29{,}267$. Net of the expense allowance, expected claims are about $1,217, implying $p\approx0.04$. Our $p\cdot L_f$ is $556, about 2.2× lower (subsidised premium: $434 vs $944; the gap was 3.1× before the $s$ change).
- **What it suggests:** the claims-based $p$, the claims-based $\bar d$ and the G&S dollar levels may not describe the same households, and $p$ may be too low.
- **Why it matters:** the model runs in ratios, but $p$ and the §4 robustness calculation (damage ≈ 88% of income, "factor 4") rest on this identity.
- **Options:** (1) **recompute from our own FEMA data (recommended)**; (2) adopt G&S's implied $p\approx0.04$–0.055: circular, since it assumes the identity; (3) ignore dollar levels: but $p$ and the robustness calculation depend on them.

**Next step:**
- In `run_flood_arrival_rate.py`, compute claims per policy-year with exactly the filters of `run_compute_damage_distribution.py`:
    - **zones:** A* and V* pooled, matched with `UPPER(TRIM(ratedFloodZone))`;
    - **buildings:** single-family (`occupancyType` 1, 11) for claims and policies;
    - **claims:** damage and building value reported, value $10k–$10m, ratio ≤ 1.5;
    - **years:** the same window for $p$ and $G$, 2009–2024. Recompute $G$ for that window (`since_2010`, mean 0.262, is close).
- **Same pass:** count condo units via `policyCount`; handle cancelled policies; compute premium paid plus fees, claims per policy-year and mean claim in dollars for A/V policies, and compare claims paid with premiums plus fees before RR2.0 (validates $s$).
- **Robustness:** keep the 2000+ distribution (with Katrina) with the same $p$.
- **Sanity check:** an A/V rate around 2% is plausible (Wing et al. 2022 supplement: 2.26% of SFHA residential buildings flooded per year; NFIP history 1.18% claims per policy across all zones).
- **Cross-check, AAL-implied $p$** (from the paper's §4 to-do list: "make consistent with AAL reported in Amornsiripanitch et al. (2025)"):
    - **Idea:** back out $p$ = average annual loss per SFHA home ÷ mean damage given a flood, so that the model's expected loss $p\,\bar d$ matches their AAL.
    - **Why useful:** $I=0.484$ is the insured share of the same AAL, so $p$, $I$ and the expected loss would rest on one population, period and risk measure. It also shows which side of the premium–damage gap (Problem 2) is off.
    - **Caveats:** the AAL is *modelled* (First Street hazard model, all flood events incl. uninsured and small ones), while $G$ is conditional on an NFIP claim, so the result is the claim probability consistent with modelled losses, not an observed frequency. Units must match (AAL in dollars vs mean claim in dollars, same building type, or both relative to home value).
    - **Needs:** their AAL per SFHA home (not in `lit/`; add the paper) and the mean dollar claim from the matched sample above.
    - **Use:** baseline stays the matched claim frequency (its sample matches $G$ exactly). If both give about 2%, fine; if the AAL-implied $p$ is clearly higher, that supports the premium-based evidence that $p$ is too low.
- **Rejected:** pooling A and V without matching filters or years; G&S's implied $p\approx0.055$ (a different object); hydrological return periods (no matching damage distribution).

## 3.2 TODO (needs `fema.db`) — damage relative to home value including land

1. **Run** `run_compute_damage_distribution.py` on `fema.db`, with the FHFA land-price file (`land-prices_2024_20_june.xlsx`) in the data folder. The merged script now **drops** claims with damage/value above 1.5 (previously clipped to 1), so the building-value variants also change slightly. Use the matched sample and years of 3.1.
2. **Switch the code:** continuous model loads `params.FEMA_DIST_MAIN_HOME` in `mvpf_continuous` (and `_EXCL_KATRINA_HOME` in `mvpf_reproduce`); discrete model sets `MEAN_D` to the home-value mean (still the G&S anchor 0.15).
3. **Update the paper:** report the home-value mean, update Figure 1, and check the robustness calculation (home value/income = 2.9/(1 − land share), i.e. 4 at a land share of about 0.27) against the computed land shares.

## 3.3 OPEN decision — utility curvature at near-total losses (continuous model)

**Problem:** with CRRA and the empirical damage distribution, the top bin (mean 0.993, 6% of claims) leaves a flooded, uninsured household with about 6% of its resources. Marginal utility there relative to an insured household: 17 / **70** / 289 / 4,903 at $\gamma$ = 1 / **1.5** / 2 / 3. This one feature drives almost everything extreme in the continuous model:
- the threshold belief collapses ($q^*/p$ = 0.29 at baseline, 0.15 at $\gamma=2$);
- the fitted beliefs become implausible (mean 0.24$p$; 3.4);
- at $\gamma=3$ the Beta fit fails (MVPF$_s$ / MVPF$_a$ = 11.0 / −4,200);
- aid's crowding out explodes, shrinking its net fiscal cost (below).

**Consequence: aid's net fiscal cost is small, and negative at $\gamma=3$.**
- **Mechanism:** with a low marginal belief, aid crowds out a lot of insurance. Each household leaving insurance saves the subsidy net of the aid it now gets: $(s-a)|\partial I/\partial a|$, compared with the direct cost $1-I=0.52$.
- **Baseline:** saving 0.13 (0.09–0.17 across the elasticity bounds), so the denominator stays positive (MVPF$_a$ = 20). The lower $s$ (gap $s-a$ = 0.17 instead of 0.42) defused most of the earlier problem.
- **$\gamma=2$:** saving 0.26 (MVPF$_a$ = 104). **$\gamma=3$:** saving 0.61 > 0.52: more aid raises welfare and lowers spending, which the MVPF convention counts as infinite.
- **Discrete model:** the term is about 0.02; no issue.
- **Reporting:** "∞ (pays for itself)", or numerator and denominator separately.

**The aid MVPF and where the tail enters** (paper eq. 7, local version; $w=1$, $u'(1)=1$):

$$
\text{MVPF}_a=\frac{(p-q^*)\,\Delta u\,\dfrac{\partial I}{\partial a}+p\,\bar U\,(1-I)}{p\bar d\,(1-I)+p\bar d\,(s-a)\,\dfrac{\partial I}{\partial a}},
\qquad \frac{\partial I}{\partial a}=-\frac{q^*}{p}\,\frac{\bar U}{\bar d\,u'(c_I)}\,\frac{\partial I}{\partial s},
\qquad \frac{\partial I}{\partial s}=-\varepsilon\,\frac{I}{1-s},
$$

with $\bar U=\mathbb E[D\,u'(1-(1-a)D)]$, $\Delta u=u(1)-\mathbb E[u(1-(1-a)D)]$ and $q^*=[u(1)-u(c_I)]/\Delta u$; in the discrete model $\bar U=\bar d\,u'(1-(1-a)\bar d)$. The tail enters three times:
- **numerator:** the direct benefit $p\,\bar U(1-I)$ scales with $\bar U$ (5.43 continuous vs 0.19 discrete, about 29×);
- **threshold belief:** a large $\Delta u$ lowers $q^*$ (0.29$p$ vs 0.74$p$), which raises the internality cost $(p-q^*)\Delta u$;
- **denominator:** $|\partial I/\partial a|$ scales with $\bar U$ (0.80 vs 0.14), so the crowding-out saving $(s-a)|\partial I/\partial a|$ offsets a larger part of the direct cost.

Baseline numbers, continuous model: $(0.0116\cdot(-0.799)+0.02\cdot5.43\cdot0.516)\,/\,(0.00609\cdot0.516+0.00609\cdot0.168\cdot(-0.799))=0.0468/0.00232=20.1$; discrete model: $0.00183/0.00148=1.24$.

**What drives MVPF$_a$**. Aid's welfare term $\bar U$ is dominated by the top bin.

| Variation | $q^*/p$ | $\bar U$ | MVPF$_s$ | MVPF$_a$ |
|---|---|---|---|---|
| **Baseline (continuous)** | 0.29 | 5.43 | 1.54 | **20.1** |
| $\gamma=1$ | 0.46 | 1.67 | 1.23 | 5.5 |
| $\gamma=2$ | 0.15 | 19.9 | 2.30 | 104 |
| Excl. Katrina | 0.39 | 2.14 | 1.33 | 8.7 |
| Damages × 0.75 (larger utility base) | 0.50 | 0.71 | 1.19 | 3.0 |
| Damages × 0.5 | 0.63 | 0.27 | 1.09 | 1.7 |
| $a=0$ | 0.13 | 105 | 2.52 | −142 (negative denominator) |
| $a=0.12$ | 0.40 | 2.23 | 1.34 | 6.9 |
| Discrete model (mean damage) | 0.74 | 0.19 | 1.04 | 1.24 |

- **Decisive:** $\gamma$, the weight of the near-total-loss tail, the damage scale relative to the utility base, and $a$, all through consumption in the worst state.
- **Not decisive:** $I$, $\varepsilon$ and $s$ (factors of about 1.5, not 10–100).

**Why uncapped CRRA isn't realistic:** households don't cut consumption by 94% after a total loss. They borrow over years, delay repairs, rely on means-tested support, or walk away. Gallagher and Hartley (2017): the most-flooded Katrina households used insurance payouts to pay off mortgages and moved.

**Options** (`fema_data_analysis/notes/calibration_decisions.md`, Problem 2):
1. **Loss cap at home equity plus moving costs:** households can walk away, so the consumption loss can't exceed equity. Anchors: home equity and LTV data.
2. **Consumption floor** (means-tested safety net), as in Finkelstein, Hendren and Luttmer (2019), who use $\gamma=3$ with a floor.
3. **Piecewise loss function:** pass-through up to a liquidity limit, then annuitised, then capped. Most complete, three extra parameters.
4. **Discrete model as the headline,** continuous only as an extension. Simplest, but drops the tail, where aid's value lies.
5. **Keep uncapped CRRA:** not recommended.

**Effect of a loss cap $\kappa$** (share of home value): uninsured flood consumption becomes $1-\min((1-a)D,\kappa)$. Marginal aid to a household at the cap has zero value to it (it goes to the lender), while the fiscal cost stays.

| Cap $\kappa$ | $q^*/p$ | MVPF$_s$ | MVPF$_a$ |
|---|---|---|---|
| none | 0.29 | 1.54 | 20.1 |
| 0.9 | 0.34 | 1.42 | 3.6 |
| **0.7** | 0.50 | 1.20 | **1.50** |
| **0.5** | 0.69 | 1.06 | **0.79** |
| 0.4 | 0.84 | 1.00 | 0.40 |
| 0.3 | 1.10 | 0.93 | 0.24 |
| $\gamma=1$, cap 0.7 / 0.5 | 0.62 / 0.79 | 1.10 / 1.02 | 1.10 / 0.65 |
| $\gamma=2$, cap 0.7 / 0.5 | 0.39 / 0.59 | 1.34 / 1.12 | 2.12 / 0.97 |
| Excl. Katrina, cap 0.7 | 0.51 | 1.18 | 1.81 |

- **What the cap achieves:** it removes the near-zero-consumption states. At $\kappa$ = 0.5–0.7 the continuous model lands near the discrete benchmark, results become robust to $\gamma$ and Katrina (MVPF$_a$ 1.1–2.1 at $\kappa=0.7$, against 5.5–104 uncapped), and $q^*/p$ rises to 0.5–0.7, closer to the survey benchmarks.
- **But the cap decides the ranking:** aid beats the subsidy at $\kappa=0.7$ (1.50 vs 1.20) but not at $\kappa=0.5$ (0.79 vs 1.06); the switch lies around $\kappa\approx0.6$.
- **Open modelling question:** whether the lender's or GSE's gain from aid paid at the cap counts in welfare, or as a fiscal saving (GSE losses partly fall on the taxpayer). Ignoring it, as above, pulls MVPF$_a$ down mechanically at low caps.
- **Scripts:** `cap.py` and `mvpf_steps.py` in the session scratchpad (not in the repo).

**Recommendation:** option 1, a loss cap, for the continuous model.
- **Why:** documented behaviour (walk-away and default after Katrina), one parameter with an empirical anchor, keeps the tail while removing the near-zero-consumption states.


## 3.4 TODO — belief distribution: survey validation and shape robustness

**Benchmarks:**
- **Bakkensen–Barrage** (Rhode Island, N = 187, all homeowners): mean belief 0.57$p$; 35% have a 10-year belief ≤ 5%.
- **Mulder (2024, Table A1, p. 59):** SFHA respondents report a mean 10-year flood risk of 27.75% (17.5% outside), about 3.2% a year, **≈ 1.6$p$** at $p=0.02$. Caveats: 159 SFHA respondents; mandated households included (39% lender-required, 66% insured), who perceive higher risk; means only. Correlation of perceived with modelled (First Street) risk is only 0.18.
- **Implication:** the surveys differ by a factor of about 3, and stated small probabilities are known to be overweighted. The surveys don't pin down beliefs tightly; the mean check is weak evidence either way.

**Fit against Bakkensen–Barrage:**

| $\varepsilon$ | $\phi$ | Voluntary $\varepsilon$ | Discrete: mean / share ≤ 5% | Continuous: mean / share ≤ 5% |
|---|---|---|---|---|
| −0.177 | 0.32 | −0.52 | 0.76$p$ / 0.63 | 0.31$p$ / 0.74 |
| **−0.25** | **0.32** | **−0.74** | **0.59$p$ / 0.58** | **0.24$p$ / 0.74** |
| −0.32 | 0.32 | −0.94 | 0.54$p$ / 0.52 | 0.21$p$ / 0.73 |
| −0.25 | 0.26 | −0.54 | 0.89$p$ / 0.54 | 0.36$p$ / 0.68 |

- **Mean, discrete:** matches (0.59$p$ vs 0.57$p$). $F$ covers only non-mandated households, who should believe less than the surveyed population, so the match may even be slightly high.
- **Low-belief share:** fails in every combination (0.52–0.74 vs 0.35), so it isn't an $\varepsilon$ or $\phi$ problem. The fitted $\alpha\approx0.31<1$ makes the Beta density rise without bound towards $q=0$.
- **Continuous model:** fails both checks, mainly because of the tail (3.3).
- **Scope:** the local MVPFs don't use $F$; the failure matters only for the optimal mix.

**Options:**
1. **Keep the Beta and report the checks as they are,** explained by decision weights, the voluntary-only scope of $F$ and the disagreement between surveys. Cheapest.
2. **Robustness over the shape of $F$** (the empty "Functional form belief distribution" section): (a) **mixture**: a point mass of "never-insure" households ($q\approx0$) plus a Beta, one extra parameter; (b) other two-parameter families (log-normal, gamma) fitted to the same moments.
3. **Calibrate to the survey** with a third parameter: loses the validation role, and with benchmarks 3× apart the target would be arbitrary.
4. **Bounds** on $(s^*,a^*)$ over all $F$ consistent with $(I, f(q^*))$: most rigorous, most work.
5. **Better-matched benchmark:** non-mandated SFHA respondents in Mulder's survey; needs his microdata.

**Recommendation:** keep the Beta as baseline and lead with the local results; report both benchmarks honestly and frame the fitted $q$ as decision weights; test the mixture (option 2a); judge the continuous fit only after 3.3; don't calibrate to the survey.

**Next step:**
- **Code:** add a mixture option (point mass $\mu$ at $q\approx0$ plus a Beta fitted to the same two moments). Re-solve the fixed-budget optimum for $\mu$ = 0, 0.1, 0.2, 0.3 and report whether aid still dominates. Optional: log-normal or gamma $F$.
- **Paper:** §4.2.2 (drafted 2026-11-08) states $F$, its fit, both survey benchmarks and the decision-weight interpretation; the fitted values are still [TO DO] placeholders until 3.3 and 3.2 are settled. Still to fill: the "Functional form belief distribution" robustness section.
- **Data (optional):** ask Mulder for the perceived-risk distribution of non-mandated SFHA respondents.

---

# 4. Results (provisional)

**Inputs:** $\gamma=1.5$, $s=0.22$, $a=0.052$, $I=0.484$, $\phi=0.32$, $\varepsilon=-0.25$, $p=0.02$ (not yet updated), building-value damage base, no loss cap. Optimal mixes from the discrete model unless stated. Provisional until 3.1–3.3 are done.

**Baseline:**

| Model | Local MVPF$_s$ | Local MVPF$_a$ | Fixed $\lambda=1.2$: $s^*$, $a^*$ | Fixed $\lambda=1.1$: $s^*$, $a^*$ |
|---|---|---|---|---|
| Discrete | 1.038 | 1.238 | 0.00, 0.14 | 0.00, 0.50 |
| Continuous (FEMA main) | 1.537 | 20.1 | 0.00, 0.81 | 0.00, 0.90 |

**Fixed budget (chosen framing; scratch script, not yet in the repo).** Today's spending $B_0$ has 20% going to aid.

| $\gamma$ | $s^*$ | $a^*$ | Aid share of budget | MVPF$_s$ / MVPF$_a$ at the optimum |
|---|---|---|---|---|
| 1 | 0.00 | 0.23 | 100% | 1.016 / 1.110 |
| 1.5 | 0.00 | 0.23 | 100% | 1.025 / 1.171 |
| 2 | 0.00 | 0.23 | 100% | 1.033 / 1.234 |
| 3 | 0.00 | 0.23 | 100% | 1.052 / 1.373 |

- **A corner at every $\gamma$:** aid's MVPF stays above the subsidy's even at the optimum; $\gamma$ changes only the size of the gap.
- **Not answered:** whether total spending should rise or fall.

**By $\gamma$ (local MVPFs and fixed $\lambda$):**

| $\gamma$ | Discrete MVPF$_s$ / MVPF$_a$ | Continuous MVPF$_s$ / MVPF$_a$ (q*/p) | $\lambda=1.2$: $s^*$, $a^*$ | $\lambda=1.1$: $s^*$, $a^*$ |
|---|---|---|---|---|
| 1 | 1.03 / 1.15 | 1.23 / 5.5 (0.46) | 0.00, 0.00 | 0.00, 0.29 |
| **1.5** | **1.04 / 1.24** | **1.54 / 20 (0.29)** | **0.00, 0.14** | **0.00, 0.50** |
| 2 | 1.05 / 1.33 | 2.30 / 104 (0.15) | 0.00, 0.32 | 0.00, 0.62 |
| 3 | 1.08 / 1.54 | 11.0 / −4,200 (0.023; Beta fit fails) | 0.00, 0.53 | 0.00, 0.75 |

- **Ranking:** aid's MVPF exceeds the subsidy's at every $\gamma$, and $s^*=0$ throughout.
- **Level of aid under fixed $\lambda$:** **with very low risk aversion optimal aid is zero, and it rises with $\gamma$.** At $\gamma=1$, $\lambda=1.2$ neither instrument is worth funding, so "optimal aid exceeds its current level" fails at the low end of the $\gamma$ range.

**Sensitivity of the local MVPFs (subsidy / aid):**

| Varied input | Discrete | Continuous |
|---|---|---|
| $\varepsilon=-0.177$ | 1.028 / 1.244 | 1.388 / 19.3 |
| $\varepsilon=-0.32$ | 1.047 / 1.232 | 1.676 / 21.1 |
| $s=0.03$ | 1.03 / 1.23 | 1.46 / 14.7 |
| $s=0.46$ | 1.05 / 1.26 | 1.68 / 39.4 |

Continuous-model drivers and the loss-cap scenarios: 3.3.

---

# Appendix: change log

**2026-11-07** (reasoning in §2):

| Parameter | Old | New | Applied in |
|---|---|---|---|
| Population | not settled | **SFHA homeowners** (Daniel's comment removed) | paper, code, notes |
| Take-up $I$ | code 0.30 | **0.484** | code (paper already) |
| Mandated share $\phi$ | in paper, not in code | **0.32**, implemented | code |
| Disaster aid $a$ | paper 0.12 (intro 0.09), code 0.10 | **0.052** | paper §4, code |
| Elasticity $\varepsilon$ | §4 −0.21, §3.6 −0.32 (semi), code −0.32 | **−0.25** (relative; §3.6 formula for $f(q^*)$ now has the factor $I$) | paper §3.6 and §4, code |
| Risk aversion $\gamma$ | paper empty, code 2 | **1.5** (log utility supported at 1) | paper §4, code |
| Subsidy $s$ | paper 0.46, code 0.47 | **0.22** (vs expected claims) | paper §4, code |
| Utility base $w$ | undefined in paper; code building value | **home value incl. land** | paper §4; code pending (3.2) |
| Planner problem | paper fixed $B$, code fixed $\lambda$ | **fixed budget $B$** | paper (already); code pending |

- **Paper text changes with the $s$ update:** the claim that administrative costs "do not affect the household" was replaced; $\partial I/\partial s$ = 0.16; the robustness calculation now gives damage/income ≈ 88% and building value/income ≈ 2.9.
- **Paper footnote (§4):** mandated households perceive higher risk (Mulder).
- **Smaller paper fixes:** figure path (Daniel); "FY2003–2024" → "2003–2024". New bibliography entries: SBA loan data, First Street (2021), GAO (2023), Davis et al. (2019), Szpiro (1986), Sydnor (2010), Barseghyan et al. (2013), Collier et al. (2017).
- **Other files:** `lit/response_insurance_to_premium.tex` (Mulder 54% corrected); Taco's land-share branch merged locally (`69a1669`).

**2026-11-08:** no parameter changes. Paper: §4 introduction and new §4.2 (mandated share, belief distribution, budget), Table 1 extended, Katrina robustness sentence, introduction rewritten. Added Mulder as a second survey benchmark and the belief-shape robustness plan (3.4); the analysis of what drives MVPF$_a$ and the loss-cap scenarios (3.3); this restructuring.
