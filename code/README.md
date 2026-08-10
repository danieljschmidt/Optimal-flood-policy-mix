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
| `mvpf_continuous.py` | continuous-damage core ($D\sim G$); `configure_damage(cv, dmax)` |
| `mvpf_optimal_mix.py` | optimal mix: `welfare`, `cost`, `optimal_mix` (take a core module as first argument) |
| `mvpf_reproduce.py` | driver: prints the Local/Global tables and regenerates all figures |

The damage distribution $G$ (Beta, CV = 0.86 baseline / 1.3 robustness) is a **placeholder**
pending a FEMA claims-based distribution; swap it in via `configure_damage`.

## Usage

```python
import sys; sys.path.insert(0, "code")
import params, belief_identification as B
import mvpf_discrete as D, mvpf_continuous as C
import mvpf_optimal_mix as A

B.mvpf_local(D, D.S0, D.A0, params.I_OBS, params.EPS)   # -> (MVPF_s, MVPF_a) = (1.072, 1.334)
B.mvpf_local(C, C.S0, C.A0, params.I_OBS, params.EPS)   # -> (1.161, 1.944)
al, be = B.fit_beta(D, D.S0, D.A0, params.I_OBS, params.EPS)   # -> Beta(0.143, 5.691)
B.validation(D, al, be)                                  # survey checks
A.optimal_mix(D, al/(al+be), al+be, lam=1.2)             # -> (s*, a*) = (0.00, 0.34)
```

Or run `python code/mvpf_reproduce.py` for all tables and the figures in
`../notes/figures{,_continuous,_continuous_cv13}/` (runtime dominated by the phase diagrams,
~10–20 min).

## Documentation

Formulas, worked example, and results: `../notes/mvpf_computations.md`. Parameter values and
provenance: `../notes/model_parameters.md`. MVPF formulas match `../draft/draft.tex` (verified
numerically).
Secondary complements-vs-substitutes diagnostics: `mvpf_complementarity.py` on the
`mvpf-complementarity` branch (not yet pushed).
