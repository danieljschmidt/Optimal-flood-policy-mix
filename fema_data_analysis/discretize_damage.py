import numpy as np


def discretize_conditional_means(samples, n_bins, value_range):
    
    min_val, max_val = value_range
    bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    
    discrete_values = np.zeros(n_bins)
    weights = np.zeros(n_bins)
    
    valid_samples = samples[(samples >= min_val) & (samples <= max_val)]
    
    for i in range(n_bins):
        left_edge = bin_edges[i]
        right_edge = bin_edges[i + 1]
        
        if i == n_bins - 1:
            bin_samples = valid_samples[(valid_samples >= left_edge) & 
                                      (valid_samples <= right_edge)]
        else:
            bin_samples = valid_samples[(valid_samples >= left_edge) & 
                                      (valid_samples < right_edge)]
        
        weights[i] = len(bin_samples) / len(valid_samples)
        
        # empty bin (e.g. damage/home value cannot exceed 1 - land share): weight 0,
        # value at the bin midpoint so weighted sums stay finite instead of NaN
        discrete_values[i] = np.mean(bin_samples) if len(bin_samples) else 0.5 * (left_edge + right_edge)

    return discrete_values, weights


def gauss_three_point(samples):
    """3-point grid matching the first five moments of the sample (Gaussian quadrature)."""
    m = [np.mean(samples ** k) for k in range(6)]
    H = np.array([[m[i + j] for j in range(3)] for i in range(3)])
    c = np.linalg.solve(H, -np.array(m[3:6]))
    nodes = np.sort(np.roots([1, c[2], c[1], c[0]]).real)
    probs = np.linalg.solve(np.vander(nodes, 3, increasing=True).T, m[:3])
    return nodes, probs