# Flood-policy MVPF model — code (core)

MVPF of the insurance **subsidy** ($s$) vs disaster **relief** ($a$) under heterogeneous flood-risk
beliefs. This folder on `main` holds the **MVPF core**; the optimal-mix / complementarity analysis and
the figure/reproduce pipeline live on the `mvpf-complementarity` branch.

## Core modules (here on `main`)

| file | role |
|---|---|
| `belief_complementarity.py` | discrete-damage model: `struct`, `take_up`, `mvpf`, belief-Beta helpers |
| `belief_complementarity_continuous.py` | continuous-damage model ($D\sim G$); `configure_damage(cv, dmax)` |

```python
import sys; sys.path.insert(0, "code")
import belief_complementarity as D
D.mvpf(D.S0, D.A0, D.M_REF, nu=25)     # -> (MVPF_s, MVPF_a) = (1.116, 1.355)
import belief_complementarity_continuous as C
C.mvpf(C.S0, C.A0, C.M_REF, nu=25)     # -> (1.251, 2.078)
```

Formulas, parameters, worked example, and MVPF result tables: `../notes/mvpf_computations.md`.
Parameters: `../notes/model_parameters.md`. MVPF formulas match `draft.tex` (verified numerically).

## On the `mvpf-complementarity` branch

`belief_complementarity_analysis.py` extends the core with `optimal_mix`, `cross_partial_S`,
`welfare`, `cost`, … (functions take a core module as their first argument), and `reproduce.py`
regenerates all tables and figures. Legacy: `baseline_model.py`, `figures.py`,
`preference_heterogeneity_model.py`, `one_region_model/`, `calibration_mvpf.py` (broken import).
