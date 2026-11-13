# Flood-policy MVPF model — code

MVPF of the insurance **subsidy** ($s$) vs disaster **relief** ($a$) under heterogeneous
flood-risk beliefs. Two layers of results:

- **Local (headline):** sufficient-statistic MVPFs at the status quo, computed from the observed
  take-up and premium elasticity $(I, \varepsilon)$ alone — no belief distribution, no MCPF.
- **Global (secondary):** the belief distribution (Beta) is fitted to the same two moments —
  $F(q^*) = 1-I$ and $f(q^*) = \hat f(I,\varepsilon)$ — and used for the optimal policy mix
  $(s^*, a^*)$ and the regime map over the belief space. Surveys (Bakkensen–Barrage) serve as
  validation checks, not calibration inputs.

## Modules

| file | role |
|---|---|
| `params.py` | **single source of truth** for all parameters; edit values here only |
| `belief_identification.py` | `mvpf_local` (sufficient statistics), `recover_fqstar`, `fit_beta`, `validation` |
| `mvpf_discrete.py` | discrete-damage core: `struct`, `take_up`, `mvpf`, belief-Beta helpers (generic in $(m,\nu)$) |
| `mvpf_continuous.py` | continuous-damage core ($D\sim G$); `configure_damage(empirical=..., scale=...)` (or Beta mode via `cv`/`alpha,beta`) |
| `mvpf_optimal_mix.py` | optimal mix: `welfare`, `cost`, `current_budget`, `optimal_mix` (fixed budget by default; `lam=` for the fixed-MCPF robustness check) |
| `mvpf_reproduce.py` | driver: prints the Local/Global tables and regenerates all figures |

The damage distribution $G$ is the **empirical FEMA claims-based distribution** — a 20-bin
discretization of $D=$ damage$/$building value over single-family SFHA claims since 2000
(`../fema_data_analysis/output/damage_distribution_main.csv`; `..._excl_katrina.csv` is the tail
robustness variant; data caveats in `../fema_data_analysis/notes/notes.md`). It is loaded at
import via `configure_damage(empirical=params.FEMA_DIST_MAIN)`; in this mode $\bar d$ is the
empirical bin mean (0.3044 main / 0.2517 excl. Katrina), not `params.MEAN_D`. The `scale`
parameter (default 1.0 = damage/house value, house-value base) implements the reinterpretation
MPC $\times$ damage/annual income with MPC $= y/h$; other scales give other (MPC, base) choices
(`../fema_data_analysis/notes/calibration_decisions.md`, App. A). The former Beta placeholder
(CV = 0.86 / 1.3) remains available as `configure_damage(cv=..., dmax=...)`.

## Usage

```python
import sys; sys.path.insert(0, "code")
import params, belief_identification as B
import mvpf_discrete as D, mvpf_continuous as C
import mvpf_optimal_mix as A

B.mvpf_local(D, D.S0, D.A0, params.I_OBS, params.EPS)   # -> (MVPF_s, MVPF_a) = (1.038, 1.238)
B.mvpf_local(C, C.S0, C.A0, params.I_OBS, params.EPS)   # -> (1.537, 20.12)  [FEMA main; see note]
al, be = B.fit_beta(D, D.S0, D.A0, params.I_OBS, params.EPS)   # -> Beta(0.313, 26.1)
B.validation(D, al, be)                                  # survey checks
A.optimal_mix(D, al/(al+be), al+be)                      # fixed budget B0 (baseline) -> s*=0.00, a*=0.233
A.optimal_mix(D, al/(al+be), al+be, lam=1.2)             # fixed MCPF (robustness)  -> s*=0.00, a*=0.14
```

Values above are for the calibration of 2026-11-07: `GAMMA = 1.5`, `S0 = 0.22` (subsidy relative
to expected claims), `I_OBS = 0.484`, `PHI = 0.32`, `A0 = 0.052`, `EPS = -0.25`. `P = 0.02` is not
yet updated. `GAMMA = 1` (log utility) is supported. `optimal_mix` solves the fixed-budget problem
by default (budget = current spending at `(S0, A0)`; `budget=` overrides) and the
fixed-lambda problem when `lam` is given. The mandated share
`PHI` enters take-up, $I = \phi + (1-\phi)(1-F(q^*))$, the Beta fit and the optimal mix; it
cancels out of the local MVPFs. **Note on the continuous MVPF_a:** its denominator (net fiscal
cost of aid) is small, because extra aid crowds out insurance and saves subsidy spending. At
`GAMMA = 1.5` and 2 it stays positive (MVPF_a = 20 and 104). At `GAMMA = 3` it turns negative: the subsidy
saved then exceeds the aid paid, while the numerator is positive. By the usual MVPF convention
that value is infinite, not negative.

Or run `python code/mvpf_reproduce.py` for all tables and the figures in
`../notes/figures{,_continuous,_continuous_excl_katrina}/` (runtime dominated by the phase
diagrams, ~10–20 min).

## Documentation

Formulas, worked example, and results: `../notes/mvpf_computations.md`. Parameter values and
provenance: `../notes/model_parameters.md`. MVPF formulas match `../draft/paper.tex` (verified
numerically).
Secondary complements-vs-substitutes diagnostics: `mvpf_complementarity.py` on the
`mvpf-complementarity` branch (not yet pushed).
