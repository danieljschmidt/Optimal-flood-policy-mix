# Flood-policy MVPF model — code

MVPF of the insurance **subsidy** ($s$) vs disaster **relief** ($a$) under heterogeneous flood-risk
beliefs. `main` holds the **headline analysis** — the MVPF core, the optimal policy mix, and the
figure/table driver. The (secondary) complements-vs-substitutes diagnostics live on the
`mvpf-complementarity` branch.

## Modules (here on `main`)

| file | role |
|---|---|
| `mvpf_discrete.py` | discrete-damage core: `struct`, `take_up`, `mvpf`, belief-Beta helpers |
| `mvpf_continuous.py` | continuous-damage core ($D\sim G$); `configure_damage(cv, dmax)` |
| `mvpf_optimal_mix.py` | optimal mix $(s^\ast,a^\ast)$: `welfare`, `cost`, `optimal_mix` (take a core module as first arg) |
| `mvpf_reproduce.py` | driver: prints all tables and regenerates the figures |

```python
import sys; sys.path.insert(0, "code")
import mvpf_discrete as D, mvpf_continuous as C
import mvpf_optimal_mix as A
D.mvpf(D.S0, D.A0, D.M_REF, nu=25)          # -> (MVPF_s, MVPF_a) = (1.116, 1.355)
C.mvpf(C.S0, C.A0, C.M_REF, nu=25)          # -> (1.251, 2.078)
A.optimal_mix(D, D.M_REF, nu=25, lam=1.2)   # -> discrete optimal (s*, a*)
```
Or run `python code/mvpf_reproduce.py` for all tables and figures.

Formulas, parameters, worked example, MVPF tables, and the optimal mix: `../notes/mvpf_computations.md`.
Parameters: `../notes/model_parameters.md`. MVPF formulas match `draft.tex` (verified numerically).

## On the `mvpf-complementarity` branch

`mvpf_complementarity.py` holds the secondary complements-vs-substitutes diagnostics
(`cross_partial_S`, `f_prime`, `beta_mode`, `driver`, `unreachable_tail`; each takes a core module as
its first argument), with working notes in `../notes/mvpf_complementarity.md`.

Legacy (unused): `baseline_model.py`, `figures.py`, `preference_heterogeneity_model.py`,
`one_region_model/`, `calibration_mvpf.py` (broken import).
