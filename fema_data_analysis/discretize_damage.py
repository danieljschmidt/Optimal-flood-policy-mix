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
        
        discrete_values[i] = np.mean(bin_samples)
    
    return discrete_values, weights