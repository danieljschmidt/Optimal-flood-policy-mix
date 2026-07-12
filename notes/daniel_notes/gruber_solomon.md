# Gruber & Solomon (NBER WP 35408, July 2026): "Optimal Flood Insurance in a Second-Best World" — Summary and Relation to Our Project

**Bottom line.** G&S ask what the optimal NFIP premium subsidy $s$ is when ex post FEMA aid exists and is held fixed. They build a sufficient-statistics model with three household margins (coverage, mitigation, location) plus a novel dynamic margin (reclassification risk from climate uncertainty), estimate five parameters with new quasi-experimental designs and FOIA'd policy-level data, and conclude the optimal subsidy is **52%** — close to the pre-Risk-Rating-2.0 level — with the first 8 points of subsidy having *infinite* MVPF. The dominant force is the fiscal spillover: each 1pp of NFIP coverage saves \$173–216 per house in ex post federal spending conditional on a flood. Their baseline assumes rational households; a behavioral appendix with *uniform* risk underperception pushes $s^*$ to 89–100%. Crucially for us: **disaster-relief generosity is never a choice variable** in their framework, and **belief heterogeneity — our core object — is absent**. The papers are complements with a real overlap that must be managed.

---

## 1. Question and headline results

The framing is second-best theory applied to RR2.0: the 2021 move to actuarially fair NFIP premiums fixes one distortion (subsidy-induced overbuilding and under-mitigation) but aggravates two others they argue were ignored — (i) lower coverage shifts costs onto FEMA's ex post programs (Samaritan's dilemma read in reverse), and (ii) tying premiums to property-level climate risk exposes households to uninsurable **reclassification risk**, since climate models disagree sharply about *where* risk will rise. Context numbers: nationwide flood coverage is 5% (18% flood-risk-weighted); FEMA-relevant ex post spending averages \$996 per house per flood-weighted county-year vs. \$3,562 in NFIP payouts; roughly 84% of flood damage is uninsured either ex ante or ex post.

Headline quantitative results: optimal subsidy $s^*=52\%$ at central parameters ($\eta_q=0.32$, $\bar P=\$1{,}739$); MVPF of the subsidy is infinite up to $s\approx 8\%$ and crosses 1 at 52%; adding NFIP admin costs (30% of premiums, vs. FEMA's 13%) lowers $s^*$ to 40%, and an MCPF of 1.2 lowers it to 34%; a "compounded worst case" floor is 14%; with behavioral misperceptions $s^*$ rises to 89–100%. The optimal subsidy falls to 19% for non-primary residences (ineligible for FEMA IA) and is 61% in below-median-income tracts vs. 43% above.

## 2. The model

Household $i$ faces an aggregate future climate state $\omega$ and an idiosyncratic flood shock $\xi$, and chooses insurance $q_i$, mitigation $m_i$ (cost $\kappa_i$), and location $x_i$ (amenity $\Gamma_i$). With subsidy $s$, the paid premium is $\tilde P_i(\omega)=(1-s)P_i(\omega)$, and a fixed fraction $f$ of uninsured losses is covered by FEMA, financed by state-specific lump-sum taxes $T(\omega)$:

$$c_i(\omega,\xi) = y_i + \Gamma_i(x_i) - \kappa_i(m_i) - q_i\tilde P_i(\omega) - (1-f)(1-q_i)L_i(\omega,\xi) - T(\omega).$$

Premiums decompose as $P_i(\omega)=\bar P(\omega)+a_i+\varepsilon_{i\omega}$: aggregate scenario risk (uninsurable in the cross-section), a predictable household fixed effect (insuring it is "just redistribution"), and idiosyncratic reclassification risk $\varepsilon_{i\omega}$ — the only component a subsidy genuinely insures. The planner balances the budget within each $\omega$ (aggregate climate risk cannot be shifted across states) and maximizes $\sum_i V_i(s)$.

Under assumptions A1–A5 (shadow value orthogonal to $\omega$; no selection into insurance, citing Wagner 2022; no redistribution on $a_i$; binary coverage; mitigation/location responses only among the insured), **Proposition 1** gives the optimality condition:

$$\underbrace{(1-s)\sum_i \mathrm{Cov}_\omega\!\big(u_i'-\bar u'(\omega),\, q_i^*\varepsilon_{i\omega}\big)}_{\text{reclassification-risk insurance value}} \;+\; \underbrace{\bar\mu\,\mathbb{E}_\omega\Big[\sum_i f\,\bar P_i\,\eta_i^q\Big]}_{\text{FEMA savings}} \;=\; -\,\bar\mu\,\mathbb{E}_\omega\Big[\underbrace{\sum_i s\,\bar P_i\,\eta_i^q}_{\text{coverage FE}} + \underbrace{\sum_i s\,\mathbb{E}_\omega\big[\tfrac{\partial P_i}{\partial m}\big]\eta_i^m}_{\text{mitigation FE}} + \underbrace{\sum_i s\,\mathbb{E}_\omega\big[\tfrac{\partial P_i}{\partial x}\big]\eta_i^x}_{\text{location FE}}\Big].$$

The general version (**Proposition 2**, Appendix C.1) adds selection and $a_i$-redistribution terms, and — important for us — writes the coverage fiscal externality as $\sum_i (s-f)P_i(\omega)\,\eta_i^q$: a household switching into insurance costs the subsidy $s$ but *saves* expected FEMA outlays $f$, the exact analogue of our $(s-a)$ fiscal-externality term. The economics of the interior optimum (their eq. 5): FEMA savings are constant in $s$, reclassification-risk value declines roughly quadratically, and all three fiscal externalities are zero at $s=0$ and scale linearly in $s$ (Harberger logic) — so benefits dominate at low $s$ and costs at high $s$.

Their MVPF (Section 9.6.3):

$$\mathrm{MVPF}(s)=\frac{q\bar P + q\cdot V_{\mathrm{reclass}}(s)}{q\bar P - \eta_q|\beta_{\mathrm{uncond}}| + \eta_q\bar P s + \bar P E_m \Delta_{\mathrm{haz}} s + \Delta P_{\mathrm{move}}E_x s + \eta_q(\bar P A_N - A_F|\beta_{\mathrm{uncond}}|)},$$

with $\beta_{\mathrm{uncond}}\approx-\$1{,}192$ per house-year per unit coverage. The FEMA-savings term $-\eta_q|\beta_{\mathrm{uncond}}|$ in the *denominator* is what makes the MVPF infinite for small $s$: the net fiscal cost of the first subsidy dollars is negative.

## 3. The five estimated parameters

| Parameter | Estimate | Identification |
|---|---|---|
| FEMA spillover $\beta_{\mathrm{cond}}$ | −\$173 (OLS) / **−\$216 (IV)** per house per 1pp coverage, conditional on flood; implies $f\approx 0.133$ | County-flood panel 2010–, flexible damage controls; IV = Gallagher-style neighbor-county flood in past 5 years (salience shifts own-county coverage by ~3pp off an 18pp base) |
| Demand semi-elasticity $\eta_q$ | **−0.32** (−0.25 in SFHA); intensive margin ≈ 0 (~1%) | FOIA policy-level panel with both billed and full-risk RR2.0 premiums; *within-policy* variation from the 18%/yr transition cap, contract FE |
| Reclassification risk | Idiosyncratic SD of 2070 premiums **\$1,842**; value of a 50% subsidy **\$207**/household (CARA $\gamma=5\times10^{-4}$) | NFIP universe × 40 climate scenarios (8 Gori GCMs × 5 ISIMIP GHMs, SSP2-4.5/5-8.5); premium-prediction model; two-way demeaning isolates $\varepsilon_{i\omega}$; $V=\mathrm{CE}_\omega(\varepsilon_{i\omega})-\mathrm{CE}_\omega((1-s)\varepsilon_{i\omega})$ |
| Mitigation elasticity $\eta_m$ | **0.30–0.38** (elevation ↑7–11pp for higher price shocks); ≈0.075 reweighted to US covariates | Florida Elevation Certificates since 2017; DiD very-high vs. high risk (in SFHA) and moderate vs. low (outside) |
| Location elasticity $\eta_x$ | **−0.0077** (0.77% of population moves; rent-elasticity ≈ 0.20) | USPS occupied-address tract panel; tracts with median RR2.0 increase vs. decrease, event study |

The calibrated per-house-year magnitudes at a 1% price cut make the ranking transparent: FEMA savings \$3.84 vs. coverage FE \$2.80 (at $s=\tfrac12$), mitigation FE \$1.18, location FE \$0.04. Migration and mitigation moral hazard — the intended benefits of RR2.0 — are an order of magnitude smaller than the fiscal spillover and reclassification channels.

## 4. The misperception extension (Appendix C.2 / B.22) — closest to our territory

Households underweight expected losses by a factor $\lambda_i$, choosing as if the loss were $(1-\lambda_i)L_i$; the planner uses true losses. The resulting internality wedges are

$$\Delta_i^q=\lambda_i(1-f)\bar P_i,\qquad \Delta_i^m=\lambda_i(1-f)(1-q_i^*)\Big(-\tfrac{\partial\bar P_i}{\partial m}\Big),\qquad \Delta_i^x=\lambda_i(1-f)(1-q_i^*)\Big(-\tfrac{\partial\bar P_i}{\partial x}\Big),$$

entering the planner FOC as $-\tfrac{1}{1-s}\mathbb{E}_\omega\big[\sum_i \mathbb{E}_\xi u_i'\,(\Delta_i^q\mathcal{E}_i^q+\Delta_i^m\mathcal{E}_i^m+\Delta_i^x\mathcal{E}_i^x)\big]$. With binary full coverage, the mitigation/location internalities vanish (insured households ignore their risk level anyway), leaving only the coverage internality — so misperception *unambiguously* raises $s^*$. Quantitatively (B.22, CARA small-risk approximation): with uniform underperception $k_R=0.57$ (from Bakkensen–Barrage 2022) the wedge is

$$\Delta^{B,R}\approx(1-k_R)(1-f)P_i+\tfrac{\gamma}{2}(1-f)^2L_f^2\big[p(1-p)-k_Rp(1-k_Rp)\big]\approx\$4{,}461$$

per newly insured household-year; FEMA over-perception ($k_F=1.5$) adds \$1,362. Result (Table A29): $s^*$ jumps from 52% to **89–100%**. Note what this is *not*: there is no distribution of beliefs, no endogenous marginal-belief threshold, no heterogeneity-driven asymmetry between instruments — $\lambda$ is one number applied to everyone, in an appendix robustness exercise.

## 5. Mapping to our framework

Their static skeleton is recognizably the same model as our baseline, which is both validating and threatening. Notation correspondence:

| Ours | Theirs | Comment |
|---|---|---|
| $s$ (premium subsidy) | $s$ | identical |
| $a$ (relief fraction) | $f$ (FEMA share of uninsured loss) | **theirs is fixed, ours is optimized** — the central difference |
| $\varepsilon,\ \partial I/\partial s$ | $\eta_q$ | their −0.32 is the best-identified voluntary estimate; −0.25 in SFHA confirms mandate attenuation |
| $(s-a)pd\cdot\partial I/\partial s$ (fiscal externality of switchers) | $(s-f)P_i\eta_i^q$ (Prop. 2 coverage FE) | same term, same economics |
| $(p-q^*)\Delta u$ (internality at the margin, exact) | $\Delta^q=\lambda(1-f)\bar P$ (uniform, linearized + CARA quadratic) | ours is heterogeneous and evaluated at the *endogenous* margin; theirs is homogeneous and inframarginal |
| $q\sim F(q)$, threshold $q^*(s,a)$ | absent | no belief distribution anywhere |
| Crowd-out $\partial I/\partial a\propto q^*$ (dampened) | absent | relief generosity never varies, so relief-side moral hazard is never modeled |
| Adaptation subsidy $b$; $\partial k^{IA}/\partial s<0$ | mitigation FE $s\,\mathbb{E}[\partial P/\partial m]\eta_m$ | same channel; they estimate $\eta_m$, we derived the premium-adjusted mechanism |
| Two-region model, location internality | location FE, $\eta_x=0.0077$ | they estimate the number our two-region note needs |
| — | reclassification risk (dynamic $\omega$) | genuinely new dimension we don't have |

**Where they answer questions we left open.** They supply the missing empirical objects for several of our TODOs: the first credible estimate of the insurance→relief fiscal offset ($f\approx13.3\%$ — notably above our IA-grant-based $a\approx4$–$7\%$, because their measure folds in SBA, HMGP and GSE channels; this discrepancy needs reconciling in our calibration); a clean within-property demand elasticity; a migration elasticity that lets us put a *number* on the sorting bound we planned from the two-region model (their location FE is tiny — \$0.04 per house-year — which supports deferring the full spatial model); a mitigation elasticity for our adaptation module; and the empirical justification for binary coverage (intensive margin ≈ 0). Their Table A29 also independently confirms our qualitative direction: underperception makes ex ante subsidies much more attractive.

**Where we do things they cannot.** First, the **policy space**: they choose $s$ given fixed $f$, explicitly flagging (Panel C, conclusion) that FEMA generosity is the variable that most moves their answer — but they never optimize over it. Our joint $(s,a)$ problem, the $\mathrm{MVPF}_s$ vs. $\mathrm{MVPF}_a$ comparison, and the optimal *mix* are outside their paper. Second, **belief heterogeneity as a distribution**: their behavioral treatment is a uniform scalar wedge; there is no marginal household, no recovery of $f(q^*)$ from elasticities, and therefore no counterpart to our central mechanism — that relief's crowd-out is weak *because* the households at the take-up margin underweight flood risk ($\partial I/\partial a\propto q^*<p$). In their framework the question "how much does relief crowd out insurance" is answered by citation (Kousky et al. 2018, Deryugina–Kirwan), not by the model. Third, our exact utility-based internality $(p-q^*)\Delta u$ at an endogenous margin vs. their linearized inframarginal wedge.

**Consistency check between our numbers and theirs.** Their $s^*=52\%$ at a current $s\approx47\%$ says the subsidy MVPF is roughly 1 at the status quo — precisely our finding ($\mathrm{MVPF}_s\approx1.00$–$1.05$ at $s=0.47$). No contradiction: at an interior optimum MVPF $=1$ by construction. The tension is subtler and productive: their infinite-MVPF result at low $s$ is driven by a FEMA offset ($f=0.133$) about twice our relief calibration, and their framework cannot ask our headline question — whether the *marginal public dollar* does better as relief than as subsidy ($\mathrm{MVPF}_a\approx1.36>\mathrm{MVPF}_s$). Adopting their larger $f$ in our model would mechanically raise both our $\mathrm{MVPF}_s$ (bigger relief savings per crowd-in) and the fiscal cost of relief itself; this needs to be rerun, not assumed.

## 6. Weak points in G&S worth recording (for later use)

Their central CARA coefficient $\gamma=5\times10^{-4}$ comes from the deductible-choice literature (Cohen–Einav, Sydnor) and implies enormous relative risk aversion at annual-consumption scales; the reclassification-risk value (and the misperception wedges, which inherit the $\tfrac{\gamma}{2}L_f^2$ term) are sensitive to it, although $s^*$ is not, because the FEMA channel dominates. The IV rests on neighbor-flood salience being excludable from own ex post spending — they defend it extensively (political controls, fund-depletion checks, alternative damage measures) but it remains a salience instrument, which sits awkwardly with a rational-household baseline: the same evidence implies the belief instability that only enters their model as an appendix wedge. $f=0.133$ is inferred from the spillover coefficient rather than measured directly, and their own Bakkensen–Barrage elicitation comparison (mean expected government coverage ≈12%) suggests households' *perceived* $f$ is close to their estimated actual $f$, which mildly undercuts the $k_F=1.5$ over-perception calibration. The mitigation elasticity is Florida-specific (their own reweighting cuts it by ~78%). Assumption A2 (no selection) leans on one paper. And everything is partial equilibrium in housing: no price capitalization, no incidence on landowners, which their own migration result implies is where the long-run action is.

Nothing here changes their qualitative conclusion, but each point matters for how our paper positions its complementary machinery — to be discussed when we turn to positioning and next steps.