import numpy as np
from scipy.stats import norm

def compute_greeks(S, K, T, r, sigma, option_type='call'):
    """
    Analytical Greeks for a European option.

    Returns a dict with delta, gamma, vega, theta, rho.
    """
    if T <= 0:
        return {'delta': None, 'gamma': None, 'vega': None, 'theta': None, 'rho': None}

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    pdf_d1 = norm.pdf(d1)

    # Delta
    if option_type == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1

    # Gamma (same for call and put)
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))

    # Vega (same for call and put) — per 1% move in vol
    vega = S * pdf_d1 * np.sqrt(T) / 100

    # Theta — per calendar day
    term1 = -(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
    if option_type == 'call':
        theta = (term1 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (term1 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

    # Rho — per 1% move in rates
    if option_type == 'call':
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    return {
        'delta': round(delta, 4),
        'gamma': round(gamma, 4),
        'vega':  round(vega, 4),
        'theta': round(theta, 4),
        'rho':   round(rho, 4)
    }