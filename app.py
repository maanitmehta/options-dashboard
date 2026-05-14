import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import datetime
import pandas as pd

from bs_model import black_scholes
from greeks import compute_greeks
from mc_pricer import monte_carlo_price
from greeks_plot import plot_greeks_surface, plot_greeks_2d
from iv_plot import plot_iv_smile, plot_iv_surface
from data_fetcher import get_spot_price, get_risk_free_rate, get_available_expiries, get_atm_iv
from payoff import build_payoff_chart
from mc_plot import plot_mc_paths, plot_mc_convergence

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True)
app.title = "Options Pricing Dashboard"
server = app.server

sidebar = dbc.Card([
    html.H5("Parameters", className="mb-3"),

    dbc.Label("Ticker"),
    dcc.Dropdown(
        id="ticker",
        options=[
            {"label": "AAPL — Apple",           "value": "AAPL"},
            {"label": "MSFT — Microsoft",        "value": "MSFT"},
            {"label": "TSLA — Tesla",            "value": "TSLA"},
            {"label": "NVDA — Nvidia",           "value": "NVDA"},
            {"label": "SPY — S&P 500 ETF",       "value": "SPY"},
            {"label": "AMZN — Amazon",           "value": "AMZN"},
            {"label": "GOOGL — Alphabet",        "value": "GOOGL"},
            {"label": "META — Meta",             "value": "META"},
            {"label": "BRK-B — Berkshire",       "value": "BRK-B"},
            {"label": "JPM — JPMorgan",          "value": "JPM"},
            {"label": "GS — Goldman Sachs",      "value": "GS"},
            {"label": "BAC — Bank of America",   "value": "BAC"},
            {"label": "QQQ — Nasdaq 100 ETF",    "value": "QQQ"},
            {"label": "IWM — Russell 2000 ETF",  "value": "IWM"},
            {"label": "GLD — Gold ETF",          "value": "GLD"},
            {"label": "NFLX — Netflix",          "value": "NFLX"},
            {"label": "AMD — AMD",               "value": "AMD"},
            {"label": "INTC — Intel",            "value": "INTC"},
            {"label": "DIS — Disney",            "value": "DIS"},
            {"label": "UBER — Uber",             "value": "UBER"},
            {"label": "COIN — Coinbase",         "value": "COIN"},
            {"label": "PLTR — Palantir",         "value": "PLTR"},
            {"label": "ARM — ARM Holdings",      "value": "ARM"},
        ],
        value="AAPL",
        searchable=True,
        clearable=False,
        placeholder="Search ticker...",
        className="mb-1"
    ),
    dbc.Input(
        id="custom-ticker",
        placeholder="Or type any ticker e.g. BABA, RIO, VOD...",
        type="text",
        size="sm",
        className="mb-2",
        style={"fontSize": "12px"}
    ),

    dbc.Label("Expiry"),
    dcc.Dropdown(id="expiry-dropdown", placeholder="Load expiries first", className="mb-2"),

    dbc.Button("Load Market Data", id="load-btn", color="primary", className="mb-3 w-100"),

    html.Hr(),

    dbc.Label("Spot Price (S)"),
    dbc.Input(id="spot", type="number", value=100, step=1, className="mb-2"),

    dbc.Label("Strike Price (K)"),
    dbc.Input(id="strike", type="number", value=100, step=1, className="mb-2"),

    html.Div(id="moneyness-label", className="mb-2",
             style={"fontSize": "12px", "color": "gray"}),

    dbc.Label("Time to Expiry (years)"),
    dbc.Input(id="T", type="number", value=0.25, step=0.01, className="mb-2"),

    dbc.Label("Risk-Free Rate"),
    dbc.Input(id="rate", type="number", value=0.05, step=0.001, className="mb-2"),

    dbc.Label("Volatility (σ)"),
    dbc.InputGroup([
        dbc.Input(id="sigma", type="number", value=0.20, step=0.01),
        dbc.Button("Use Market IV", id="btn-market-iv", color="outline-secondary", size="sm"),
    ], className="mb-2"),

    dbc.Label("Option Type"),
    dbc.RadioItems(
        id="option-type",
        options=[{"label": "Call", "value": "call"}, {"label": "Put", "value": "put"}],
        value="call", inline=True, className="mb-3"
    ),

    dbc.Label("Preset Strategies"),
    html.Div([
        dbc.Button("ATM Call",     id="pre-atm-call",    color="outline-primary",   size="sm", className="me-1 mb-1"),
        dbc.Button("ATM Put",      id="pre-atm-put",     color="outline-primary",   size="sm", className="me-1 mb-1"),
        dbc.Button("ATM Straddle", id="pre-straddle",    color="outline-secondary", size="sm", className="me-1 mb-1"),
        dbc.Button("OTM Call",     id="pre-otm-call",    color="outline-success",   size="sm", className="me-1 mb-1"),
        dbc.Button("OTM Put",      id="pre-otm-put",     color="outline-success",   size="sm", className="me-1 mb-1"),
        dbc.Button("Bull Spread",  id="pre-bull-spread", color="outline-warning",   size="sm", className="me-1 mb-1"),
        dbc.Button("Bear Spread",  id="pre-bear-spread", color="outline-danger",    size="sm", className="me-1 mb-1"),
    ], className="mb-3"),

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

    dbc.Button("Price Option",  id="price-btn",      color="success",      className="w-100 mb-2"),
    dbc.Button("Export CSV",    id="btn-export-csv", color="outline-info", className="w-100 mb-2"),
    dbc.Spinner(html.Div(id="loading-output"), color="success", size="sm"),
    html.Div(id="error-msg", style={"color": "red", "fontSize": "12px", "marginTop": "8px"}),

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
    dbc.Row([
        dbc.Col(html.H3("Options Pricing & Greeks Dashboard", className="my-3"), width=10),
        dbc.Col(
            dbc.Switch(id="theme-switch", label="Dark mode", value=False, className="mt-3"),
            width=2, className="text-end"
        ),
    ]),
    dbc.Row([
        dbc.Col(sidebar, width=3),
        dbc.Col([summary_cards, tabs], width=9),
    ]),
    dcc.Download(id="download-csv"),
], fluid=True)


# ── Dark mode ────────────────────────────────────────────────────────────────

app.clientside_callback(
    """
    function(darkMode) {
        const links = document.querySelectorAll('link[rel=stylesheet]');
        links.forEach(link => {
            if (link.href.includes('bootswatch') || link.href.includes('bootstrap')) {
                link.href = darkMode
                    ? 'https://cdn.jsdelivr.net/npm/bootswatch@5/dist/darkly/bootstrap.min.css'
                    : 'https://cdn.jsdelivr.net/npm/bootswatch@5/dist/flatly/bootstrap.min.css';
            }
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output("theme-switch", "id"),
    Input("theme-switch", "value")
)


# ── Custom ticker input ──────────────────────────────────────────────────────

@app.callback(
    Output("ticker", "value", allow_duplicate=True),
    Input("custom-ticker", "value"),
    prevent_initial_call=True
)
def use_custom_ticker(custom):
    if custom and len(custom) >= 1:
        return custom.upper().strip()
    return dash.no_update


# ── Auto load on ticker change ───────────────────────────────────────────────

@app.callback(
    Output("expiry-dropdown", "options", allow_duplicate=True),
    Output("expiry-dropdown", "value",   allow_duplicate=True),
    Output("spot", "value",              allow_duplicate=True),
    Output("rate", "value",              allow_duplicate=True),
    Input("ticker", "value"),
    prevent_initial_call=True
)
def auto_load_on_ticker_change(ticker):
    if not ticker or len(ticker) < 1:
        return [], None, 100, 0.05
    try:
        expiries = get_available_expiries(ticker)
        S = get_spot_price(ticker)
        r = get_risk_free_rate()
        options = [{"label": f"{e} ({(datetime.datetime.strptime(e, '%Y-%m-%d') - datetime.datetime.today()).days}d)", "value": e} for e in expiries[:12]]
        return options, expiries[0], round(S, 2), round(r, 4)
    except Exception:
        return [], None, 100, 0.05


# ── Load market data button ──────────────────────────────────────────────────

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
        options = [{"label": f"{e} ({(datetime.datetime.strptime(e, '%Y-%m-%d') - datetime.datetime.today()).days}d)", "value": e} for e in expiries[:12]]
        return options, expiries[0], round(S, 2), round(r, 4)
    except Exception:
        return [], None, 100, 0.05


# ── Auto ATM strike ──────────────────────────────────────────────────────────

@app.callback(
    Output("strike", "value"),
    Input("spot", "value"),
    prevent_initial_call=True
)
def auto_atm_strike(spot):
    if spot:
        return round(float(spot))
    return 100


# ── Moneyness label ──────────────────────────────────────────────────────────

@app.callback(
    Output("moneyness-label", "children"),
    Input("spot",   "value"),
    Input("strike", "value"),
    prevent_initial_call=True
)
def update_moneyness(spot, strike):
    if not spot or not strike:
        return ""
    ratio = float(strike) / float(spot)
    if ratio < 0.97:
        label = "💰 ITM (In the Money)"
        color = "green"
    elif ratio > 1.03:
        label = "❌ OTM (Out of the Money)"
        color = "red"
    else:
        label = "🎯 ATM (At the Money)"
        color = "orange"
    return html.Span(label, style={"color": color, "fontWeight": "500"})


# ── Update T from expiry ─────────────────────────────────────────────────────

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


# ── Market IV button ─────────────────────────────────────────────────────────

@app.callback(
    Output("sigma", "value"),
    Input("btn-market-iv",   "n_clicks"),
    State("ticker",          "value"),
    State("expiry-dropdown", "value"),
    State("option-type",     "value"),
    prevent_initial_call=True
)
def use_market_iv(n, ticker, expiry, option_type):
    if not ticker or not expiry:
        return 0.20
    try:
        iv = get_atm_iv(ticker, expiry, option_type)
        return iv
    except Exception:
        return 0.20


# ── Preset strategies ────────────────────────────────────────────────────────

@app.callback(
    Output("strike",      "value",  allow_duplicate=True),
    Output("option-type", "value",  allow_duplicate=True),
    Output("strategy",    "value",  allow_duplicate=True),
    Output("T",           "value",  allow_duplicate=True),
    Input("pre-atm-call",    "n_clicks"),
    Input("pre-atm-put",     "n_clicks"),
    Input("pre-straddle",    "n_clicks"),
    Input("pre-otm-call",    "n_clicks"),
    Input("pre-otm-put",     "n_clicks"),
    Input("pre-bull-spread", "n_clicks"),
    Input("pre-bear-spread", "n_clicks"),
    State("spot", "value"),
    prevent_initial_call=True
)
def apply_preset(*args):
    spot = args[-1]
    if not spot:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    S = float(spot)
    atm      = round(S)
    otm_call = round(S * 1.05)
    otm_put  = round(S * 0.95)

    presets = {
        "pre-atm-call":    (atm,      "call", "single",     0.25),
        "pre-atm-put":     (atm,      "put",  "single",     0.25),
        "pre-straddle":    (atm,      "call", "straddle",   0.25),
        "pre-otm-call":    (otm_call, "call", "single",     0.25),
        "pre-otm-put":     (otm_put,  "put",  "single",     0.25),
        "pre-bull-spread": (atm,      "call", "bull_spread", 0.25),
        "pre-bear-spread": (atm,      "put",  "bear_spread", 0.25),
    }

    preset = presets.get(ctx.triggered_id)
    if preset:
        return preset
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# ── Price option ─────────────────────────────────────────────────────────────

@app.callback(
    Output("bs-price",        "children"),
    Output("mc-price",        "children"),
    Output("g-delta",         "children"),
    Output("g-gamma",         "children"),
    Output("g-vega",          "children"),
    Output("g-theta",         "children"),
    Output("payoff-chart",    "figure"),
    Output("greeks-2d-chart", "figure"),
    Output("greeks-3d-chart", "figure"),
    Output("mc-chart",        "figure"),
    Output("mc-paths-chart",  "figure"),
    Output("loading-output",  "children"),
    Output("error-msg",       "children"),
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
    try:
        S, K, T, r, sigma = float(S), float(K), float(T), float(r), float(sigma)

        if T <= 0:
            raise ValueError("Time to expiry must be greater than 0. Please select a future expiry date.")
        if sigma <= 0:
            raise ValueError("Volatility must be greater than 0.")
        if S <= 0 or K <= 0:
            raise ValueError("Spot and strike prices must be greater than 0.")

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
            "",
            "",
        )
    except Exception as e:
        empty = go.Figure()
        return "—", "—", "—", "—", "—", "—", empty, empty, empty, empty, empty, "", str(e)


# ── IV charts ────────────────────────────────────────────────────────────────

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


# ── CSV export ───────────────────────────────────────────────────────────────

@app.callback(
    Output("download-csv", "data"),
    Input("btn-export-csv", "n_clicks"),
    State("spot",        "value"),
    State("strike",      "value"),
    State("T",           "value"),
    State("rate",        "value"),
    State("sigma",       "value"),
    State("option-type", "value"),
    State("ticker",      "value"),
    prevent_initial_call=True
)
def export_csv(n, S, K, T, r, sigma, option_type, ticker):
    S, K, T, r, sigma = float(S), float(K), float(T), float(r), float(sigma)

    bs = black_scholes(S, K, T, r, sigma, option_type)
    mc = monte_carlo_price(S, K, T, r, sigma, option_type)
    gk = compute_greeks(S, K, T, r, sigma, option_type)

    data = {
        "Ticker":      [ticker],
        "Option Type": [option_type],
        "Spot (S)":    [S],
        "Strike (K)":  [K],
        "T (years)":   [T],
        "Rate (r)":    [r],
        "Sigma (σ)":   [sigma],
        "BS Price":    [bs],
        "MC Price":    [mc['price']],
        "MC CI Lower": [mc['ci_lower']],
        "MC CI Upper": [mc['ci_upper']],
        "Delta":       [gk['delta']],
        "Gamma":       [gk['gamma']],
        "Vega":        [gk['vega']],
        "Theta":       [gk['theta']],
        "Rho":         [gk['rho']],
    }

    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, f"{ticker}_option_pricing.csv", index=False)


if __name__ == '__main__':
    app.run(debug=True, port=8050)