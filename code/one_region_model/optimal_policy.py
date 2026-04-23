"""
Optimal Flood Insurance Policy Solver

Solves for optimal subsidy (s) and disaster relief (a) given:
- CRRA utility: u(c) = c^(1-γ) / (1-γ)
- Beta-distributed subjective beliefs: q ~ Beta(α, β)
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import beta
from dataclasses import dataclass
import matplotlib.pyplot as plt


@dataclass
class Parameters:
    """Model parameters"""
    w: float = 1              # wealth
    d: float = 0.5            # flood damage
    p: float = 0.02           # true flood probability
    pi: float = 0.03          # insurance premium per unit coverage
    # WARNING: The Latex file assumes actuarially fair insurance,
    # i.e. pi = p. Set pi = p = 0.02 to match the proposal's formulas.
    # The default pi = 0.03 includes a loading factor and will produce
    # different numerical results (e.g. q*(0,0) ≈ 1.5% instead of ≈ 1%).
    gamma: float = 2.0        # CRRA risk aversion
    B: float = 0.001          # government budget (per capita)
    mean_q: float = 0.01      # mean of beta distribution (subjective flood probability)
    var_q: float = 0.0001     # variance of beta distribution
    
    @property
    def alpha(self):
        """Compute alpha parameter from mean and variance"""
        mu = self.mean_q
        sigma2 = self.var_q
        # From Beta distribution: mu = alpha/(alpha+beta), var = alpha*beta/[(alpha+beta)^2*(alpha+beta+1)]
        # Solving: alpha = mu * [mu(1-mu)/sigma2 - 1]
        if sigma2 >= mu * (1 - mu):
            raise ValueError(f"Variance {sigma2} too large for mean {mu}. Max variance: {mu*(1-mu)}")
        concentration = mu * (1 - mu) / sigma2 - 1
        return mu * concentration
    
    @property
    def beta(self):
        """Compute beta parameter from mean and variance"""
        mu = self.mean_q
        sigma2 = self.var_q
        if sigma2 >= mu * (1 - mu):
            raise ValueError(f"Variance {sigma2} too large for mean {mu}. Max variance: {mu*(1-mu)}")
        concentration = mu * (1 - mu) / sigma2 - 1
        return (1 - mu) * concentration


def u(c, gamma):
    """CRRA utility function"""
    return c ** (1 - gamma) / (1 - gamma)


def u_prime(c, gamma):
    """Marginal utility"""
    return c ** (-gamma)


def q_star(s, a, par):
    """Insurance purchase threshold"""
    c_ins = par.w - (1 - s) * par.pi * par.d
    c_unins_flood = par.w - (1 - a) * par.d
    
    num = u(par.w, par.gamma) - u(c_ins, par.gamma)
    denom = u(par.w, par.gamma) - u(c_unins_flood, par.gamma)
    
    return num / denom


def V_ins(s, par):
    """Expected utility if insured"""
    c = par.w - (1 - s) * par.pi * par.d
    return u(c, par.gamma)


def V_unins(a, par):
    """True expected utility if uninsured"""
    return (1 - par.p) * u(par.w, par.gamma) + par.p * u(par.w - (1 - a) * par.d, par.gamma)


def social_welfare(s, a, par):
    """Compute social welfare for given policy"""
    q = q_star(s, a, par)
    F_q = beta.cdf(q, par.alpha, par.beta)
    return V_unins(a, par) * F_q + V_ins(s, par) * (1 - F_q)


def budget_spent(s, a, par):
    """Compute budget expenditure"""
    q = q_star(s, a, par)
    F_q = beta.cdf(q, par.alpha, par.beta)
    return a * par.p * par.d * F_q + s * par.pi * par.d * (1 - F_q)


def solve_optimal_policy(par, x0=None):
    """Solve for optimal (s, a) using constrained optimization"""
    
    def neg_welfare(x):
        s, a = x
        return -social_welfare(s, a, par)
    
    def budget_constraint(x):
        s, a = x
        return par.B - budget_spent(s, a, par)
    
    if x0 is None:
        x0 = [0.3, 0.3]
    
    # Bounds: s and a in [0, 1]
    bounds = [(1e-6, 1-1e-6), (1e-6, 1-1e-6)]
    
    # Budget constraint: spending <= B
    constraints = {'type': 'eq', 'fun': budget_constraint}
    
    result = minimize(
        neg_welfare, x0, method='SLSQP',
        bounds=bounds, constraints=constraints,
        options={'ftol': 1e-10, 'maxiter': 1000}
    )
    
    s_opt, a_opt = result.x
    
    # Compute shadow value numerically
    # TODO: understand this better
    eps = 1e-6
    par_plus = Parameters(
        w=par.w, d=par.d, p=par.p, pi=par.pi, gamma=par.gamma,
        B=par.B + eps, mean_q=par.mean_q, var_q=par.var_q
    )
    result_plus = minimize(
        lambda x: -social_welfare(x[0], x[1], par_plus),
        [s_opt, a_opt], method='SLSQP',
        bounds=bounds,
        constraints={'type': 'eq', 'fun': lambda x: par_plus.B - budget_spent(x[0], x[1], par_plus)}
    )
    welfare_plus = -result_plus.fun
    welfare_base = -result.fun
    lam_opt = (welfare_plus - welfare_base) / eps
    
    return s_opt, a_opt, lam_opt, result.success


def compute_outcomes(s, a, par):
    """Compute equilibrium outcomes"""
    q = q_star(s, a, par)
    F_q = beta.cdf(q, par.alpha, par.beta)
    
    welfare = V_unins(a, par) * F_q + V_ins(s, par) * (1 - F_q)
    spending = a * par.p * par.d * F_q + s * par.pi * par.d * (1 - F_q)
    
    return {
        'q_star': q,
        'frac_uninsured': F_q,
        'frac_insured': 1 - F_q,
        'welfare': welfare,
        'spending': spending,
        'mean_belief': par.mean_q
    }


def subsidy_given_relief(a, par):
    """
    Compute subsidy s given disaster relief a, satisfying budget constraint.
    
    Solves: budget_spent(s, a, par) = par.B for s
    
    Args:
        a: disaster relief level [0, 1]
        par: Parameters object
    
    Returns:
        s: subsidy level that exhausts the budget
    """
    from scipy.optimize import brentq
    
    def budget_residual(s):
        return budget_spent(s, a, par) - par.B
    
    try:
        # Search for s in (0, 1) that satisfies budget constraint
        s = brentq(budget_residual, 1e-6, 1 - 1e-6)
        return s
    except ValueError:
        # If no solution exists in (0, 1), return boundary value
        if budget_residual(1e-6) > 0:
            return 1e-6  # Budget exceeded even at minimum s
        else:
            return 1 - 1e-6  # Budget allows maximum s


def relief_given_subsidy(s, par):
    """
    Compute disaster relief a given subsidy s, satisfying budget constraint.
    
    Solves: budget_spent(s, a, par) = par.B for a
    
    Args:
        s: subsidy level [0, 1]
        par: Parameters object
    
    Returns:
        a: disaster relief level that exhausts the budget
    """
    from scipy.optimize import brentq
    
    def budget_residual(a):
        return budget_spent(s, a, par) - par.B
    
    try:
        # Search for a in (0, 1) that satisfies budget constraint
        a = brentq(budget_residual, 1e-6, 1 - 1e-6)
        return a
    except ValueError:
        # If no solution exists in (0, 1), return boundary value
        if budget_residual(1e-6) > 0:
            return 1e-6  # Budget exceeded even at minimum a
        else:
            return 1 - 1e-6  # Budget allows maximum a


def compute_welfare_vs_budget_allocation(par, n_points=11):
    """
    Compute social welfare for different budget allocations to insurance subsidy.
    
    For each budget fraction allocated to subsidy (0%, 10%, 20%, ..., 100%),
    computes the corresponding s and a values that exhaust the budget, and
    calculates the resulting social welfare.
    
    Args:
        par: Parameters object
        n_points: number of points to compute (default: 11 for 0%, 10%, ..., 100%)
    
    Returns:
        results: dict with arrays of fractions, s values, a values, and welfare
    """
    fractions = np.linspace(0, 1, n_points)
    s_values = np.zeros(n_points)
    a_values = np.zeros(n_points)
    welfare_values = np.zeros(n_points)
    
    for i, frac in enumerate(fractions):
        # Budget allocated to subsidy
        B_subsidy = frac * par.B
        # Budget allocated to disaster relief
        B_relief = (1 - frac) * par.B
        
        # Compute q_star for different (s, a) pairs
        # We need to find s and a such that spending matches allocation
        # This is complex because q_star depends on both s and a
        
        if frac == 0:
            # All budget to disaster relief, no subsidy
            s = 1e-6
            a = relief_given_subsidy(s, par)
        elif frac == 1:
            # All budget to subsidy, no disaster relief
            a = 1e-6
            s = subsidy_given_relief(a, par)
        else:
            # Mixed allocation - need to solve system
            # Use iterative approach: given fraction, find s and a
            from scipy.optimize import minimize_scalar
            
            def objective(s):
                # Given s, compute implied a from budget constraint
                a = relief_given_subsidy(s, par)
                # Compute actual spending on subsidy
                spending = budget_spent(s, a, par)
                q = q_star(s, a, par)
                F_q = beta.cdf(q, par.alpha, par.beta)
                subsidy_spending = s * par.pi * par.d * (1 - F_q)
                # We want subsidy_spending = frac * B
                return (subsidy_spending - frac * par.B) ** 2
            
            result = minimize_scalar(objective, bounds=(1e-6, 1-1e-6), method='bounded')
            s = result.x
            a = relief_given_subsidy(s, par)
        
        s_values[i] = s
        a_values[i] = a
        welfare_values[i] = social_welfare(s, a, par)
    
    results = {
        'fractions': fractions,
        's_values': s_values,
        'a_values': a_values,
        'welfare_values': welfare_values
    }
    
    return results


def compute_mvpf_components(s, a, par):
    """
    Compute MVPF sub-terms analytically at policy (s, a).

    dI/ds is derived from the beta PDF via the envelope theorem;
    dI/da follows from the ratio trick (eq. 7 in model notes).
    Assumes actuarially fair insurance: premium = p·d.

    Returns a dict with all numerator/denominator components for MVPF_s and MVPF_a.
    """
    pd = par.p * par.d

    c_I   = par.w - (1 - s) * pd
    c_U_F = par.w - (1 - a) * par.d

    Delta_u = u(par.w, par.gamma) - u(c_U_F, par.gamma)
    qs = (u(par.w, par.gamma) - u(c_I, par.gamma)) / Delta_u

    du_I  = u_prime(c_I,   par.gamma)
    du_UF = u_prime(c_U_F, par.gamma)

    f_q = beta.pdf(qs, par.alpha, par.beta)
    I   = 1 - beta.cdf(qs, par.alpha, par.beta)

    # Envelope-theorem derivatives (dq*/ds = -du_I*pd/Delta_u, dq*/da = q*·du_UF·d/Delta_u)
    dI_ds =  f_q * du_I  * pd         / Delta_u   # > 0: subsidy raises take-up
    dI_da = -f_q * qs    * du_UF * par.d / Delta_u  # < 0: relief crowds out

    internality = (par.p - qs) * Delta_u           # (p - q*) * Delta_u  [eq. 4]

    # ── MVPF_s decomposition  [eq. 5] ──────────────────────────────────────
    ic_s = internality * dI_ds      # internality correction: welfare gain from switchers
    db_s = pd * du_I   * I          # direct benefit to insured
    dc_s = pd * I                   # direct fiscal cost
    fe_s = pd * (s - a) * dI_ds    # fiscal externality from switching
    MVPF_s = (ic_s + db_s) / (dc_s + fe_s)

    # ── MVPF_a decomposition  [eq. 6] ──────────────────────────────────────
    co_a = internality * dI_da      # crowd-out loss (negative)
    db_a = pd * du_UF  * (1 - I)   # direct benefit to uninsured flood victims
    dc_a = pd * (1 - I)            # direct fiscal cost
    fe_a = pd * (s - a) * dI_da    # fiscal externality from switching
    MVPF_a = (co_a + db_a) / (dc_a + fe_a)

    return dict(
        s=s, a=a, q_star=qs, I=I,
        internality=internality, dI_ds=dI_ds, dI_da=dI_da,
        ic_s=ic_s, db_s=db_s, dc_s=dc_s, fe_s=fe_s, MVPF_s=MVPF_s,
        co_a=co_a, db_a=db_a, dc_a=dc_a, fe_a=fe_a, MVPF_a=MVPF_a,
    )


def compute_mvpfs_along_frontier(par, n_points=51):
    """
    Sweep the budget frontier and return MVPF components as arrays.

    For each budget-to-subsidy fraction in [0, 1], finds the (s, a) pair
    on the budget constraint and computes full MVPF decomposition.
    """
    res = compute_welfare_vs_budget_allocation(par, n_points=n_points)
    rows = [compute_mvpf_components(s, a, par)
            for s, a in zip(res['s_values'], res['a_values'])]

    keys = ['s', 'a', 'q_star', 'I', 'MVPF_s', 'MVPF_a',
            'ic_s', 'db_s', 'dc_s', 'fe_s',
            'co_a', 'db_a', 'dc_a', 'fe_a']
    out = {k: np.array([r[k] for r in rows]) for k in keys}
    out['fractions']      = res['fractions']
    out['welfare_values'] = res['welfare_values']
    return out


def plot_mvpf_decomposition(mvpf_data, label='', figsize=(12, 9)):
    """
    Four-panel figure: MVPF curves + sub-term decompositions along the frontier.

    Panels:
      top-left:  MVPF_s and MVPF_a vs budget allocation
      top-right: MVPF_s numerator terms (internality correction + direct benefit)
      bot-left:  MVPF_a numerator terms (crowd-out + direct benefit)
      bot-right: Denominator terms (direct cost + fiscal externality) for both

    x-axis: share of budget allocated to insurance subsidy (%).
    Dashed vertical line marks the welfare-maximising allocation.
    """
    pct = mvpf_data['fractions'] * 100
    opt = int(np.argmax(mvpf_data['welfare_values']))

    fig, axes = plt.subplots(2, 2, figsize=figsize)

    def vline(ax):
        ax.axvline(pct[opt], color='gray', lw=1, ls='--',
                   label=f'Optimal ({pct[opt]:.0f}% → subsidy)')

    # ── top-left: MVPF curves ───────────────────────────────────────────────
    ax = axes[0, 0]
    ax.plot(pct, mvpf_data['MVPF_s'], color='steelblue',  lw=2, label='MVPF$_s$ (subsidy)')
    ax.plot(pct, mvpf_data['MVPF_a'], color='darkorange', lw=2, label='MVPF$_a$ (relief)')
    ax.axhline(0, color='black', lw=0.5)
    vline(ax)
    ax.set_xlabel('Budget → subsidy (%)')
    ax.set_ylabel('MVPF')
    ax.set_title('Marginal value of public funds')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # ── top-right: MVPF_s numerator ─────────────────────────────────────────
    ax = axes[0, 1]
    ax.plot(pct, mvpf_data['ic_s'], color='green',     lw=2,
            label=r'Internality $(p-q^*)\Delta u \cdot \partial I/\partial s$')
    ax.plot(pct, mvpf_data['db_s'], color='steelblue', lw=2,
            label=r"Direct benefit $pd\,u'(c_I)\cdot I$")
    ax.plot(pct, mvpf_data['ic_s'] + mvpf_data['db_s'], color='black', lw=2, ls='--',
            label='Total numerator')
    ax.axhline(0, color='black', lw=0.5)
    vline(ax)
    ax.set_xlabel('Budget → subsidy (%)')
    ax.set_ylabel('Welfare units')
    ax.set_title('MVPF$_s$ numerator terms')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── bottom-left: MVPF_a numerator ───────────────────────────────────────
    ax = axes[1, 0]
    ax.plot(pct, mvpf_data['co_a'], color='red',       lw=2,
            label=r'Crowd-out $(p-q^*)\Delta u \cdot \partial I/\partial a$')
    ax.plot(pct, mvpf_data['db_a'], color='darkorange', lw=2,
            label=r"Direct benefit $pd\,u'(c_{U,F})\cdot(1-I)$")
    ax.plot(pct, mvpf_data['co_a'] + mvpf_data['db_a'], color='black', lw=2, ls='--',
            label='Total numerator')
    ax.axhline(0, color='black', lw=0.5)
    vline(ax)
    ax.set_xlabel('Budget → subsidy (%)')
    ax.set_ylabel('Welfare units')
    ax.set_title('MVPF$_a$ numerator terms')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ── bottom-right: denominator terms ─────────────────────────────────────
    ax = axes[1, 1]
    ax.plot(pct, mvpf_data['dc_s'], color='steelblue',  lw=2,
            label=r'Direct cost$_s$  $pd \cdot I$')
    ax.plot(pct, mvpf_data['fe_s'], color='steelblue',  lw=2, ls='--',
            label=r'Fiscal ext.$_s$  $pd(s-a)\,\partial I/\partial s$')
    ax.plot(pct, mvpf_data['dc_a'], color='darkorange', lw=2,
            label=r'Direct cost$_a$  $pd \cdot (1-I)$')
    ax.plot(pct, mvpf_data['fe_a'], color='darkorange', lw=2, ls='--',
            label=r'Fiscal ext.$_a$  $pd(s-a)\,\partial I/\partial a$')
    ax.axhline(0, color='black', lw=0.5)
    vline(ax)
    ax.set_xlabel('Budget → subsidy (%)')
    ax.set_ylabel('Budget units')
    ax.set_title('Denominator terms (fiscal costs)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    if label:
        fig.suptitle(label, fontsize=13)
    plt.tight_layout()
    return fig, axes


def compare_beta_distributions(par_list, max_q=1, labels=None, figsize=(8, 5)):
    """
    Compare PDF of beta distributions for multiple parameter sets.
    
    Args:
        par_list: list of Parameters objects to compare
        labels: list of labels for each parameter set (default: auto-generated)
        figsize: tuple, figure size (default: (8, 5))
    
    Returns:
        fig, ax: matplotlib figure and axis objects
    """
    if labels is None:
        labels = [f'σ = {np.sqrt(par.var_q):.4f}' for par in par_list]
    
    # Use the maximum pi for x range
    x = np.linspace(0, 1, 10000)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color palette for multiple lines
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(par_list)))
    
    for i, (par, label, color) in enumerate(zip(par_list, labels, colors)):
        # Compute PDF
        pdf = beta.pdf(x, par.alpha, par.beta)
        
        # Plot PDF
        ax.plot(x, pdf, linewidth=2, color=color, label=label)
    
    # Configure plot
    ax.set_xlabel('Belief q (flood probability)', fontsize=12)
    ax.set_ylabel('Probability Density', fontsize=12)
    ax.set_title('PDF Comparison', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max_q)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def compare_welfare_vs_budget_allocation(results_list, labels=None, figsize=(8, 5)):
    """
    Compare social welfare curves for multiple parameter sets.
    
    Args:
        results_list: list of results dicts from compute_welfare_vs_budget_allocation
        labels: list of labels for each result set (default: auto-generated)
        figsize: tuple, figure size (default: (12, 5))
    
    Returns:
        fig, ax: matplotlib figure and axis objects
    """
    if labels is None:
        labels = [f'Config {i+1}' for i in range(len(results_list))]
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color palette for multiple lines
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(results_list)))
    
    for results, label, color in zip(results_list, labels, colors):
        fractions = results['fractions']
        welfare_values = results['welfare_values']
        
        ax.plot(fractions * 100, welfare_values, linewidth=2,
                color=color, label=label)
        
        # Mark maximum welfare point
        max_idx = np.argmax(welfare_values)
        ax.plot(fractions[max_idx] * 100, welfare_values[max_idx], 
                marker='o', markersize=5, color=color, 
                markeredgecolor='black', markeredgewidth=1.)
    
    ax.set_xlabel('Budget Allocated to Insurance Subsidy (%)', fontsize=12)
    ax.set_ylabel('Social Welfare', fontsize=12)
    ax.set_title('Social Welfare Comparison', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    
    return fig, ax
