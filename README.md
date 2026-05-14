# Options Pricing & Greeks Dashboard

An interactive, fully deployed derivatives pricing dashboard built in Python. Prices European options using both **Black-Scholes** (analytical) and **Monte Carlo simulation** (numerical), with real-time market data, implied volatility analysis, and interactive 3D Greeks surfaces.

🔗 **Live Demo:** https://options-dashboard-okuw.onrender.com  
📁 **GitHub:** https://github.com/maanitmehta/options-dashboard

---

## What This Project Demonstrates

This project was built to signal practical derivatives knowledge relevant to trading, structuring, and quantitative finance roles. It covers:

- **Derivatives pricing theory** — Black-Scholes PDE, risk-neutral valuation, GBM
- **Numerical methods** — Monte Carlo simulation with variance reduction via large sample sizes, Brent's method for root-finding
- **Greeks** — Analytical derivation and visualisation of all first and second-order sensitivities
- **Implied volatility** — Numerical inversion of the BS formula to back out market-implied vol from live option prices
- **Market microstructure** — Mid-price computation, bid-ask filtering, liquidity screening on live option chains
- **Full-stack deployment** — Python backend, interactive Dash frontend, deployed on Render

---

## Features

### Pricing Engine
- **Black-Scholes** analytical pricer for European calls and puts
- **Monte Carlo** simulation with 100,000 GBM paths, discounted expectation, and 95% confidence intervals
- Both methods run simultaneously — BS price should always fall within the MC confidence interval, serving as a live cross-validation

### Greeks Calculator
- Analytical computation of all five Greeks: **delta, gamma, vega, theta, rho**
- **2D chart** — all Greeks plotted against strike for a fixed expiry, with spot price marker
- **3D surface** — fully vectorised numpy computation of each Greek across a strike × time-to-expiry grid, rendered as an interactive Plotly surface

### Implied Volatility
- **IV solver** using `scipy.optimize.brentq` — backs out σ* such that BS(σ*) = market price
- **IV smile** — plots implied volatility against strike for a single expiry, showing the well-known volatility skew in equity markets
- **IV surface** — 3D surface across strike and expiry, built from live option chain data across 6 expiries

### Multi-Leg Payoff Diagrams
- **Single leg** — long call or put P&L at expiry
- **Straddle** — long call + long put at same strike (profits from large moves in either direction)
- **Strangle** — OTM call + OTM put (cheaper than straddle, requires larger move)
- **Bull call spread** — buy ATM call, sell OTM call (capped upside, reduced premium)
- **Bear put spread** — buy ATM put, sell OTM put (capped downside, reduced premium)
- All diagrams show profit/loss zones in green/red with max profit, max loss, and premium annotations

### Monte Carlo Visualiser
- **Path plot** — 50 simulated GBM paths coloured blue (ITM at expiry) or red (OTM)
- **Convergence chart** — running MC price as N increases from 1 to 20,000, with 95% confidence band and BS price overlay, demonstrating convergence

### Live Market Data
- Real-time spot prices, option chains, and risk-free rate (proxied via 13-week T-bill yield ^IRX) via **yfinance**
- Automatic liquidity filtering — strips zero-bid and zero-volume options before IV computation
- Expiry dropdown shows days remaining for intuitive selection

### UX Features
- One-click ticker buttons — AAPL, MSFT, TSLA, NVDA, SPY, AMZN
- Auto-loads market data on ticker selection
- Strike auto-sets to ATM (spot price) on load
- Live ITM / ATM / OTM moneyness label
- Preset strategy buttons — ATM Call, ATM Put, ATM Straddle, OTM Call, OTM Put, Bull Spread, Bear Spread
- Error messages for invalid tickers or missing options data
- Loading spinner during computation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Pricing & maths | Python, NumPy, SciPy |
| Market data | yfinance |
| Visualisation | Plotly |
| Dashboard | Dash, Dash Bootstrap Components |
| Deployment | Render (free tier), Gunicorn |
| Version control | Git, GitHub |

---

## Project Structure
options_dashboard/
├── app.py            # Main Dash application — layout, callbacks, routing
├── bs_model.py       # Black-Scholes pricing engine
├── greeks.py         # Analytical Greeks calculator
├── mc_pricer.py      # Monte Carlo pricer with confidence intervals
├── iv_solver.py      # Implied volatility solver (Brent's method)
├── iv_plot.py        # IV smile and 3D surface visualisations
├── greeks_plot.py    # Greeks 2D charts and vectorised 3D surfaces
├── payoff.py         # Multi-leg payoff diagram builder
├── mc_plot.py        # MC path visualiser and convergence chart
├── data_fetcher.py   # yfinance market data fetcher
├── requirements.txt  # Python dependencies
└── Procfile          # Render deployment config

---

## Setup & Installation

```bash
git clone https://github.com/maanitmehta/options-dashboard.git
cd options-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8050 in your browser.

---

## How to Use

1. Click a ticker button (e.g. **NVDA**) — spot price and expiries load automatically
2. Select an expiry from the dropdown (shows days remaining)
3. Use a **preset strategy button** or manually adjust strike, volatility, option type
4. Click **Price Option** to populate all charts and Greeks
5. Browse the 7 tabs: Payoff Diagram, Greeks vs Strike, Greeks Surface, MC Simulation, MC Paths, IV Smile, IV Surface

---

## Key Financial Concepts Covered

**Black-Scholes formula**
C = S·N(d1) − K·e^(−rT)·N(d2)
d1 = [ln(S/K) + (r + σ²/2)·T] / (σ·√T)
d2 = d1 − σ·√T

**Monte Carlo (GBM)**
S_T = S · exp((r − ½σ²)T + σ√T · Z),  Z ~ N(0,1)
Price = e^(−rT) · E[max(S_T − K, 0)]

**Implied Volatility**
Find σ* such that BS(S, K, T, r, σ*) = market_price
Solved numerically using Brent's method

---

## Author

**Maanit Mehta**  
MSc Financial Modelling & Investment, University of Glasgow  
BCom Financial Analytics, Christ University