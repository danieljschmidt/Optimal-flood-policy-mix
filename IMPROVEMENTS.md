# Planned improvements

Backlog from the August 2026 repository scan. The restructure pass (moving files into `lit/`, `archive/`, and tagging `pre-cleanup-2026-08`) deliberately changed **no content, no numbers, and no code behaviour** — everything substantive it surfaced is listed here.

Ordered by dependency: the research items gate each other, the infrastructure items don't.

---

## Research

### 1. Reconcile the flood probability `p`

`p = 0.02` is currently a round modelling choice (`notes/model_parameters.md` §1b), while G&S's premium/loss ratio implies `0.04–0.06`. The consistency check in §2 of the same file is 3× low (`p·d̄ = $585` vs. their `P̄ = $1,739`) and closes only at `p ≈ 0.06`.

This is upstream of everything else: `p` rescales the belief mean `m = 0.57p`, moves `q*/p`, and plausibly decides item 2. **Do this first.**

### 2. Decide the belief-identification strategy

Three documents currently describe three different strategies for the same object:

| source | strategy |
|---|---|
| `draft/draft.tex:217-238` | recover `f(q*)` from `(I, ε)`; fit Beta to two moments |
| `archive/claude_july_assessment/claude_assessment.md:102` | same — and states surveys are *validation targets, not calibration inputs*, naming `k_R = 0.57` as the over-identifying check |
| `code/mvpf_discrete.py:23-30` | impose `k_R = 0.57` as an input, sweep `ν`, derive `I` and `f(q*)`; `ε` never used |

The code path fixes the mean exogenously, leaving one free parameter (`ν`), so only one moment can be matched. Take-up was matched; the elasticity was dropped. Measured consequences:

- The `ν = 25` anchor implies `ε = −0.56` against G&S's `−0.32` (1.7× too elastic).
- Matching `ε = −0.32` instead gives `ν ≈ 12`, `I = 0.22` — so `I = 0.30` and `ε = −0.32` are mutually inconsistent while `m` is pinned at `0.57p`.
- Running the draft's own two-moment fit at `(I = 0.30, ε = −0.32)` returns `Beta(0.143, 6.00)`, i.e. mean belief `m = 1.16p`, **above** the true probability.

Note what does and does not break: the fitted distribution still has 77% of mass below `p` and a median of `0.04p`, so underperception as a *premise* survives — a thin upper tail (7% believing `q > 0.10`) drags the mean up. What fails is `k_R = 0.57` **as a mean target**. Given the elicited distribution is strongly right-skewed, a quantile target (Bakkensen–Barrage's "35% perceive ≤5%") is a more robust second moment than the mean.

Minimum action regardless of which way this goes: add an **implied-`ε` column** to the `notes/mvpf_computations.md` §8/§9 tables, and stop describing "`ν = 25` reproduces observed take-up" (`:47`, `:123`) as an internal-consistency check — it is the one moment being fitted.

Reassurance for prioritisation: `MVPF_a` is ~1.355–1.357 under every variant tried, so the relief-over-subsidy **ranking is not at risk**. `MVPF_s` moves 1.08–1.12, and §10 (optimal mix, phase diagrams) is where this actually bites.

### 3. Grade local vs. global results differently

`notes/mvpf_computations.md` §§8–9 need only `(I, f(q*))` — they are sufficient-statistic results, independent of the shape of `F` *and* of `λ`. §10 (optimal mix, phase diagrams) integrates over all of `F` and additionally assumes it is stable. They are presented at identical confidence today. Re-deriving §§8–9 in explicit sufficient-statistic form would make them a strictly stronger claim than they currently make. The exposure-grading argument is already written up in `archive/claude_july_assessment/claude_assessment.md:114`.

### 4. Restate the crowd-out claim — `draft/draft.tex:157`

The draft asserts that because `q* < p`, relief crowd-out is "always weaker" than the crowd-in from an equal-cost subsidy. The actual comparison is `q*·d·u'(c_UF)` against `p·d·u'(c_I)`, so the correct condition is `q*/p < u'(c_I)/u'(c_UF)`. It **holds** at the current calibration (0.482 < 0.739), so no number changes — but as written it is false in general.

### 5. Extract an identification note

`archive/claude_july_assessment/claude_assessment.md` §7 contains the confounder taxonomy (liquidity, distrust, salience, relief anticipation), the over-identification programme, and the contamination-share exercise (`χ*`) — the paper's answer to its deepest referee objection, currently buried in an archived strategy document. It should become `notes/identification.md`, carrying the diagnostics from item 2.

### 6. Mandate contamination

The recovery of `f(q*)` from `(I, ε)` assumes all take-up is voluntary. Roughly half of SFHA policyholders hold insurance only because of the lender mandate, which contaminates both moments. Detailed in `claude_assessment.md:69`.

---

## Infrastructure

### 7. `code/params.py` — single source of truth

`W, GAMMA, P, D, S0, A0, M_REF` are declared in both `code/mvpf_discrete.py:19-22` and `code/mvpf_continuous.py`, and restated in prose in `notes/model_parameters.md`, `notes/mvpf_computations.md` §6, and `draft/draft.tex` Table 1 (where they are stale). Extract to one module; keep the existing names re-exported so `D.S0`, `C.M_REF` etc. still resolve.

### 8. `draft/bibfile.bib` does not exist

`draft/draft_progress_august.tex:83` calls `\bibliography{bibfile.bib}`, so the newest document **cannot compile**. ~35 keys to populate; some overlap `archive/presentations/sam_march_2026/subfiles/references.bib`.

### 9. Merge the two drafts

Intro + institutional setting from `draft_progress_august.tex`; model, MVPF derivations, continuous damage, and risk-aversion heterogeneity from `draft.tex`. Two gaps to close in the merge:

- Table 1 is stale — `p=0.01, s=0.3, a=0.05, I=0.5, ε=−1` against the notes' `0.02/0.47/0.055/0.30/−0.32`, and still carries `TODO: fill table`.
- `\subsection{Results}` is `TODO: add results`, while every figure in `notes/figures*/` (`figBC_optimalmix`, `figD_segmentation`, `figE_phase` × 3 specifications) appears in **no** `.tex` file. The draft currently shows none of the August results.

### 10. Promote `recover_fqstar` / `fit_beta`

`archive/legacy_code/baseline_model.py:163-210` holds the sufficient-statistic belief recovery and the two-moment Beta fit. They are correct and are needed by items 2, 3, and 5. Move into `code/belief_identification.py` rather than leaving them archived.

Related: `archive/legacy_code/calibration_mvpf.py` computes the local MVPF straight from `(I, ε)` with no belief density (`:47`), which is exactly the form item 3 wants. It has never run — it was added in commit `5989d5e`, the same commit that deleted its dependency `optimal_policy.py`, and the rename to `baseline_model.py` (`Parameters` → `Params`, different fields) was never applied to it. Treat it as a reference implementation, not something to repair: it also hardcodes the retired `ε = −0.17` and predates every G&S input.

### 11. The `mvpf-complementarity` branch does not exist

It is referenced from `code/README.md:5-6,30-34`, `code/mvpf_discrete.py:12-13`, `code/mvpf_continuous.py:14`, and `notes/mvpf_computations.md:10,247`, but exists neither locally nor on origin — so `mvpf_complementarity.py` and `mvpf_complementarity.md` are unreachable. Push the branch (references retained deliberately in the meantime).

### 12. Finish the restructure

Two pieces of the August restructure were not completed: **status headers** (`live | source | parked | archive`, plus `last-verified`) on every `.md`/`.tex` outside `archive/`, and a **root `README.md`** stating the headline result, the layout, how to reproduce, and what is archived and why.

---

## Recovery point

`git tag pre-cleanup-2026-08` marks the state before any files were moved. All 55 files from that tag were verified present by content hash after the restructure — nothing was lost or duplicated.
