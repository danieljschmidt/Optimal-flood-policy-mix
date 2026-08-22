# Calibration the Disaster-Aid Parameter $a$

This note lays out two approaches to calibrating $a$, the model's disaster-relief parameter. It is simultaneously the household's benefit rate and the government's cost rate.
---

## 1. Two ways to get to $a$

### Method 1 — G&S's spillover-regression approach

Gruber & Solomon estimate $a$ (their $f$) indirectly, off
a behavioral response: **how much does ex post federal disaster-aid spending to a county fall, conditional on a flood, when NFIP insurance coverage in that county is one percentage point higher?** The logic is substitution, a household with more insurance needs less government aid after a flood, so the *decline* in aid spending as coverage rises reveals how generous that aid is.

Concretely:
- They run a county-flood panel regression of ex post disaster-aid spending per house on NFIP coverage, conditional on flooding, with flexible damage controls.
- Because coverage is not randomly assigned (higher-risk-awareness counties may have both more coverage and different aid needs), they instrument for local coverage using flooding in *neighboring* counties in the past five years, a salience shock that shifts a county's own coverage without directly affecting its own damage.
- Their preferred (IV) estimate is $\beta_{\text{cond}} \approx -\$216$ per house per 1pp of coverage, conditional on a flood.
- They convert that spillover coefficient into a generosity rate via $f = |\beta_{\text{cond}}|/(\sigma_{PDD}\bar P)$ — normalizing dollars-per-percentage-point into a fraction of damage — landing on $f \approx 0.133$.

The result is flood-specific by construction (the panel is conditioned on flooding), so it needs no all-hazard correction. But it is a **substitution/fiscal-response** rate, not a direct per-dollar-of-damage transfer rate: it picks up every channel through which more insurance reduces total federal outlays, not just "how much of a household's damage does the government hand back."

### Method 2 — bottom-up, program-size approach

An alternative approach is to identify which disaster-aid programs actually match $a$'s definition in the model (paid directly to households, no repayment, sized against their damage), sum their dollar flows nationally, and divide by an estimate of national
flood damage:

$$a = \frac{\text{program \$/yr}}{\text{annual flood damage \$/yr}}$$

This requires three corrections the spillover method doesn't need: (1) picking the right flood-damage denominator (narrow/residential/broad), (2) scaling program totals down from all-hazard to flood-only spending, since FEMA/SBA totals cover every disaster type, not just floods (a 9.3–88.6% flood-share range, computed from FEMA's own data — see Section 4), and (3) restricting that denominator to its uninsured-only share, since aid is only ever paid to uninsured households (≈82% of residential flood damage — see Section 4). It's a direct accounting exercise rather than an estimated behavioral response — simpler, but its accuracy depends entirely on correctly scoping which programs belong in the numerator (Section 3 below).

---

## 2. The four programs in play

G&S's \$216 bundles four distinct federal channels. Their paper's Appendix Tables A2–A6 report the
exact IV decomposition:

| Program | What it is | Paid to | Repaid? | Share of the \$216 spillover |
|---|---|---|---|---|
| **FEMA IHP** (Individuals and Households Program) | Post-disaster grants (Housing Assistance + Other Needs Assistance) | Households, directly | No | −\$183.4 (≈85%) |
| **HMGP** (Hazard Mitigation Grant Program) | Funds mitigation projects — elevations, buyouts, infrastructure hardening | Mostly to state/local governments and, via them, some homeowners | Mostly no, but not a damage payment | −\$21.4 (≈10%) |
| **SBA disaster loans** | Low-interest loans for real/personal property | Households, directly | Yes | −\$9.3 (≈4%) |
| **GSE mortgage channels** (Fannie Mae / Freddie Mac) | Fiscal cost of foreclosures avoided when insurance covers a loss | Households, indirectly (avoided default, not cash) | n/a | −\$1.7 / +\$0.5, one wrong-signed and both statistically insignificant |

All four move when insurance coverage moves, which is exactly why G&S's regression picks them all
up — their target quantity is "total federal fiscal exposure to under-insurance," and every channel
belongs in that.

---

## 3. Why this project scopes down to two programs

This model's $a$ is not "total federal fiscal exposure" — it has to be a single number that is
*simultaneously* the household's benefit rate and the government's cost rate. Checked against that requirement, only two of the four programs qualify:

- **FEMA IHP — included.** A no-repayment grant paid straight to the household, sized to their
  damage. Its face value equals both the household's benefit and the government's cost, exactly
  the dual role $a$ plays in the model.
- **SBA loans — included, but revalued.** A loan's *face value* overstates household benefit
  (it must be repaid); the true benefit is only the interest-rate subsidy, roughly 13 cents per
  dollar lent. So SBA is included at its **subsidy-equivalent** value, not face value.
- **HMGP — excluded.** It funds forward-looking mitigation and buyouts, not compensation for
  realized flood damage. It isn't a payment to a flooded household sized against their loss; it's a
  different policy lever (risk reduction) that the model doesn't currently have a parameter for.
  Bundling it into $a$ would conflate "cash paid after a flood" with "spending that lowers future
  flood risk."
- **GSE forbearance — excluded.** It's payment-deferral, not a cash grant, so face value doesn't
  represent benefit any more than SBA's does — and unlike SBA, there's no available data to convert
  it to a benefit-equivalent value, so it can't currently be quantified at all.

**The difference from G&S:** G&S bundle all four because their object is "how much does total federal disaster spending respond to insurance", every channel that responds belongs in that number, however it's structured. This project's $a$ is narrower and stricter: it has to be a
clean transfer rate where the dollar the household receives *is* the dollar the government spends, because the model uses $a$ on both sides of its welfare and budget equations, and because, unlike G&S, who hold $f$ fixed, this project treats $a$ itself as the object being optimized.

---

## 4. Computing $a$ under both methods

**Method 1 (G&S spillover), restricted to the same two programs.** $f$ scales linearly in
$\beta_{\text{cond}}$, and the exact per-program split is known from Appendix Tables A2–A6 (Section 2), so
restricting the \$216 total to IHP's \$183.4 gives:

$$f_{\text{IHP}} = 0.133 \times \frac{183.4}{216} \approx 0.113$$

Adding SBA back at its subsidy-equivalent value (13% of its \$9.3 decomposed spillover, ≈\$1.2):

$$f_{\text{IHP+SBA-equiv}} = 0.133 \times \frac{183.4 + 1.2}{216} \approx 0.114$$

So on this project's scope, the G&S method gives **$f \approx 0.11$**, essentially unchanged by
whether SBA is included.

**Method 2 (bottom-up), scoped to IHP + SBA subsidy-equivalent, residential denominator.**

- **Program size, all-hazard:** IHP ≈\$1.55bn/yr; SBA subsidy-equivalent ≈\$0.18bn/yr (13¢ per
  dollar lent, on ≈\$1.4bn/yr face value) — combined ≈\$1.73bn/yr.
- **All-hazard → flood-only correction:** IHP totals cover every disaster type, not just floods, so
  they're scaled down by flooding's share of all-hazard IHP spending. This is now computed directly
  from FEMA's own data (OpenFEMA `FemaWebDisasterSummaries` × `DisasterDeclarationsSummaries`,
  summing `totalAmountIhpApproved` by disaster `incidentType`, FY2003–2024 to match the CRS
  program-size window — \$37.4bn total, close to CRS's \$33.2bn) rather than assumed from literature
  ranges:
  - **Primary-hazard convention** (only disasters FEMA labels `Flood`): **9.3%** of all IHP dollars.
  - **Flood-present convention** (`Flood` + `Hurricane` + `Tropical Storm` + `Severe Storm` +
    `Typhoon` + `Dam/Levee Break` — the perils whose damage is substantially flood-driven): **88.6%**.
    `Hurricane` alone is 65% of all IHP dollars and is the swing category: whether it counts as
    "flood" drives almost the entire gap between the two conventions.
  - Neither bound is exactly right, primary-hazard undercounts (major floods are usually filed
    under `Hurricane`), flood-present overcounts (hurricane IHP grants include wind damage too), so
    the **midpoint, 48.9%**, is used as the point estimate, with the two computed bounds reported as
    a genuine (not assumed) sensitivity range.
- **Denominator:** three candidates appear in the literature, each covering a different population:
  - *Narrow* (\$9.4bn, CBO) — flood damage to homeowners with federally backed mortgages only.
  - *Residential* (≈\$20bn, First Street Foundation) — flood damage to all U.S. residential
    property, from physical flood-risk modeling (fluvial/pluvial/coastal), independent of mortgage
    status or FEMA flood-zone designation.
  - *Broad* (\$46bn, CBO) — residential + commercial property + infrastructure + business
    interruption.

  **Residential is preferred.** The model's household has no mortgage-backing status as a state variable, so the narrow denominator would arbitrarily exclude cash buyers, privately-financed mortgages, and renters shrinking the denominator without a matching shrink in who's IHP-eligible, which mechanically inflates $a$. The model also has no commercial-property or public-infrastructure agent, so the broad denominator's extra \$26bn is spending on a population outside the model, which would deflate $a$ for no good reason.
- **Insured/uninsured correction:** aid is only ever paid to *uninsured* households but the \$20bn denominator is *total* residential damage (insured + uninsured), since First Street's estimate is a physical-risk figure independent of coverage status. The fix only needs the take-up rate: G&S's PDD-county sample has an **18% take-up rate**, so — assuming insured and uninsured houses have similar average damage — **≈82% of residential flood damage belongs to uninsured households**. The effective denominator is therefore \$20bn × 0.82 ≈ **\$16.4bn/yr**, not \$20bn. (A robustness check using the project's own take-up rate instead of G&S's sample-specific 18% appears in Section 5.)

$$a = \frac{\text{flood share} \times \text{program \$/yr}}{\$16.4\text{bn/yr}}$$

**IHP alone** (\$1.55bn/yr):

| Flood share | Flood-adjusted \$/yr | $a$ |
|---|---|---|
| 9.3% (primary-hazard) | \$0.14bn | 0.009 |
| 48.9% (midpoint) | \$0.76bn | **0.046** |
| 88.6% (flood-present) | \$1.37bn | 0.084 |

**IHP + SBA subsidy-equivalent** (\$1.73bn/yr):

| Flood share | Flood-adjusted \$/yr | $a$ |
|---|---|---|
| 9.3% (primary-hazard) | \$0.16bn | 0.010 |
| 48.9% (midpoint) | \$0.85bn | **0.052** |
| 88.6% (flood-present) | \$1.53bn | 0.093 |

SBA's inclusion barely moves the number at any flood share.

| | Method 1: G&S spillover, same scope | Method 2: bottom-up |
|---|---|---|
| **Value** | **0.11** | **0.052** (range 0.010–0.093) |
| Ratio to Method 1 | — | ≈2.1× smaller |

Program bundling remains a real but secondary source of the disagreement, moving the aid parameter from 0.13 to 0.11, most of the gap is that a
spillover coefficient captures *substitution* (NFIP-payout offsets, correlated triggers, other
general-equilibrium effects on FEMA's response), not a clean per-dollar-of-damage transfer, even
once scoped to the same two programs.

---

## 5. Robustness checks

**Cross-check — a direct estimate from G&S's own aid levels.** G&S's paper reports flood-weighted
average *aid* levels per house, not just the spillover coefficient: FEMA IHP at \$736/house, SBA
loans at \$967/house face value (≈\$125.71/house at the 13¢-per-dollar subsidy-equivalent rate used
throughout this note). Since aid effectively only reaches the uninsured (duplication-of-benefits
rules), rescaling each by the same 82% uninsured share used in Section 4 (take-up rate only, per that
section's correction) and dividing by the \$29,267 average total damage per flooded house gives:

$$
\begin{aligned}
a_{\text{IHP-only, G\&S-levels}} &= \frac{736/0.82}{29{,}267} \approx 0.031 \\
a_{\text{IHP+SBA-equiv, G\&S-levels}} &= \frac{861.71/0.82}{29{,}267} \approx 0.036
\end{aligned}
$$

This is a genuinely independent third route to $a$, built entirely from G&S's own per-house sample averages, using none of the CRS national totals or First Street's residential-damage denominator that Method 2 in Section 4 relies on. It lands close to Method 2's own range (0.010–0.093, midpoint 0.052): two structurally different data sources converge on the same rough magnitude (≈0.03–0.05) rather than diverging the way Method 1's spillover-based 0.11 does.
Caveats: it implicitly assumes damage-per-house doesn't differ much between insured and uninsured
subgroups (if insured properties, concentrated in the highest-risk zones, suffer more raw damage on
average, true uninsured-only damage would be lower than \$29,267 and this estimate would be biased
down), and it inherits G&S's PDD/IHP-authorized-county sample selection, likely skewed toward more
severe, officially recognized floods, rather than reflecting all flood damage nationally.

| | Method 1: G&S spillover, same scope | Method 2: bottom-up | Cross-check: G&S aid levels |
|---|---|---|---|
| **Value** | **0.11** | **0.052** (range 0.010–0.093) | **0.031–0.036** |
| Ratio to Method 1 | — | ≈2.1× smaller | ≈3.1–3.5× smaller |

**Further check — take-up rate consistency with the project's own code.** The 82% uninsured-damage
share in Section 4 rests on G&S's *own sample's* 18% take-up rate. But `code/params.py` calibrates the
project's primary household take-up rate at `I_OBS = 0.30` (FEMA/Dixon, high-risk), explicitly
listing G&S's 0.18 as a *competing alternative* the project didn't adopt as its default. Recomputing with the project's own 0.30:

$$
\begin{aligned}
\text{uninsured share} &= 1-0.30 = 70\% \\
\text{denominator} &= \$20\text{bn}\times0.70 = \$14.0\text{bn}
\end{aligned}
$$

| Take-up used | Uninsured share | Denominator | $a$ (IHP+SBA, midpoint) | $a$ range (9.3–88.6% flood share) |
|---|---|---|---|---|
| G&S sample (0.18) — used in Section 4 | 82% | \$16.4bn | 0.052 | 0.010–0.093 |
| Project's own `I_OBS` (0.30) | 70% | \$14.0bn | **0.060** | **0.011–0.109** |

Using the project's own take-up rate pushes the midpoint up further, to ≈0.060, a lower uninsured share means a smaller "uninsured damage" base, and the same aid dollars are a larger fraction of a smaller pie. Neither pairing is a clean population match, though: `I_OBS` targets a "high-risk" subpopulation while the \$20bn denominator spans all U.S. residential property, and G&S's 18\% is specific to their PDD/IHP-authorized-county sample, so this is a genuine open sensitivity, not a resolved discrepancy. Around $a \approx 0.052$–$0.060$ (IHP+SBA) is the resulting midpoint range once this is factored in.

---

## 6. Recommendation

**Use Method 2 (bottom-up), $a \approx 0.052$ (range 0.010–0.093), as the primary calibration.** It
directly targets the quantity the model actually needs, a rate that is *both* the household's benefit and the government's cost by construction, since it's built from program dollars that are paid straight to households with no repayment. Method 1's spillover estimate is contaminated for this purpose by channels beyond direct relief (NFIP-payout interactions, correlated triggers, general-equilibrium effects), so even scoped to the right two programs, it likely overstates the pure transfer rate rather than just measuring it more precisely. Section 5's cross-check (0.031–0.036, built entirely from G&S's own per-house aid levels rather than CRS/First-Street national totals) lands in the same rough neighborhood as Method 2 rather than near Method 1's 0.11, which is independent support for Method 2's magnitude over Method 1's.

That said, Method 2 has its own weak points, like the flood-share correction (the all-hazard → flood-only adjustment it needs and Method 1 doesn't, genuinely wide, 9.3–88.6%, driven almost entirely by whether `Hurricane`-labeled IHP spending counts as flood relief) and the insured/uninsured correction (≈82%, resting on G&S's single sample-specific take-up rate rather than a direct national estimate, Section 5's further check shows this moving to ≈0.060 under the project's own take-up rate). Both remain sources of uncertainty in the 0.052 figure.
Report $f_{\text{IHP+SBA-equiv}}\approx0.114$ alongside $a\approx0.052$ as a **sensitivity/upper-bound
case** rather than discarding it. If the true fiscal externality of relief runs closer to G&S's
number, that has first-order consequences for the MVPF/budget side of the model regardless of which
estimate anchors the household-benefit side. The ~2.2× gap between the two methods, even after
matching program scope, is worth flagging explicitly in the paper rather than presented as resolved.
