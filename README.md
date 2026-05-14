# Options Pricing & Greeks Dashboard

An interactive dashboard for pricing European options using Black-Scholes and Monte Carlo simulation, with real-time market data, Greeks surfaces, and implied volatility analysis.

## Live Demo
[[(https://options-dashboard-okuw.onrender.com)]

## Features
- Black-Scholes analytical pricer for calls and puts
- Monte Carlo simulation with 100,000 paths and 95% confidence intervals
- Full Greeks calculator — delta, gamma, vega, theta, rho
- Interactive 3D Greeks surfaces across strike and time to expiry
- Live options chain data via yfinance for any US equity
- Implied volatility solver using Brent's method
- IV smile and 3D volatility surface plots
- Multi-leg payoff diagrams — single leg, straddle, strangle, bull/bear spreads
- GBM path visualiser with MC convergence chart

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/options-dashboard.git
cd options-dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:8050

## Usage
1. Enter a ticker (e.g. AAPL, SPY, TSLA) and click Load Market Data
2. Select an expiry from the dropdown
3. Adjust strike, volatility, and option type
4. Click Price Option to populate all charts and Greeks
5. Switch between tabs to explore payoff diagrams, Greeks surfaces, IV smile, and MC simulation

## Project Structure
## Tech Stack
Python, Dash, Plotly, yfinance, scipy, numpy, pandas

## Author
Maanit Mehta — MSc Financial Modelling & Investment, University of Glasgow
# Options Pricing Dashboard
