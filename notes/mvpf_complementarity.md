# MVPF Cross-Schedules and the Complements-vs-Substitutes Question
### (archival working notes — complementarity is a *secondary* finding)

> **Framing note.** The headline of the project is **not** complementarity. The MVPF evidence shows the
> marginal public dollar favors **disaster relief** (see `mvpf_computations.md`). The
> complements-vs-substitutes question below turned out to be a **null / weak-substitutes** result — the
> welfare cross-partial is (weakly) negative and the gain from using both instruments over the best
> single one is negligible (~\$1–2/household-year). These notes are retained for the detailed
> diagnostics and derivations, but the framing has been demoted accordingly.

*Working notes. Computation now in `code/mvpf_discrete.py` /
`code/mvpf_continuous.py` (the early `scratchpad/mvpf_cross.py` used a fitted Beta).*

## Question

Can we compute the MVPF of subsidies *along the aid dimension* — i.e. MVPF$_s(a)$ — and is that
a way to tell whether subsidies and relief are complements or substitutes?

## Short answer

Yes, it is computable and well-defined, and I computed it. But as a complements/substitutes test
the **MVPF slope is asymmetric** and gives no single verdict; the **symmetric** primitive (the
welfare cross-partial) comes out as **weak substitutes** at the current calibration. The paper's
"complements" claim should therefore be reframed: it is a statement about *division of labor across
the belief distribution* (incidence), **not** about the cross-partial sign, which reads as the
conventional Samaritan's-dilemma substitute.

---

## Setup for the computation

- **Units fix.** Use the proper elasticity $\varepsilon\equiv(\pi/I)(\partial I/\partial\pi)$, so
  $\partial I/\partial s=-\varepsilon I/(1-s)$. The corrected $\partial I/\partial s$ is ~600× the
  note's buggy $0.000153$ (the factor-$1/\pi$ error).
- **Adopt G&S** $\eta_q=-0.32$ as baseline (also ran $-0.17$ for comparison).
- **Fit** Beta$(\alpha,\beta)$ to the status-quo $(I,\varepsilon)$ via the two moments in
  `draft.tex` (CDF: $F(q^*)=1-I$; PDF: $f(q^*)=-\varepsilon(I/\pi)(\Delta u/u'(c_I))$), then sweep
  each instrument using the structural take-up responses.
- Calibration: $s=0.47$, $a=0.055$, $I=0.30$, $p=0.02$, $d/w=0.15$, $\gamma=2$.

**Sanity check.** MVPF$_a\approx1.36 >$ MVPF$_s\approx1.08$ — ranking survives the correction,
matching Daniel's predicted corrected numbers (MVPF$_s\approx1.05$, MVPF$_a\approx1.36$).

---

## Results

### Status quo (baseline $\varepsilon=-0.32$)
| Object | Value |
|---|---|
| $q^*$ | 0.00964 |
| $\partial I/\partial s$ (corrected) | 0.181 |
| $\partial I/\partial a$ | −0.118 |
| MVPF$_s$ | **1.078** |
| MVPF$_a$ | **1.356** |

### Cross-effects
| Diagnostic | $\varepsilon=-0.32$ | $\varepsilon=-0.17$ | Reading |
|---|---|---|---|
| $\partial\text{MVPF}_s/\partial a$ | **−0.105** | −0.076 | aid makes subsidy **less** cost-effective → *substitute* |
| $\partial\text{MVPF}_a/\partial s$ | **+0.064** | +0.033 | subsidy makes aid **more** cost-effective → *complement* |
| Symmetric $\partial^2 S/\partial s\,\partial a$ | **−0.0011** | −0.0006 | weak net *substitutes* |

Signs are robust to the elasticity value.

---

## Interpretation

**The MVPF slope is asymmetric** — exactly why it gives no single verdict. The asymmetry traces
to $q^*$ moving in *opposite* directions under the two instruments:

- Raising $a$ → $q^*\uparrow$ (crowd-out) → internality $(p-q^*)$ shrinks → the marginal switcher
  the subsidy buys is *less* mistaken → **subsidy worth less** ($\partial\text{MVPF}_s/\partial a<0$).
- Raising $s$ → $q^*\downarrow$ → relief's crowd-out ($\propto q^*$) weakens and its internality
  grows → **relief worth more** ($\partial\text{MVPF}_a/\partial s>0$).

So aid *degrades* the subsidy while the subsidy *protects* relief. Netted symmetrically, the
instruments are **weak substitutes**, and the coupling is tiny ($\sim10^{-3}$): they are nearly
welfare-separable, interacting only through the $f(q^*)$ belief margin — i.e. the cross-effect
$\propto f(q^*)$ and vanishes in the degenerate-belief benchmark. This is a direct, quantitative
statement of the thesis that the interaction *is* the belief distribution — but note it delivers
substitutability, not complementarity, in the cross-partial sense.

---

## Implication for the paper (the important part)

**Do not rest the headline "complements" claim on the cross-partial or the MVPF slope.** At the
current calibration the model delivers weak *substitutes* there — the conventional Samaritan's-
dilemma reading. A referee who computes $\partial^2 S/\partial s\,\partial a$ would contradict the
word "complements" if it is framed as Edgeworth complementarity.

The genuinely novel, defensible content is a *different* object and survives intact:
1. **Segmentation / division of labor** — subsidy benefits marginal + high-$q$ insured; relief
   insures the low-$q$ underperceiving tail no affordable subsidy reaches. An *incidence*
   statement (the decomposition figure), not a cross-partial sign.
2. **Dampened crowd-out asymmetry** — $\partial I/\partial a\propto q^*<p$, the $q^*/p$ discount.

**Recommendation:** reframe the thesis language from "complements" to "**complementary roles / a
division of labor across the belief distribution**" — true and provable — and explicitly *concede*
the weak-substitute cross-partial rather than let a referee find it.

---

## Two red flags surfaced by the sweep

- **The Beta fit is not globally disciplined.** Implied $\mathbb{E}[q]/p$ swings from **1.16**
  ($\varepsilon=-0.32$) to **3.95** ($\varepsilon=-0.17$). The value 1.16 means *over*-perception
  on average — nonsensical against the belief story and against $k_R=0.57$. Two local moments do
  not pin the tail, so the **wide** parts of the swept curves are untrustworthy; only the
  neighborhood of the status quo is. This is the §7 identification concern in concrete form and
  motivates the over-identification program (Mulder's information effect) in roadmap step 4.
- Local cross-effect **signs** are robust to $\varepsilon$; the global curve **shapes** are not.

---

## Follow-ups

- Fold the corrected `compute_mvpfs` back into `code/calibration_mvpf.py` (currently broken import).
- Derive $\partial^2 S/\partial s\,\partial a$ analytically to confirm the $\propto f(q^*)$ structure.
- Build the segmentation/decomposition figure as the actual carrier of the "complementary roles"
  claim.

---
---

# Part II — Complementarity as a function of the belief distribution

*Research plan and first results. Code: `code/mvpf_complementarity.py` (the cross-partial and
belief-density diagnostics) on the core `code/mvpf_discrete.py`; the optimal-mix figures are
regenerated by `code/mvpf_reproduce.py` (on `main`). Figures: `notes/figures/figA…figE.png`.*

## The question, made precise

How does the substitutability/complementarity of subsidy $s$ and relief $a$ depend on the belief
distribution $F(q)$? We track **four distinct notions** (they can, and do, disagree):

| Notion | Object | Symmetric? |
|---|---|---|
| A. Edgeworth | $\partial^2 S/\partial s\,\partial a$ | yes |
| B. Fiscal | $\partial\text{MVPF}_s/\partial a,\ \partial\text{MVPF}_a/\partial s$ | no |
| C. Optimal-mix | which instruments are used at the optimum; $\Delta W$ from using both | — |
| D. Segmentation | incidence of each instrument over $F(q)$; unreachable tail | — |

## Method

- **Parametrise** $F(q)=\text{Beta}(\alpha,\beta)$ by mean $m$ and concentration $\nu$
  ($\alpha=m\nu,\ \beta=(1-m)\nu$), so $\sigma_q=\sqrt{m(1-m)/(\nu+1)}$ is a clean heterogeneity
  dial at fixed mean. Reference mean $m=0.0114=0.57p$ (Bakkensen–Barrage $k_R$).
- **Sweep** $\sigma_q$ (fixed mean) for the mechanism; **grid** over $(\mathbb{E}[q]/p,\sigma_q)$
  for the phase map. Optimal mix uses an MCPF $\lambda=1.10$ (so an interior "both" band can exist).

## The analytical handle: $f'(q^*)$

The subsidy's behavioural welfare weight is $(p-q^*)f(q^*)$; differentiating through the crowd-out
channel $q^*(a)$,
$$\frac{\partial}{\partial a}\big[(p-q^*)f(q^*)\big]=\underbrace{\frac{\partial q^*}{\partial a}}_{>0}\big[(p-q^*)f'(q^*)-f(q^*)\big].$$
So the cross-effect sign is governed by the **density slope at the margin** $f'(q^*)$ — i.e. whether
the belief mode sits above or below $q^*$. This `driver` predicts the sign of the full numerical
cross-partial in every case tested.

## Statistics computed (all in `mvpf_complementarity.py`)

`cross_partial_S`, `driver`, `mvpf_slopes`, `optimal_mix` (returns $s^*,a^*$, relief share, and the
complementarity premium $\Delta W$), `unreachable_tail`.

## Figures and one-line findings

- **`figA_crosseffect.png`** — $\partial^2S/\partial s\partial a$ vs $\sigma_q$: **complements at low
  heterogeneity ($\sigma_q<\approx0.0026$), substitutes above.** Right panel: the belief mode
  crossing the margin $q^*$ is the mechanism.
- **`figBC_optimalmix.png`** — optimal $(s^*,a^*)$ and $\Delta W$ vs $\sigma_q$: **three regimes** —
  subsidy-only (low het) → both (intermediate) → relief-only (high het); the gain from using both is
  **tiny** ($\Delta W\sim10^{-5}$ of wealth).
- **`figD_segmentation.png`** — density with instrument incidence shaded, low vs high $\sigma_q$: the
  **uninsured tail no free subsidy reaches** grows from $F=0.00$ to $F=0.46$ as heterogeneity rises.
- **`figE_phase.png`** — phase diagram over $(\mathbb{E}[q]/p,\sigma_q)$: the three optimal regimes,
  with the Edgeworth complement/substitute boundary overlaid.

## Findings

1. **The interaction is a belief-heterogeneity phenomenon.** All cross-effects scale with $f(q^*)$
   and vanish as $F$ degenerates. Nothing here exists in a homogeneous-belief (or G&S uniform-wedge)
   model.
2. **Cross-partial (Notion A) flips sign with heterogeneity**, governed by $f'(q^*)$: complements
   when beliefs cluster at an interior mode above $q^*$ (low $\sigma_q$), substitutes when mass piles
   at zero (high $\sigma_q$). This is the opposite of the naive "heterogeneity ⇒ complements" guess.
3. **The optimal policy is corner-dominated** (Notion C): the model generically wants *one*
   instrument, and heterogeneity selects which — relief when the uninsured tail is fat, subsidy when
   beliefs concentrate above the margin. An interior "both" band exists only at intermediate
   heterogeneity and moderate MCPF.
4. **The complementarity premium is economically negligible** ($\sim\$1$–$2$ per household-year).
   In the baseline model $s$ and $a$ are **near-perfect substitutes**: the mix question is
   first-order about *which* instrument, not about fine-tuning a blend.
5. **The two "complementarity" notions are anti-aligned.** In `figE`, the "both used" region sits
   where the cross-partial says *substitutes*, while the Edgeworth-complements region falls entirely
   inside *subsidy-only*. Where they are formal complements it is optimal to use only the subsidy.

## Implications for the paper

- **Do not claim Edgeworth complementarity** — it holds only in a thin low-heterogeneity sliver where
  the optimum uses subsidy alone. The honest baseline result is "near-substitutes with a
  heterogeneity-driven regime switch."
- **The large-complementarity story needs the extensions.** The baseline (single $p$, binary damage)
  is too stark to generate meaningful gains from combining instruments. Continuous damage
  (body-vs-tail), heterogeneous $p$ (two zones), the mandated segment, and adaptation are the
  channels that should make "use both" quantitatively real — this is a concrete argument for
  prioritising them (roadmap steps 2–3), and a prediction to test: does $\Delta W$ become
  first-order once damage is continuous and $p$ heterogeneous?
- **Reframe the thesis** around the **regime switch** (which instrument dominates, and how the belief
  distribution selects it — `figE`) plus the **segmentation/unreachable-tail** result (`figD`), not
  around a cross-partial sign.

## Caveats

- MCPF $\lambda=1.10$ is a modelling choice; higher $\lambda$ makes corners even more dominant (the
  interior band shrinks). Robustness across $\lambda$ still to be run.
- The cross-partial in `figE` is evaluated at current US policy $(s_0,a_0)$, a fixed reference; the
  regime fill is at the *optimal* policy. Evaluating both at a common point is a refinement.
- Same Beta-fragility caveat as Part I: results here vary $F$ freely (mechanism study); they are not
  yet disciplined to match the locally-identified moments. The identification-robust version (vary
  the tail subject to fixed $(I,f(q^*))$) is the natural next step.

---
---

# Part III — Continuous damage: what changes

*Continuous-damage baseline (draft.tex sec. "Continuous flood damage"). Code:
`code/mvpf_continuous.py`. Figures: `notes/figures_continuous/` — a drop-in
parallel to `notes/figures/`, same axes, so the two folders diff directly.*

**Setup.** Only the damage side changes: uninsured flood loss is random, $c_{U,F}(D)=w-(1-a)D$ with
$D\sim G$; insured premium uses the mean, $c_I=w-(1-s)p\bar d$; $\Delta u(a)=u(w)-\mathbb{E}[u(w-(1-a)D)]$;
relief's marginal-utility factor becomes $\overline{Du'}/\bar d$ with $\overline{Du'}=\mathbb{E}[D\,u'(c_{U,F})]$.
The belief distribution $F(q)$ is untouched. $G=\text{Beta}(1,5.67)$ on $[0,1]$, mean $\bar d=0.15$,
CV $\approx0.86$ (a documented, swappable choice; discrete = the degenerate $G$ at $\bar d$).

**Status-quo comparison** (belief concentration $\nu=25$, which reproduces observed take-up $I\approx0.30$):

| | $q^*$ | $\Delta u$ | $I$ | MVPF$_s$ | MVPF$_a$ |
|---|---|---|---|---|---|
| discrete | 0.0096 | 0.165 | 0.300 | 1.116 | 1.355 |
| continuous | 0.0081 | 0.197 | 0.329 | **1.251** | **2.078** |

**What changes**

1. **Relief becomes markedly more valuable.** MVPF$_a$ rises $1.36\to2.08$ (**+53%**). Mechanism:
   relief now insures the *dispersion* of damage — $\overline{Du'}/\bar d>u'(c_{U,F}(\bar d))$ because
   $D$ and $u'(c_{U,F})$ are positively correlated (bigger loss ⇒ higher marginal utility). **MVPF$_s$
   also rises, but only +12%** ($1.12\to1.25$): its *direct transfer* uses the mean $\bar d$, but the
   larger $\Delta u$ (Jensen) lowers $q^*$ and enlarges the internality. Relief gains disproportionately
   — the ratio widens $1.21\to1.66$.
2. **The "both used" region expands dramatically** (compare `figE_phase.png`). The relief-only
   triangle shrinks to a top-left corner; most of the belief-distribution space becomes *both*. This
   is the **body-vs-tail complementarity** Daniel's §3 anticipated: relief covers the body of $G(D)$
   for the uninsured, full insurance (moved by the subsidy) covers the tail, so it becomes optimal to
   run both across a wide range of $F$.
3. **But the two deeper caveats survive.** (i) The complementarity premium stays tiny (peak
   $\sim6\times10^{-6}$ of wealth, even *smaller* than discrete's $9\times10^{-6}$ — relief now
   dominates so strongly that adding subsidy on top buys little). (ii) The cross-partial still flips
   complements→substitutes with heterogeneity, the Edgeworth-complements region is still confined to
   *subsidy-only*, and it remains **anti-aligned** with the "both used" region.

**Verdict.** Continuous damage moves the model toward the paper's "use both" thesis in the
decision-relevant (Notion C) sense — both instruments optimal over a much wider belief space, relief
more valuable — vindicating the promotion decision. It does **not** rescue Edgeworth complementarity,
and the incremental welfare from blending stays small; the mix story is still first-order about *which*
instrument and about *coverage of the damage distribution*, not about a large super-additive gain.
Next: check whether heterogeneous $p$ (two zones) + the mandate + adaptation push the premium to
first-order, and rerun with a heavier-tailed $G$ (CV$\to$1.3) since relief's tail-insurance value is
$G$-shape sensitive.
