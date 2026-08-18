# FEMA damage distribution — data notes

*Produced by `run_compute_damage_distribution.py`; outputs in `fema_data_analysis/output/`. The distribution is wired into the model (2026-08-18) via `code/mvpf_continuous.configure_damage(empirical=…)` — main variant as the continuous baseline, excl_katrina as tail robustness, raw damage/house-value ratios (house-value base; `scale` hook for the MPC×damage/income reading). How to use it in the model — the utility base, the loss function, mean versus full distribution — is decided in `calibration_decisions.md`; this note documents the data itself and its caveats.*

## What is computed

The empirical distribution of

    D_ratio = buildingDamageAmount / buildingPropertyValue,  clipped to [0, 1]

over single-family SFHA claims (`occupancyType IN (1, 11)`, flood zone `A*` or `V*`, `yearOfLoss >= 2000`, denominator between \$10k and \$10M), discretized into 20 bins of width 0.05, each represented by its conditional mean. Three sample variants:

| variant | n | mean | CV | share ≥ 0.9 |
|---|---|---|---|---|
| main (≥ 2000) | 812,938 | 0.304 | 0.994 | 7.5% |
| excl_katrina | 712,066 | 0.252 | 1.021 | 2.8% |
| since_2010 | 481,666 | 0.262 | 0.972 | 2.4% |
| model placeholder, baseline | — | 0.15 | 0.86 | — |
| model placeholder, robustness | — | 0.15 | 1.3 | — |

The discretization reproduces the raw mean exactly and the raw CV to within 0.002.

**Headline:** the CV is stable at roughly 1.0 in every variant — between the two placeholder values, nearer the 0.86 baseline. The mean is less stable (0.25–0.30) and depends mainly on whether Katrina is in the sample.

## Caveats

**The denominator is depreciated building value, not wealth.** `buildingPropertyValue` is the adjuster's actual cash value (ACV) of the building alone — depreciated, excluding land and contents — so it is smaller than household wealth and the ratio overstates damage as a share of wealth (roughly: scaling by building value / wealth gives E[D]/w ≈ 0.21 against the 0.15 placeholder). The shape is the right object; the scale correction is part of the utility-base decision in `calibration_decisions.md`.

**The mass at D = 1 is partly an accounting convention.** 3.5% of claims report damage *exactly* equal to the building value (46% of the entire top bin), and almost none above it: for a total loss the adjuster simply records the ACV. So part of the spike at 1 is how total losses are booked, not a physical fact — and under CRRA, mass at total loss is exactly where relief's insurance value comes from.

**Why there is no replacement-cost variant.** An alternative denominator (`buildingReplacementCost`) was tried and removed. Because the damage amount is itself an ACV figure capped at the building value, dividing by replacement cost just rescales every claim down by the depreciation factor (ACV/RC, median 0.80) — a total loss of a depreciated building can then never reach 1, which mechanically empties the top bin (7.5% → 2.5%). Multiplying each claim's ratio by its own ACV/RC reproduces the replacement-cost top-bin share exactly (2.52% vs 2.53%), so the variant carried no independent information.

**The distribution is conditional on a claim, not on a flood.** Households must be insured and the loss worth filing, so small losses are missing and the mean is biased up. `p` and `G` must be defined consistently: either `p` is claim frequency per policy-year (computable from this database — the coherent pairing), or, if `p` stays the hydrological 0.02, `G` should include the small events that never generate claims.

**One storm drives the tail.** Katrina is 12% of the main sample but carries about two thirds of the near-total losses; dropping it cuts the share above 0.9 from 7.5% to 2.8% and the mean from 0.304 to 0.252 (`since_2010` mostly does the same thing by excluding Katrina too). Katrina is a real draw from the loss distribution and should stay in the baseline, but `excl_katrina` must be reported as robustness.

**The sample pools adapted and unadapted homes.** 33% of the main sample is elevated; non-elevated homes have a higher mean (0.333 vs 0.248) and lower CV (0.905 vs 1.200). The pooled distribution embeds today's elevation rate; if `D` is meant for an unadapted baseline household, the non-elevated numbers are the right target.

**Claim-weighted, not property-weighted.** Repetitive-loss properties enter once per claim and are overweighted; the redacted data have no property identifier, so this can only be noted, not fixed.

## Next step

Compute claim frequency per policy-year on this database and adopt it as `p`, so that `(p, G)` is a mutually consistent pair; then rescale by the utility base chosen in `calibration_decisions.md` and refit `configure_damage` to the empirical mean and CV.
