import numpy as np
from scipy import stats

def perform_mann_whitney_u(group1, group2):
    """
    Performs the Mann-Whitney U test on two independent samples with robust input validation.
    
    Parameters:
    group1 (list or array-like): Observations from sample 1.
    group2 (list or array-like): Observations from sample 2.
    
    Returns:
    tuple: The Mann-Whitney U statistic and the p-value.
    """
    g1 = np.asarray(group1, dtype=float)
    g2 = np.asarray(group2, dtype=float)
    
    if g1.size == 0 or g2.size == 0:
        raise ValueError("Input groups cannot be empty.")
        
    if not np.isfinite(g1).all() or not np.isfinite(g2).all():
        raise ValueError("Input data must contain finite numeric values.")

    statistic, p_value = stats.mannwhitneyu(g1, g2, alternative='two-sided')
    return statistic, p_value

# Example execution
if __name__ == "__main__":
    sample_a = [12, 14, 19, 21, 30]
    sample_b = [22, 28, 35, 40, 45]
    
    u_stat, p_val = perform_mann_whitney_u(sample_a, sample_b)
    print(f"U-statistic: {u_stat}")
    print(f"P-value: {p_val}")
