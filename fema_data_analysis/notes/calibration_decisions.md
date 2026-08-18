# Two calibration decisions: the utility base and the damage distribution

This note states two open modeling problems, lists the options for each, gives a recommendation, and evaluates the recommended fix critically. Appendix A contains the formal mapping from a dynamic consumption-savings model to the static model, with key references.

---

## Problem 1: What is the argument of the utility function?

### The problem

The model needs consumption in three states: insured, uninsured without flood, uninsured with flood. The current draft writes these as wealth minus premium or damage, with wealth normalized to 1 and damage $d = 0.15$ "of house value." But CRRA utility is scale-free: only the *ratio* of the loss to the base matters. So the choice of base (house value, income, total wealth) silently sets how risk-averse households effectively are toward floods, and through that:

- how large the utility gap $\Delta u$ between the flood and no-flood states is,
- where the marginal belief $q^*$ sits, and how large the internality $(p - q^*)$ is,
- how large the marginal-utility gap $u'(c_{U,F})/u'(c_I)$ is — which is the welfare case for disaster aid.

A rough magnitude: with $\gamma = 2$, the marginal-utility gap is about 1.2 if the loss is 10% of the base, about 1.4 at 15%, and about 6 if the loss is 60% of the base. The relative attractiveness of aid versus subsidy can move by a factor of five depending on this one choice. So the base is not a normalization; it is a substantive assumption that must be justified.

### What the base actually represents

The static model is a stand-in for a dynamic problem in which a household spreads a one-time loss over time by saving, borrowing, and delaying repairs. Appendix A derives the mapping: the static base that reproduces the dynamic household's choices (to second order in the size of the stakes) is

$$B = \frac{c}{\mathrm{MPC}},$$

where MPC is the marginal propensity to consume out of a one-time shock. Equivalently, keep consumption ($\approx$ income) as the base and multiply all monetary stakes by a pass-through parameter $\phi = \mathrm{MPC}$. The three familiar candidates are then special cases:

| Base | Implied MPC | Verdict |
|---|---|---|
| Total wealth | $\approx$ interest rate (perfect smoothing) | Too low. Predicts near risk-neutrality toward floods (the calibration critique of Rabin 2000 and Sydnor 2010, run in reverse), which assumes the policy problem away. |
| Income (hand-to-mouth) | $1$ | Too high as a universal value, but roughly right for liquidity-constrained households — which the post-disaster evidence says the uninsured often are. |
| House value | $\approx y/h \approx 0.25$–$0.33$ | Coincides with measured MPCs almost by accident. Defensible, but only via this MPC argument — "utility over the house price" is not coherent on its own. |

Empirical MPCs out of one-time shocks are about 0.35–0.5 within a year, and higher for losses than for gains. So the defensible range for $\phi$ is roughly $[0.3, 1]$, with the upper half more plausible for the uninsured.

### Options

**Option 1A. Keep the house-value base as is, no justification.**
Pros: no work; matches Collier et al. (2022).
Cons: a referee will ask what $u(\text{house value} - \text{damage})$ means; the answer "we follow Collier" concedes the base is arbitrary while it in fact drives the aid-vs-subsidy result. Not recommended.

**Option 1B. Income base with pass-through $\phi$, justified by the MPC mapping (Appendix A). Sweep $\phi \in [0.3, 1]$, re-fitting the belief distribution at each value.**
Pros: turns the arbitrary choice into a disciplined empirical statement; the sweep shows readers how much of the optimal policy mix depends on it; connects the paper to the Baily–Chetty tradition (value of insurance = risk aversion $\times$ consumption drop), which referees know.
Cons: the belief distribution must be re-estimated at each $\phi$ (the fitted beliefs absorb the base choice — this is unavoidable under any option, 1B just makes it visible); the linear specification breaks for very large damages (see Problem 2).
Recommended for the baseline.

**Option 1C. Full dynamic model (buffer-stock consumption-savings).**
Pros: exact.
Cons: a different, much heavier paper; the sufficient-statistics literature exists precisely so one does not have to do this. Use it only as an appendix check: solve the dynamic model once, verify the static specification reproduces its valuations to within a few percent.

### One warning

Do not scale the damage by $\phi$ but leave the premium unscaled. Both are monetary stakes and both must be treated the same way (equivalently: change the base, not one of the stakes). Mixed treatment distorts the premium-versus-expected-loss comparison by a factor $\phi$.

---

## Problem 2: What to do about the distribution of damages?

### The problem

Real flood damages are heavily skewed: median claim around 9% of house value, mean around 20%, and a mass point at total loss (Collier et al. 2022). Two difficulties follow.

**(a) Technical.** With an income base and pass-through $\phi$ above roughly $y/h$, a total loss implies negative consumption, and CRRA utility of a nonpositive number is minus infinity. The model then says willingness to pay for insurance is infinite. So "linear pass-through" and "damages up to full house value" are jointly infeasible for most of the $\phi$ range we want to sweep.

**(b) Substantive.** Disaster aid pays out most in the worst states, so its welfare value depends on marginal utility in the tail — exactly the region the mean-damage shortcut throws away and the linear specification handles worst.

### Why the technical problem is really an economics problem

A household cannot cut this year's consumption by three years of income; arithmetic forbids it. In reality large losses are absorbed on other margins: borrowing and repaying over years, delaying repairs, and — at the extreme — walking away from the house. A household's exposure is capped at roughly its home equity plus moving costs, and below that sits the means-tested safety net. This is what the Katrina evidence shows: the most-flooded households did not display consumption catastrophes; they used insurance payouts to pay off mortgages and moved (Gallagher and Hartley 2017). So the model needs pass-through that *declines with loss size*, not a numerical trick to keep consumption positive.

### The proposed fix

Replace the linear pass-through $\phi z$ with a piecewise loss function $\ell(z)$, where $z = (1-a)D$ is the uninsured damage:

$$\ell(z) = \phi \, \min(z, \kappa y) + \rho \,\big(z - \kappa y\big)^{+}, \qquad \ell(z) \le \bar\ell \equiv (h - m)^{+} + \chi,$$

$$c_{U,F}(D) = c - \ell\big((1-a)D\big),$$

with three regions:

- **Small losses** ($z \le \kappa y$, a liquidity capacity): pass-through $\phi$, as in Problem 1.
- **Larger losses**: the excess is financed over time; the consumption-equivalent cost is roughly the annuitization rate $\rho \approx 0.05$–$0.10$ per dollar.
- **Cap** $\bar\ell$: total consumption-equivalent loss cannot exceed home equity $(h-m)^{+}$ plus moving costs $\chi$ (walk-away option; limited liability).

Every piece has an empirical anchor (MPC estimates; disaster-loan terms; equity data). Utility is then finite for any $\phi$ and any damage, including total loss. One consequence to be aware of: at the cap, $\ell' = 0$ — marginal damage no longer reaches consumption, and therefore marginal *aid* in near-total-loss states partly benefits the household's lender (less default, more recovered equity) rather than consumption. This matches the observed post-Katrina payout behavior and matters for interpreting results.

### Critical evaluation of the fix, and alternatives

The fix is the right shape but should be presented honestly as a calibrated reduced form, not a microfoundation. Its weaknesses:

1. **The annuitization region mixes time periods.** It compresses a multi-year consumption path into a one-period utility argument. The parameter $\rho$ is a one-period-equivalent weight, only loosely pinned down by loan terms.
2. **The cap is imposed, not derived.** The walk-away decision that justifies the cap should in principle depend on the policy variables themselves: more generous aid changes who defaults, so $\ell(\cdot)$ shifts with the very policies being optimized. The fix ignores this feedback, which means the "aid accrues to creditors at the cap" result is partly assumed rather than discovered. It should be framed as an implication of documented post-disaster behavior, not a theorem of the model.
3. **Heterogeneity is suppressed.** One representative $\ell(\cdot)$ is used, while liquidity and home equity vary widely across households and plausibly correlate with beliefs. Since beliefs are fitted residually from take-up, heterogeneity in $\ell$ leaks into the fitted belief distribution.
4. **The proposed validation only half-helps.** A standard buffer-stock model (Appendix A setting) has no housing asset and no default option, so it can validate $\ell$ in the small-loss region — where it was never in doubt — but not in the tail, where the results live.

Alternatives, all worse for the present purpose:

- **Numerical floor near zero consumption** (as in Collier et al.'s implementation): pure artifact; with $\gamma = 2$ the results become a function of an arbitrary constant.
- **Linear pass-through throughout**: infeasible for the $\phi$ range and damage support required (see (a) above).
- **Smooth variant** $u(c - \ell(z) + \sigma)$ with a small non-marketable endowment $\sigma$ (home production, in-kind aid): a legitimate substitute for the kinked $\ell$ if the kinks cause trouble in the first-order conditions; same information demands, slightly less transparent.
- **Full dynamic model with housing and default**: the correct long-run answer and a different paper.

Conclusion: adopt the piecewise $\ell$, and let a tail-sensitivity table ($\rho$ varied; cap varied by home-equity quartile) do the honesty work. The results section should state plainly that the aid MVPF in the continuous-damage model inherits its tail behavior from these parameters.

### Options for the main specification

**Option 2A. Mean damages only ($d = \bar d$ everywhere).**
Pros: simple; transparent; exact for the insured side and the government budget (full coverage and actuarial pricing only need the mean).
Cons: aid's value is a tail object, so this simplification is first-order *for the instrument the paper is about*. Risky as the only specification.

**Option 2B. Mean damages in the main text, plus a verbal claim that the full distribution would strengthen the case for aid.**
Pros: none beyond 2A.
Cons: the claim is not true in general. Three forces push the other way once the distribution is real:
1. *Recalibration.* More dispersion raises $\Delta u$; at the same observed take-up and elasticity, the re-fitted belief density and the internality rise — which strengthens the **subsidy's** numerator too. Both MVPFs move.
2. *Crowd-out.* The same force that raises aid's benefit makes aid a stronger substitute for insurance at the margin ($\partial I/\partial a$ scales with the same tail object), and each crowded-out household now costs more.
3. *Product mismatch.* Dispersion raises the value of *complete* tail coverage — which is what insurance sells — at least as much as the value of covering a fraction $a$ of the tail. And with the cap from the fix above, plus the fact that real aid programs cap benefits (FEMA Individual Assistance grants are capped far below typical severe losses), aid payouts concentrate in the *low*-marginal-utility small-loss region. Under a realistic capped-aid specification, dispersion can plausibly *weaken* the measured case for aid.
Asserting a direction that the paper's own tail machinery undermines invites a serious referee objection. Not recommended.

**Option 2C. Mean damages as the headline specification for transparency; full distribution with the loss function $\ell$ as a computed section, not a conjecture.**
Pros: keeps the simple model readable; replaces the unsupported directional claim with a result — and either direction is publishable. If dispersion strengthens aid only under linear uncapped pass-through and weakens it under realistic $\ell$ and capped aid, that is a genuine finding about disaster-aid design (aid misses the mid-sized losses where the smoothing case is strongest), not a robustness footnote. The computation is cheap: the loss distribution is already estimated (Collier et al. 2022), and the continuous-damage formulas are already in the draft.
Cons: the belief re-fitting must now be done on a grid of ($\phi$, distribution) combinations; a few days of computation and one more table.
Recommended.

---

## How the two problems interact

1. **The base sets where the distribution hurts.** With a low $\phi$ (heavy smoothing), even total losses stay in the well-behaved region and the linear model survives; with high $\phi$ it does not. So Problem 2's fix must be built before the $\phi$ sweep, not after.
2. **The beliefs absorb both choices.** The belief distribution is fitted from take-up and one elasticity. Change the base or the damage distribution and the fitted beliefs change, and with them the internality that drives both MVPFs. No comparison across specifications is valid without re-fitting. This is not a flaw introduced by our approach; it is a property of the identification that the approach makes explicit.
3. **One instrument is exposed, the other is not.** The insured side and the budget need only mean damages under full coverage — so the subsidy's MVPF is fairly robust to all of this, while aid's MVPF is sensitive to the base, the tail, and the aid cap. That asymmetry, stated plainly, is itself one of the paper's findings.

## Bottom line

- Base: income with pass-through $\phi$, justified by the MPC mapping in Appendix A; sweep $\phi \in [0.3, 1]$ with belief re-fitting (Option 1B). Keep a one-line remark that the house-value normalization is the special case $\phi \approx 0.3$.
- Damages: piecewise loss function with liquidity capacity, annuitization, and an equity cap; mean-damage model as the transparent headline, full-distribution results computed, including a capped-aid variant (Option 2C).
- Do not claim in advance which way the distribution pushes the aid-versus-subsidy comparison. Compute it; the answer is interesting either way.

---

## Appendix A: Mapping the dynamic model to an equivalent static model

### A.1 Setup

Time is discrete. A household has period utility $u$ with $u' > 0$, $u'' < 0$ (CRRA with coefficient $\gamma$ in the application), discount factor $\beta$, gross return $R$, stochastic income $y_t$, and cash-on-hand $x_t = R a_{t-1} + y_t$, with a borrowing limit $a_t \ge -\underline{b}$. The consumption-savings problem defines a value function

$$V(x) = \max_{c} \; u(c) + \beta \, \mathbb{E}\big[ V( R(x - c) + y' ) \big], \tag{A1}$$

with policy function $c(x)$ and $\mathrm{MPC}(x) \equiv c'(x)$. Under standard conditions $V$ is concave and, by Carroll and Kimball (1996), the consumption function is concave, so $\mathrm{MPC}(x)$ is decreasing in $x$.

At date 0 the household faces a one-time insurable risk: pay premium $\pi$ now, or bear loss $L$ with subjective probability $q$, where both $\pi$ and $L$ are one-time reductions of cash-on-hand. The insurance choice compares

$$V(x - \pi) \quad \text{versus} \quad (1 - q)\,V(x) + q\,V(x - L). \tag{A2}$$

### A.2 Curvature of the value function

At an interior optimum the envelope theorem gives $V'(x) = u'(c(x))$. Differentiating once more,

$$V''(x) = u''(c(x)) \cdot c'(x) = u''(c(x)) \cdot \mathrm{MPC}(x),$$

so the absolute risk aversion of the *value function* over one-time monetary shocks is

$$A_V(x) \equiv -\frac{V''(x)}{V'(x)} = \left[-\frac{u''(c)}{u'(c)}\right] \mathrm{MPC}(x) = A_u\big(c(x)\big)\,\mathrm{MPC}(x), \tag{A3}$$

and with CRRA period utility, $A_u(c) = \gamma/c$, hence

$$A_V(x) = \frac{\gamma \, \mathrm{MPC}(x)}{c(x)}. \tag{A4}$$

Interpretation: a marginal dollar of loss reduces consumption in every future period; the fraction absorbed *today* is the MPC, and smoothing dilutes exposure to one-time risk at exactly that rate. Equation (A3) is the discrete-time envelope version of a result in Gollier (2001) on time diversification: the risk tolerance of wealth is the (discounted) sum of future consumption risk tolerances.

### A.3 The equivalence

**Proposition.** Consider a one-period ("static") agent with CRRA utility of base $B$ facing the same unscaled stakes: $u_s(B - \pi)$ versus $(1-q)\,u_s(B) + q\,u_s(B - L)$. The static agent's indifference condition agrees with the dynamic household's, up to third-order terms in the stakes, if and only if

$$B = \frac{c(x)}{\mathrm{MPC}(x)}. \tag{A5}$$

**Proof.** Expand both sides of (A2) around $x$ to second order:

$$V(x) - V(x - L) = V'(x)\,L - \tfrac{1}{2}V''(x)\,L^2 + O(L^3) = V'(x)\,L\left[1 + \tfrac{1}{2}A_V(x)\,L\right] + O(L^3),$$

and identically for $\pi$. The indifference condition — the certain utility cost of $\pi$ equals $q$ times the expected utility cost of $L$ — divides out the level $V'(x)$, leaving a condition on $(\pi, L, q)$ and the single curvature parameter $A_V(x)$. The static agent's indifference condition has the same form with curvature $A_{u_s}(B) = \gamma/B$. The two coincide iff $\gamma/B = \gamma\,\mathrm{MPC}/c$, i.e. $B = c/\mathrm{MPC}$. $\blacksquare$

By CRRA scale invariance, an equivalent implementation keeps base $c$ and multiplies every monetary stake by $\phi = \mathrm{MPC}$ — the pass-through formulation used in the main text. The equivalence requires *all* stakes to be scaled identically; scaling the loss but not the premium changes the first-order (actuarial) comparison by a factor $\phi$ and is not an implementation of (A5).

**Limiting cases.** (i) Frictionless permanent income: $\mathrm{MPC} \approx r$, so $B \approx c/r \approx$ present value of consumption $\approx$ total (including human) wealth — the Arrow–Pratt benchmark, with its counterfactually small curvature over moderate losses (the observation underlying Rabin 2000 and Sydnor 2010). (ii) Binding liquidity constraint: $\mathrm{MPC} = 1$, $B = c$ — the hand-to-mouth income base. (iii) $\mathrm{MPC} = y/h$ with $h$ the house value: the house-value normalization of Collier et al. (2022), a legitimate special case precisely when the MPC equals the income-to-house-value ratio ($\approx 0.25$–$0.33$), a value inside the empirical range.

### A.4 Where the approximation fails, and the correction

Equation (A5) is local: it evaluates the MPC at current cash-on-hand. For a large loss the exact object is

$$V(x) - V(x - L) = \int_{x-L}^{x} u'\big(c(t)\big)\,dt,$$

so the relevant statistic averages MPC-adjusted marginal utilities over the traversed interval. Concavity of the consumption function implies the MPC rises as resources fall: effective pass-through *increases* with loss size — until other margins take over. Three bounds operate in reality: (i) consumption cannot fall below a floor sustained by means-tested transfers (the approach used to value insurance against larger-than-income losses by Finkelstein, Hendren and Luttmer 2019); (ii) losses beyond liquid capacity are financed over time, at a consumption-equivalent cost near the annuitization rate; (iii) exposure to a housing loss is truncated at home equity plus moving costs by the option to default or walk away. The piecewise loss function $\ell(\cdot)$ of Problem 2 is the reduced form of (i)–(iii); its small-loss slope is the $\phi$ of (A5).

Ericson and Sydnor (2018) compute, in a buffer-stock model, the wedge between dynamic consumption-based valuations of insurance contracts and static expected-utility-over-wealth valuations, and show that no single static risk-aversion parameter rationalizes the dynamic valuations across contracts; $\ell(\cdot)$ is the analytical, calibrated counterpart of their numerical exercise for the flood context. Their focus is health-insurance contract features, so they are the reference for the existence and sign of the wedge, not for the base-selection rule (A5).

### A.5 Key references

- Carroll, C. D., & Kimball, M. S. (1996). On the concavity of the consumption function. *Econometrica*, 64(4), 981–992.
- Chetty, R. (2006). A general formula for the optimal level of social insurance. *Journal of Public Economics*, 90(10–11), 1879–1901. [The sufficient-statistic logic: dynamics summarized by the observed consumption drop.]
- Ericson, K. M., & Sydnor, J. R. (2018). Liquidity constraints and the value of insurance. NBER Working Paper 24993.
- Finkelstein, A., Hendren, N., & Luttmer, E. F. P. (2019). The value of Medicaid: Interpreting results from the Oregon Health Insurance Experiment. *Journal of Political Economy*, 127(6), 2836–2874. [Template for valuing insurance against larger-than-income losses via consumption floors.]
- Gollier, C. (2001). *The Economics of Risk and Time.* MIT Press. [Value-function risk tolerance under HARA; time diversification.]

*(Verify bibliographic details before submission.)*
