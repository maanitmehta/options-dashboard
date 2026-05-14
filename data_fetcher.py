import yfinance as yf
import pandas as pd


def get_spot_price(ticker):
    tk = yf.Ticker(ticker)
    hist = tk.history(period="1d")
    if hist.empty:
        raise ValueError(f"No price data found for {ticker}")
    return round(hist["Close"].iloc[-1], 4)


def get_risk_free_rate():
    irx = yf.Ticker("^IRX")
    hist = irx.history(period="1d")
    if hist.empty:
        print("Warning: could not fetch risk-free rate, defaulting to 0.05")
        return 0.05
    return round(hist["Close"].iloc[-1] / 100, 4)


def get_option_chain(ticker, expiry=None):
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
    tk = yf.Ticker(ticker)
    expirations = tk.options
    if not expirations:
        raise ValueError(f"No options data for {ticker}")
    return list(expirations)


def get_atm_iv(ticker, expiry, option_type='call'):
    """
    Fetch the ATM implied volatility from the live option chain.
    Returns IV as a decimal e.g. 0.25 for 25%.
    """
    import datetime
    from iv_solver import implied_volatility

    S = get_spot_price(ticker)
    r = get_risk_free_rate()
    calls, puts, _ = get_option_chain(ticker, expiry)

    chain = calls if option_type == 'call' else puts

    chain = chain.copy()
    chain['dist'] = abs(chain['strike'] - S)
    atm_row = chain.sort_values('dist').iloc[0]

    price = atm_row['mid'] if atm_row['mid'] > 0 else atm_row['lastPrice']

    expiry_dt = datetime.datetime.strptime(expiry, '%Y-%m-%d')
    T = max((expiry_dt - datetime.datetime.today()).days / 365, 1/365)

    iv = implied_volatility(price, S, atm_row['strike'], T, r, option_type)
    return round(iv, 4) if iv else 0.20