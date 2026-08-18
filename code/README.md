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
| `mvpf_optimal_mix.py` | optimal mix: `welfare`, `cost`, `optimal_mix` (take a core module as first argument) |
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

B.mvpf_local(D, D.S0, D.A0, params.I_OBS, params.EPS)   # -> (MVPF_s, MVPF_a) = (1.072, 1.334)
B.mvpf_local(C, C.S0, C.A0, params.I_OBS, params.EPS)   # -> (2.212, 31.445)  [FEMA main]
al, be = B.fit_beta(D, D.S0, D.A0, params.I_OBS, params.EPS)   # -> Beta(0.143, 5.691)
B.validation(D, al, be)                                  # survey checks
A.optimal_mix(D, al/(al+be), al+be, lam=1.2)             # -> (s*, a*) = (0.00, 0.34)
```

Or run `python code/mvpf_reproduce.py` for all tables and the figures in
`../notes/figures{,_continuous,_continuous_excl_katrina}/` (runtime dominated by the phase
diagrams, ~10–20 min).

## Documentation

Formulas, worked example, and results: `../notes/mvpf_computations.md`. Parameter values and
provenance: `../notes/model_parameters.md`. MVPF formulas match `../draft/draft.tex` (verified
numerically).
Secondary complements-vs-substitutes diagnostics: `mvpf_complementarity.py` on the
`mvpf-complementarity` branch (not yet pushed).
