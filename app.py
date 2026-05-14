import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import datetime

from bs_model import black_scholes
from greeks import compute_greeks
from mc_pricer import monte_carlo_price
from greeks_plot import plot_greeks_surface, plot_greeks_2d
from iv_plot import plot_iv_smile, plot_iv_surface
from data_fetcher import get_spot_price, get_risk_free_rate, get_available_expiries
from payoff import build_payoff_chart
from mc_plot import plot_mc_paths, plot_mc_convergence

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Options Pricing Dashboard"
server = app.server
sidebar = dbc.Card([
    html.H5("Parameters", className="mb-3"),
    dbc.Label("Ticker"),
    dbc.Input(id="ticker", value="AAPL", type="text", className="mb-2"),
    dbc.Label("Expiry"),
    dcc.Dropdown(id="expiry-dropdown", placeholder="Load expiries first", className="mb-2"),
    dbc.Button("Load Market Data", id="load-btn", color="primary", className="mb-3 w-100"),
    html.Hr(),
    dbc.Label("Spot Price (S)"),
    dbc.Input(id="spot", type="number", value=100, step=1, className="mb-2"),
    dbc.Label("Strike Price (K)"),
    dbc.Input(id="strike", type="number", value=100, step=1, className="mb-2"),
    dbc.Label("Time to Expiry (years)"),
    dbc.Input(id="T", type="number", value=0.25, step=0.01, className="mb-2"),
    dbc.Label("Risk-Free Rate"),
    dbc.Input(id="rate", type="number", value=0.05, step=0.001, className="mb-2"),
    dbc.Label("Volatility (σ)"),
    dbc.Input(id="sigma", type="number", value=0.20, step=0.01, className="mb-2"),
    dbc.Label("Option Type"),
    dbc.RadioItems(
        id="option-type",
        options=[{"label": "Call", "value": "call"}, {"label": "Put", "value": "put"}],
        value="call", inline=True, className="mb-3"
    ),
    dbc.Label("Payoff Strategy"),
    dbc.Select(
        id="strategy",
        options=[
            {"label": "Single Leg",       "value": "single"},
            {"label": "Straddle",         "value": "straddle"},
            {"label": "Strangle",         "value": "strangle"},
            {"label": "Bull Call Spread", "value": "bull_spread"},
            {"label": "Bear Put Spread",  "value": "bear_spread"},
        ],
        value="single", className="mb-3"
    ),
    dbc.Button("Price Option", id="price-btn", color="success", className="w-100"),
], body=True, className="h-100")

summary_cards = dbc.Row([
    dbc.Col(dbc.Card([html.H6("BS Price",  className="text-muted mb-1"), html.H3(id="bs-price",  children="—")], body=True)),
    dbc.Col(dbc.Card([html.H6("MC Price",  className="text-muted mb-1"), html.H3(id="mc-price",  children="—")], body=True)),
    dbc.Col(dbc.Card([html.H6("Delta",     className="text-muted mb-1"), html.H3(id="g-delta",   children="—")], body=True)),
    dbc.Col(dbc.Card([html.H6("Gamma",     className="text-muted mb-1"), html.H3(id="g-gamma",   children="—")], body=True)),
    dbc.Col(dbc.Card([html.H6("Vega",      className="text-muted mb-1"), html.H3(id="g-vega",    children="—")], body=True)),
    dbc.Col(dbc.Card([html.H6("Theta",     className="text-muted mb-1"), html.H3(id="g-theta",   children="—")], body=True)),
], className="mb-3")

tabs = dbc.Tabs([
    dbc.Tab(dcc.Graph(id="payoff-chart"),     label="Payoff Diagram"),
    dbc.Tab(dcc.Graph(id="greeks-2d-chart"),  label="Greeks vs Strike"),
    dbc.Tab(dcc.Graph(id="greeks-3d-chart"),  label="Greeks Surface"),
    dbc.Tab(dcc.Graph(id="mc-chart"),         label="MC Simulation"),
    dbc.Tab(dcc.Graph(id="mc-paths-chart"),   label="MC Paths"),
    dbc.Tab(dcc.Graph(id="iv-smile-chart"),   label="IV Smile"),
    dbc.Tab(dcc.Graph(id="iv-surface-chart"), label="IV Surface"),
], className="mt-2")

app.layout = dbc.Container([
    html.H3("Options Pricing & Greeks Dashboard", className="my-3"),
    dbc.Row([
        dbc.Col(sidebar, width=3),
        dbc.Col([summary_cards, tabs], width=9),
    ])
], fluid=True)


@app.callback(
    Output("expiry-dropdown", "options"),
    Output("expiry-dropdown", "value"),
    Output("spot", "value"),
    Output("rate", "value"),
    Input("load-btn", "n_clicks"),
    State("ticker", "value"),
    prevent_initial_call=True
)
def load_market_data(n, ticker):
    try:
        expiries = get_available_expiries(ticker)
        S = get_spot_price(ticker)
        r = get_risk_free_rate()
        options = [{"label": e, "value": e} for e in expiries[:12]]
        return options, expiries[0], round(S, 2), round(r, 4)
    except Exception:
        return [], None, 100, 0.05


@app.callback(
    Output("T", "value"),
    Input("expiry-dropdown", "value"),
    prevent_initial_call=True
)
def update_T(expiry):
    if not expiry:
        return 0.25
    expiry_dt = datetime.datetime.strptime(expiry, '%Y-%m-%d')
    T = max((expiry_dt - datetime.datetime.today()).days / 365, 1/365)
    return round(T, 4)


@app.callback(
    Output("bs-price",       "children"),
    Output("mc-price",       "children"),
    Output("g-delta",        "children"),
    Output("g-gamma",        "children"),
    Output("g-vega",         "children"),
    Output("g-theta",        "children"),
    Output("payoff-chart",   "figure"),
    Output("greeks-2d-chart","figure"),
    Output("greeks-3d-chart","figure"),
    Output("mc-chart",       "figure"),
    Output("mc-paths-chart", "figure"),
    Input("price-btn", "n_clicks"),
    State("spot",        "value"),
    State("strike",      "value"),
    State("T",           "value"),
    State("rate",        "value"),
    State("sigma",       "value"),
    State("option-type", "value"),
    State("strategy",    "value"),
    prevent_initial_call=True
)
def price_option(n, S, K, T, r, sigma, option_type, strategy):
    S, K, T, r, sigma = float(S), float(K), float(T), float(r), float(sigma)
    bs = black_scholes(S, K, T, r, sigma, option_type)
    mc = monte_carlo_price(S, K, T, r, sigma, option_type)
    gk = compute_greeks(S, K, T, r, sigma, option_type)
    fig_payoff   = build_payoff_chart(S, K, T, r, sigma, option_type, strategy)
    fig_g2d      = plot_greeks_2d(S, r, sigma, option_type, T)
    figs_3d      = plot_greeks_surface(S, r, sigma, option_type)
    fig_g3d      = figs_3d['delta']
    fig_mc       = plot_mc_convergence(S, K, T, r, sigma, option_type)
    fig_mc_paths = plot_mc_paths(S, K, T, r, sigma, option_type)
    return (
        f"${bs}",
        f"${mc['price']} (±{round(mc['ci_upper'] - mc['price'], 4)})",
        str(gk['delta']),
        str(gk['gamma']),
        str(gk['vega']),
        str(gk['theta']),
        fig_payoff,
        fig_g2d,
        fig_g3d,
        fig_mc,
        fig_mc_paths,
    )


@app.callback(
    Output("iv-smile-chart",   "figure"),
    Output("iv-surface-chart", "figure"),
    Input("load-btn", "n_clicks"),
    State("ticker",          "value"),
    State("expiry-dropdown", "value"),
    prevent_initial_call=True
)
def update_iv_charts(n, ticker, expiry):
    try:
        fig_smile = plot_iv_smile(ticker, expiry)
    except Exception:
        fig_smile = go.Figure()
    try:
        fig_surface = plot_iv_surface(ticker)
    except Exception:
        fig_surface = go.Figure()
    return fig_smile, fig_surface


if __name__ == '__main__':
    app.run(debug=True, port=8050)