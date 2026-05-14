import numpy as np

def monte_carlo_price(S, K, T, r, sigma, option_type='call', n_simulations=100_000, seed=42):
    """
    Monte Carlo pricer for a European option using GBM.

    Returns price, confidence interval lower bound, upper bound.
    """
    rng = np.random.default_rng(seed)

    Z = rng.standard_normal(n_simulations)
    S_T = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)

    if option_type == 'call':
        payoffs = np.maximum(S_T - K, 0)
    elif option_type == 'put':
        payoffs = np.maximum(K - S_T, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    discount = np.exp(-r * T)
    price = discount * np.mean(payoffs)
    std_err = discount * np.std(payoffs) / np.sqrt(n_simulations)

    ci_lower = price - 1.96 * std_err
    ci_upper = price + 1.96 * std_err

    return {
        'price':    round(price, 4),
        'ci_lower': round(ci_lower, 4),
        'ci_upper': round(ci_upper, 4)
    }