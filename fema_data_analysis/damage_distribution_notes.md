# FEMA damage distribution — what the script does, and what must be decided before calibrating

*Status: live. Produced by `run_compute_damage_distribution.py`; outputs in
`fema_data_analysis/output/`. This is TODO 6 in `daniel_notes/handover_notes.md`
("swap in the FEMA damage distribution"). The distribution is **saved but not wired into
the model** — the decisions in §3 change what should be fed to `configure_damage`.*

---

## 1. What is computed

The empirical distribution of

    D_ratio = buildingDamageAmount / buildingPropertyValue,  clipped to [0, 1]

over single-family SFHA claims, discretized into 20 equal-width bins of width 0.05, each
represented by its conditional mean. Base sample: `occupancyType IN (1, 11)`, rated flood
zone `A*` or `V*`, `yearOfLoss >= 2000`, denominator between \$10k and \$10M.

Output files, one row per bin with columns `damage_ratio_lower`, `damage_ratio_upper`,
`damage_ratio_mean` (the conditional mean — the value the model should use), `weight`,
`n_claims`:

| file | n | mean | CV | share ≥ 0.9 |
|---|---|---|---|---|
| `damage_distribution_main.csv` | 812,938 | 0.304 | 0.994 | 7.5% |
| `damage_distribution_excl_katrina.csv` | 712,066 | 0.252 | 1.021 | 2.8% |
| `damage_distribution_since_2010.csv` | 481,666 | 0.262 | 0.972 | 2.4% |
| `damage_distribution_replacement_cost.csv` | 812,155 | 0.243 | 1.046 | 2.5% |
| model placeholder, baseline | — | 0.15 | 0.86 | — |
| model placeholder, robustness | — | 0.15 | 1.3 | — |

`damage_distribution_summary.csv` collects those moments. Two figures:
`damage_distribution_main.png` (histogram of the main specification) and
`damage_distribution_comparison.png` (all five discretized distributions in one line chart).

The discretization is faithful: at 20 bins it reproduces the raw mean exactly and the raw
CV to within 0.002.

**Headline for the calibration:** the empirical CV sits in a tight band of 0.91–1.05 across
every variant — between the two placeholder values, and nearer the 0.86 baseline than the
1.3 robustness case. That is the robust finding. The mean is far less stable (0.24–0.33)
and is the live problem — see §3.1 and §3.4.

---

## 2. Fixed in the pipeline

Relative to the previous version of the script:

- **Database path** pointed at `C:\Data\FEMA\fema.db`, which no longer exists; the live
  database is `C:\Users\dschm\Documents\Data\FEMA\fema.db` (the path
  `adaptation_analysis/run_adaptation_analysis.py` already used).
- **Sample definition now matches the adaptation analysis.** The old filter was
  `primaryResidenceIndicator = 1`; it is now `occupancyType IN (1, 11)`. The old column is
  not populated consistently over time — the share flagged primary residence is 0% for
  1970s losses, 2.4% for the 1980s, 34% for the 1990s and ~70% from 2000 on, with no NULLs
  anywhere, so unreported has been coerced to false. Filtering on it was a disguised
  "loss after ~2000" filter. The year window is now explicit instead.
- **Zero and implausible denominators are dropped, not absorbed.** 17,646 claims in the
  single-family SFHA sample report `buildingPropertyValue = 0`. Where damage was positive
  the ratio was `inf`, and `clip(0, 1)` silently converted each one to exactly 1.0 — a
  total loss. In the old sample that was 8,176 claims, or 13% of the entire top bin. A
  further 12,591 have denominators outside \$10k–\$10M (the raw column has a median of
  \$132k against a mean of \$1.5M, and a mean of \$3.4M for 1990s losses); those inflate
  the *bottom* bin instead.
- **NaN is no longer silently dropped.** 7,602 claims were 0/0. `discretize_conditional_means`
  excluded them through failed comparisons without reporting it, which is why the old
  printed bin counts summed to 779,933 against a query returning 787,535 rows.
- **Every exclusion and clip is now counted and printed**, and the bins are half the old
  width (20 rather than 10).

Combined effect on the two moments the model calibrates on: mean 0.298 → 0.304, CV
1.03 → 0.99. The mean barely moves, but the corrections are concentrated in the tail,
which is the part of the distribution that drives the result (per `handover_notes.md` §2,
"relief's edge grows with the damage tail").

---

## 3. Not fixable in the data pipeline — decisions needed

### 3.1 The denominator is building value, not wealth

The model's `D` is a share of household wealth `w` (normalized to 1, cross-checked at
`w ≈ $195k` with `MEAN_D = 0.15` giving G&S's `L_f = $29,267`). `buildingPropertyValue` is
the adjuster's *actual cash value of the building alone* — depreciated, and excluding land
and contents. It is therefore a strictly smaller base than wealth, and the ratio is biased
up as a measure of `D/w`.

The shape is still the right object (it is the standard physical damage ratio); what needs
fixing is the scale. With `κ = building value / wealth`:

    E[D]/w = κ × 0.304

At the sample's own magnitudes (median ACV \$132k, median replacement cost \$175k) against
`w ≈ $195k`, κ ≈ 0.68, giving **E[D]/w ≈ 0.21**. Running the same calculation on the
replacement-cost denominator (mean ratio 0.243, κ ≈ 0.90) gives ≈ 0.22 — reassuringly
close, so the two value concepts agree once each is scaled by its own base.

So the apparent 2× discrepancy against `MEAN_D = 0.15` is mostly a denominator artifact,
but not entirely: **the reconciled figure is ~0.21, still about 40% above the placeholder.**

Two consequences to decide on:

1. Whether `MEAN_D` moves from 0.15 to ~0.21. It should, unless the gap is attributed to
   claim-filing selection (§3.2).
2. `D_max` is currently 1.0. Under the rescaling, total destruction of the building is a
   loss of κ ≈ 0.68 of wealth, not 1.0. Leaving `D_max = 1.0` while rescaling the mean
   would misstate the support.

**Why the replacement-cost variant has almost no mass near 1.** The two value concepts are
*not* interchangeable, and the gap between them is almost exactly the width of the top bin.
`buildingPropertyValue` is actual cash value — replacement cost *minus depreciation* — and
in this sample the ratio ACV / replacement cost has median **0.80** (25th–75th percentile
0.74–0.88). Dividing by a base that is ~20% larger shifts a claim sitting at 0.95 of ACV
down to ~0.76 of replacement cost, straight out of the `[0.9, 1]` bin. Landing in the top
bin on a replacement-cost basis requires the damage ratio to be high *and* the building to
be barely depreciated, which is only 33% of the ACV-basis total losses.

The rescaling is the whole story, and it can be shown exactly: multiplying each claim's ACV
damage ratio by its own ACV/RC ratio — a pure change of base, nothing else — reproduces a
top-bin share of **2.52%** against the 2.53% actually observed on the replacement-cost
denominator. So the two variants carry the same information about relative damage; they
differ only in what "total loss" is measured against.

**A second, less comfortable finding.** 28,128 claims (3.5% of the sample, and 46% of the
entire top bin) have `buildingDamageAmount` exactly equal to `buildingPropertyValue`, while
only 949 claims (0.12%) report damage *above* it. Damage therefore appears to be censored
at the reported cash value rather than measured independently of it — for a total loss the
adjuster records the ACV. The same claims have a median ratio of 0.895 on a replacement-cost
basis, and settlements coded on an ACV basis (`replacementCostBasis = A`) show both a higher
pile-up (4.5% vs 1.6%) and double the top-bin share (9.1% vs 4.9%) relative to
replacement-cost settlements. Dropping the pile-up cuts the ACV top-bin share from 7.5% to
4.3%.

So the mass point at `D = 1` in the main specification is partly an accounting convention,
not a physical fact about floods. That matters more here than it normally would: under
CRRA, mass at total loss is exactly where relief's insurance value is generated. The
replacement-cost variant is the natural robustness check *against this artifact* — which is
a better reason to carry it than "an alternative denominator".

### 3.2 The distribution is conditional on a claim, not on a flood

The model wants `G(D)` conditional on a flood event of annual probability `p`. The claims
data give damage conditional on an insured household *filing a claim that got adjusted*.
Two selection layers sit in between: the household must be insured, and the loss must be
worth filing. Losses below the deductible are essentially absent, so the left tail is
truncated and the mean is biased up — plausibly the residual gap in §3.1.

`p` and `G` have to be defined consistently:

- If `p` is **claim frequency** (paid claims per policy-year in the target zone — option (a)
  in `model_parameters.md` §1b, and computable from this same database), then "flood event"
  means "claim event" and the conditioning matches. This is the internally coherent pairing
  and it is the one I would take.
- If `p` stays the hydrological 0.02, then `G` ought to include the small and no-damage
  events that never generate claims, and the empirical mean overstates `E[D | flood]`.

This is the same reconciliation already flagged as the standing `p` discussion point, now
with a second reason to resolve it: it is not only about the level of `p`, it determines
whether the damage distribution is measuring the right conditional object.

### 3.3 The sample pools adapted and unadapted homes

The main sample is 33% elevated, and the two groups differ sharply (one-off diagnostic —
no longer shipped as a variant, since the adaptation instrument is parked):

| | n | mean | CV |
|---|---|---|---|
| not elevated | 541,637 | 0.333 | 0.905 |
| elevated | 271,301 | 0.248 | 1.200 |
| pre-FIRM | 556,617 | 0.325 | 0.917 |
| post-FIRM | 256,321 | 0.259 | 1.185 |

The pooled distribution embeds today's 33% elevation rate. If `D` is meant to be damage for
the *unadapted* baseline household, the non-elevated row is the right target — and note it
moves the mean *up* (0.333) while lowering the CV (0.905). The adaptation instrument is
parked (`handover_notes.md` §9), so pooling is defensible for now, but the choice should be
stated rather than inherited, especially since the adaptation analysis in the sibling folder
is built on exactly this margin.

### 3.4 One storm drives the tail

This is the sharpest sensitivity in the whole exercise, and it is not really about the time
window — it is about Hurricane Katrina specifically:

| variant | n | mean | CV | share ≥ 0.9 |
|---|---|---|---|---|
| main (≥ 2000) | 812,938 | 0.304 | 0.994 | 7.5% |
| main excluding Katrina | 712,066 | 0.252 | 1.021 | 2.8% |
| ≥ 2010 | 481,666 | 0.262 | 0.972 | 2.4% |

Katrina is 12% of the main sample but carries roughly two thirds of the near-total losses:
dropping that one event cuts the share of claims above 0.9 from 7.5% to 2.8% and the mean
from 0.304 to 0.252. The `since_2010` window looks like a "cleaner data" choice but is
mostly doing the same thing by another route — it excludes Katrina too, and lands in nearly
the same place.

Since relief's MVPF advantage grows with precisely this tail (`handover_notes.md` §2), the
result is materially sensitive to whether a single 2005 storm is in the sample. That has to
be reported, not chosen quietly. Note the direction of the trade-off: excluding Katrina
*lowers* the mean but slightly *raises* the CV, so the two calibration targets move in
opposite directions and the net effect on the ranking is not obvious a priori — worth
running both.

My reading is that Katrina belongs in the sample — it is a real draw from the loss
distribution and excluding realised catastrophes because they are large would bias the
tail down, which is the tail the whole exercise is about. But the paper should carry
`excl_katrina` as a robustness row, since "the result rests on one storm" is the first
objection a referee will raise.

### 3.5 Claim-weighted, not property-weighted

Repetitive-loss properties enter once per claim, so they are overweighted relative to a
per-household annual damage distribution. The redacted data carry no property identifier,
so this cannot be corrected here — it can only be bounded, or noted.

---

## 4. Suggested next step

Resolve §3.1 and §3.2 together, since both feed the same question of what `MEAN_D` should
be: compute claim frequency per policy-year on this database, adopt it as `p`, and rescale
the distribution by κ. That yields a mutually consistent `(p, G)` pair, replacing two
independently chosen round numbers with two jointly estimated ones. Then refit
`configure_damage` against the empirical mean and CV, and rerun.
