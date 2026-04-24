"""
Solves for optimal subsidy (s) and disaster relief (a) given:
- Cobb-Douglas utility: u(c) = (c^(1-\phi)+h^phi)^(1-γ) / (1-γ)
- Beta-distributed subjective beliefs: q ~ Beta(α, β)
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import beta
from scipy.stats import lognorm
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
    mean_gamma: float = 2
    var_gamma: float = 0.27
    gamma_max: float = 5.0   # truncation for numerical stability
    n_gamma: int = 25        # number of grid points
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
    
    def gamma_grid(self):
        """
        Construct grid and weights for truncated lognormal CRRA distribution
        matching mean and variance approximately.
        """
        mean = self.mean_gamma
        var = self.var_gamma
    
        # Convert mean/var of gamma → lognormal parameters
        sigma2 = np.log(1 + var / mean**2)
        mu = np.log(mean) - 0.5 * sigma2
    
        sigma = np.sqrt(sigma2)
    
        # Create evenly spaced quantiles
        probs = np.linspace(1e-4, 1 - 1e-4, self.n_gamma)
        dist = lognorm(s=sigma, scale=np.exp(mu))
        gamma_vals = dist.ppf(probs)
    
        # Truncate extreme tail for stability
        gamma_vals = np.clip(gamma_vals, 1e-4, self.gamma_max)
    
        weights = np.ones_like(gamma_vals) / len(gamma_vals)
    
        return gamma_vals, weights


def u(c, gamma):
    """CRRA utility function - when gamma is close to 1, reduce to log utility"""
    if abs(gamma - 1.0) < 1e-6:
        return np.log(c)
    return c ** (1 - gamma) / (1 - gamma)


def u_prime(c, gamma):
    """Marginal utility"""
    return c ** (-gamma)


def q_star_gamma(s, a, gamma, par):
    """Insurance purchase threshold"""
    c_ins = par.w - (1 - s) * par.pi * par.d
    c_unins_flood = par.w - (1 - a) * par.d
    
    num = u(par.w, gamma) - u(c_ins, gamma)
    denom = u(par.w, gamma) - u(c_unins_flood, gamma)
    
    return num / denom


def social_welfare(s, a, par):
    gamma_vals, weights = par.gamma_grid()

    total = 0.0

    for gamma, wgt in zip(gamma_vals, weights):
        q = q_star_gamma(s, a, gamma, par)
        F_q = beta.cdf(q, par.alpha, par.beta)

        V_ins = u(par.w - (1 - s) * par.pi * par.d, gamma)
        V_unins = (1 - par.p) * u(par.w, gamma) + par.p * u(par.w - (1 - a) * par.d, gamma)

        total += wgt * (V_unins * F_q + V_ins * (1 - F_q))

    return total


def budget_spent(s, a, par):
    gamma_vals, weights = par.gamma_grid()

    total = 0.0

    for gamma, wgt in zip(gamma_vals, weights):
        q = q_star_gamma(s, a, gamma, par)
        F_q = beta.cdf(q, par.alpha, par.beta)

        total += wgt * (
            a * par.p * par.d * F_q +
            s * par.pi * par.d * (1 - F_q)
        )

    return total


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
        w=par.w, d=par.d, p=par.p, pi=par.pi, mean_gamma=par.mean_gamma, var_gamma=par.var_gamma,
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
    gamma_vals, weights = par.gamma_grid()

    frac_uninsured = 0.0
    welfare = 0.0

    for gamma, wgt in zip(gamma_vals, weights):
        q = q_star_gamma(s, a, gamma, par)
        F_q = beta.cdf(q, par.alpha, par.beta)

        frac_uninsured += wgt * F_q

        V_ins = u(par.w - (1 - s) * par.pi * par.d, gamma)
        V_unins = (1 - par.p) * u(par.w, gamma) + par.p * u(par.w - (1 - a) * par.d, gamma)

        welfare += wgt * (V_unins * F_q + V_ins * (1 - F_q))

    return {
        'frac_uninsured': frac_uninsured,
        'frac_insured': 1 - frac_uninsured,
        'welfare': welfare
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
