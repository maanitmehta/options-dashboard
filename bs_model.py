import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    Black-Scholes price for a European option.

    S     : current spot price
    K     : strike price
    T     : time to expiry in years (e.g. 30 days = 30/365)
    r     : risk-free rate as a decimal (e.g. 5% = 0.05)
    sigma : volatility as a decimal (e.g. 20% = 0.20)
    option_type : 'call' or 'put'
    """
    if T <= 0:
        return max(S - K, 0) if option_type == 'call' else max(K - S, 0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return round(price, 4)