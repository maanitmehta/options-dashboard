import yfinance as yf
import pandas as pd

def get_spot_price(ticker):
    """Fetch current spot price for a ticker."""
    tk = yf.Ticker(ticker)
    hist = tk.history(period="1d")
    if hist.empty:
        raise ValueError(f"No price data found for {ticker}")
    return round(hist["Close"].iloc[-1], 4)

def get_risk_free_rate():
    """
    Proxy for risk-free rate using 13-week T-bill yield (^IRX).
    Returns rate as a decimal e.g. 0.05 for 5%.
    """
    irx = yf.Ticker("^IRX")
    hist = irx.history(period="1d")
    if hist.empty:
        print("Warning: could not fetch risk-free rate, defaulting to 0.05")
        return 0.05
    return round(hist["Close"].iloc[-1] / 100, 4)

def get_option_chain(ticker, expiry=None):
    """
    Fetch the full option chain for a ticker.

    If expiry is None, uses the nearest available expiry.
    Returns (calls_df, puts_df, expiry_used).
    """
    tk = yf.Ticker(ticker)
    expirations = tk.options

    if not expirations:
        raise ValueError(f"No options data available for {ticker}")

    if expiry is None:
        expiry = expirations[0]
    elif expiry not in expirations:
        raise ValueError(f"Expiry {expiry} not available. Choose from: {list(expirations)}")

    chain = tk.option_chain(expiry)
    calls = chain.calls[['strike','lastPrice','bid','ask','volume','openInterest','impliedVolatility']].copy()
    puts  = chain.puts[['strike','lastPrice','bid','ask','volume','openInterest','impliedVolatility']].copy()

    calls['mid'] = round((calls['bid'] + calls['ask']) / 2, 4)
    puts['mid']  = round((puts['bid']  + puts['ask'])  / 2, 4)

    return calls, puts, expiry

def get_available_expiries(ticker):
    """Return list of available expiry dates for a ticker."""
    tk = yf.Ticker(ticker)
    expirations = tk.options
    if not expirations:
        raise ValueError(f"No options data for {ticker}")
    return list(expirations)