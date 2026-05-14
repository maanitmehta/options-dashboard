# Options Pricing & Greeks Dashboard

> An interactive, fully deployed derivatives pricing dashboard built in Python. Prices European options using Black-Scholes (analytical) and Monte Carlo simulation (numerical), with real-time market data, implied volatility analysis, 3D Greeks surfaces, and multi-leg payoff diagrams.

🔗 **Live Demo:** https://options-dashboard-okuw.onrender.com  
📁 **GitHub:** https://github.com/maanitmehta/options-dashboard

---

![Status](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![Dash](https://img.shields.io/badge/Dash-2.x-lightblue) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview

This project was built to demonstrate practical derivatives knowledge relevant to trading, structuring, and quantitative finance roles. It covers the full pipeline from raw financial theory to a live, publicly accessible web application — pricing, Greeks, implied volatility, strategy visualisation, and real-time market data, all in one tool.

---

## Live Features

### Pricing Engine

| Method | Description |
|---|---|
| Black-Scholes | Closed-form analytical solution for European calls and puts |
| Monte Carlo | 100,000 GBM paths, discounted expectation, 95% confidence interval |
| Cross-validation | BS price displayed alongside MC price — should always fall within the CI |

### Greeks

| Greek | Definition | Formula |
|---|---|---|
| Delta | Rate of change of price w.r.t. spot | N(d1) for calls, N(d1)−1 for puts |
| Gamma | Rate of change of delta w.r.t. spot | N'(d1) / (S·σ·√T) |
| Vega | Sensitivity to volatility | S·N'(d1)·√T |
| Theta | Time decay per calendar day | Multi-term BS derivative / 365 |
| Rho | Sensitivity to interest rates | K·T·e^(−rT)·N(d2) for calls |

All Greeks visualised as:
- **2D chart** — all five Greeks vs strike for a fixed expiry
- **3D surface** — fully vectorised NumPy computation across a 25×25 strike × time-to-expiry grid

### Implied Volatility

- **IV solver** — numerically inverts the BS formula using `scipy.optimize.brentq`
- **IV smile** — plots IV against strike for a single expiry, revealing the volatility skew in equity markets
- **IV surface** — 3D surface across strike and expiry from live option chain data across 6 expiries
- **Use Market IV button** — fetches the ATM implied vol from the live chain and plugs it into the pricing engine

### Multi-Leg Payoff Diagrams

| Strategy | Description |
|---|---|
| Single Leg | Long call or put — basic directional exposure |
| Straddle | Long call + put at same strike — profits from large moves either direction |
| Strangle | OTM call + OTM put — cheaper than straddle, needs larger move to profit |
| Bull Call Spread | Buy ATM call, sell OTM call — capped upside, reduced premium |
| Bear Put Spread | Buy ATM put, sell OTM put — capped downside, reduced premium |

All diagrams show profit/loss zones in green/red with max profit, max loss, and premium annotated.

### Monte Carlo Visualiser

- **Path plot** — 50 GBM paths coloured blue (ITM at expiry) or red (OTM)
- **Convergence chart** — running MC price from N=1 to 20,000 with 95% confidence band and BS price overlay

### Market Data

- Live spot prices and option chains via **yfinance**
- Risk-free rate proxied via 13-week T-bill yield (^IRX)
- Liquidity filtering — strips zero-bid and zero-volume options before IV computation
- Mid-price computation from bid/ask spread

### UX & Interface

- Searchable dropdown with 23 popular tickers (AAPL, MSFT, TSLA, NVDA, SPY, AMZN, GOOGL, META, JPM, GS, and more)
- Custom ticker input with real-time validation — shows green (valid with options), orange (valid but no options), red (not found)
- Strike auto-sets to ATM on ticker load
- Live ITM / ATM / OTM moneyness label
- Preset strategy buttons — ATM Call, ATM Put, ATM Straddle, OTM Call, OTM Put, Bull Spread, Bear Spread
- Expiry dropdown shows days remaining e.g. "2026-06-20 (37d)"
- Dark / light mode toggle
- CSV export of full pricing and Greeks summary
- Loading spinner and friendly error messages

---

## Key Formulas

**Black-Scholes**

    C = S·N(d1) − K·e^(−rT)·N(d2)
    P = K·e^(−rT)·N(−d2) − S·N(−d1)

    d1 = [ln(S/K) + (r + σ²/2)·T] / (σ·√T)
    d2 = d1 − σ·√T

**Monte Carlo (Geometric Brownian Motion)**

    S_T = S · exp((r − ½σ²)·T + σ·√T · Z),   Z ~ N(0,1)
    Price = e^(−rT) · E[max(S_T − K, 0)]
    95% CI: Price ± 1.96 · std / √N

**Implied Volatility**

    Find σ* such that BS(S, K, T, r, σ*) = market_price
    Solved via Brent's method on interval [1e-6, 10.0]

---

## Tech Stack

| Layer | Technology |
|---|---|
| Pricing & maths | Python, NumPy, SciPy |
| Market data | yfinance |
| Visualisation | Plotly |
| Dashboard | Dash, Dash Bootstrap Components |
| Deployment | Render, Gunicorn |
| Version control | Git, GitHub |

---

## Project Structure

    options_dashboard/
    ├── app.py            # Main Dash app — layout, all callbacks
    ├── bs_model.py       # Black-Scholes pricing engine
    ├── greeks.py         # Analytical Greeks calculator
    ├── mc_pricer.py      # Monte Carlo pricer with confidence intervals
    ├── iv_solver.py      # Implied volatility solver (Brent's method)
    ├── iv_plot.py        # IV smile and 3D surface plots
    ├── greeks_plot.py    # Greeks 2D charts and vectorised 3D surfaces
    ├── payoff.py         # Multi-leg payoff diagram builder
    ├── mc_plot.py        # GBM path visualiser and convergence chart
    ├── data_fetcher.py   # yfinance market data + ATM IV fetcher
    ├── requirements.txt  # Python dependencies
    └── Procfile          # Render deployment config

---

## Setup & Installation

    git clone https://github.com/maanitmehta/options-dashboard.git
    cd options-dashboard
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python app.py

Open **http://127.0.0.1:8050**

---

## How to Use

1. Select a ticker from the dropdown or type any US equity ticker in the custom input
2. Expiries, spot price, and risk-free rate load automatically
3. Click **Use Market IV** to calibrate volatility to live market prices
4. Use a **preset strategy button** or manually set strike, T, and option type
5. Click **Price Option** — all 7 tabs populate instantly
6. Click **Export CSV** to download the full pricing and Greeks summary

---

## Financial Concepts Demonstrated

- Risk-neutral valuation and the Black-Scholes PDE
- Geometric Brownian Motion and Monte Carlo methods
- Greeks as partial derivatives of the option price function
- Implied volatility as the market's forward-looking vol estimate
- Volatility skew and its interpretation in equity markets
- Options strategy construction and payoff decomposition
- Numerical root-finding (Brent's method) for IV inversion

---

## Author

**Maanit Mehta**  
MSc Financial Modelling & Investment, University of Glasgow  
BCom Financial Analytics, Christ University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Maanit_Mehta-blue)](https://www.linkedin.com/in/maanit-mehta/)
[![GitHub](https://img.shields.io/badge/GitHub-maanitmehta-black)](https://github.com/maanitmehta)
