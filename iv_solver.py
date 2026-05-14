import numpy as np
from scipy.optimize import brentq
from bs_model import black_scholes


def implied_volatility(market_price, S, K, T, r, option_type='call'):
    if T <= 0:
        return None
    if market_price <= 0:
        return None

    intrinsic = max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    if market_price < intrinsic * 0.999:
        return None

    def objective(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - market_price

    try:
        iv = brentq(objective, 1e-6, 10.0, xtol=1e-6, maxiter=500)
        return round(iv, 6)
    except (ValueError, RuntimeError):
        return None


def compute_iv_surface(calls_df, puts_df, S, T, r):
    import pandas as pd

    def iv_row(row, option_type):
        price = row['mid'] if row['mid'] > 0 else row['lastPrice']
        if price <= 0 or row['bid'] == 0:
            return None
        return implied_volatility(price, S, row['strike'], T, r, option_type)

    calls = calls_df.copy()
    puts = puts_df.copy()

    calls['iv'] = calls.apply(lambda r: iv_row(r, 'call'), axis=1)
    puts['iv'] = puts.apply(lambda r: iv_row(r, 'put'), axis=1)

    calls['type'] = 'call'
    puts['type'] = 'put'

    combined = pd.concat([calls, puts], ignore_index=True)
    combined = combined.dropna(subset=['iv'])
    combined = combined[combined['iv'] > 0.01]
    combined = combined[combined['iv'] < 5.0]

    return combined[['type', 'strike', 'mid', 'iv']].sort_values('strike').reset_index(drop=True)


def get_iv_smile_data(ticker, expiry=None):
    import datetime
    from data_fetcher import get_option_chain, get_spot_price, get_risk_free_rate

    S = get_spot_price(ticker)
    r = get_risk_free_rate()
    calls, puts, expiry_used = get_option_chain(ticker, expiry)

    expiry_dt = datetime.datetime.strptime(expiry_used, '%Y-%m-%d')
    T = max((expiry_dt - datetime.datetime.today()).days / 365, 1/365)

    surface = compute_iv_surface(calls, puts, S, T, r)
    surface['moneyness'] = round(surface['strike'] / S, 4)
    surface['expiry'] = expiry_used
    surface['S'] = S
    surface['T'] = round(T, 6)

    return surface, S, T, r, expiry_used
