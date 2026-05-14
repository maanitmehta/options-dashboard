import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import datetime
import pandas as pd

pio.renderers.default = "browser"

from iv_solver import get_iv_smile_data, compute_iv_surface
from data_fetcher import get_available_expiries, get_option_chain, get_spot_price, get_risk_free_rate


def plot_iv_smile(ticker='AAPL', expiry=None):
    df, S, T, r, expiry_used = get_iv_smile_data(ticker, expiry)
    calls = df[df['type'] == 'call']
    puts  = df[df['type'] == 'put']
    calls = calls[(calls['moneyness'] >= 0.7) & (calls['moneyness'] <= 1.3)]
    puts  = puts[(puts['moneyness']  >= 0.7) & (puts['moneyness']  <= 1.3)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=calls['strike'], y=calls['iv'] * 100,
        mode='lines+markers', name='Calls',
        line=dict(color='#2196F3', width=2),
        marker=dict(size=6),
        hovertemplate='Strike: %{x}<br>IV: %{y:.1f}%<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=puts['strike'], y=puts['iv'] * 100,
        mode='lines+markers', name='Puts',
        line=dict(color='#FF5722', width=2),
        marker=dict(size=6),
        hovertemplate='Strike: %{x}<br>IV: %{y:.1f}%<extra></extra>'
    ))
    fig.add_vline(
        x=S, line_dash='dash', line_color='gray',
        annotation_text=f'Spot ${S:.2f}', annotation_position='top right'
    )
    fig.update_layout(
        title=f'{ticker} IV Smile — Expiry {expiry_used}',
        xaxis_title='Strike Price',
        yaxis_title='Implied Volatility (%)',
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    return fig


def plot_iv_surface(ticker='AAPL'):
    expiries = get_available_expiries(ticker)[:6]
    S = get_spot_price(ticker)
    r = get_risk_free_rate()
    all_data = []
    for exp in expiries:
        try:
            calls, puts, _ = get_option_chain(ticker, exp)
            expiry_dt = datetime.datetime.strptime(exp, '%Y-%m-%d')
            T = max((expiry_dt - datetime.datetime.today()).days / 365, 1/365)
            df = compute_iv_surface(calls, puts, S, T, r)
            df['T'] = round(T, 6)
            df['expiry'] = exp
            df['moneyness'] = round(df['strike'] / S, 4)
            all_data.append(df)
        except Exception:
            continue
    combined = pd.concat(all_data, ignore_index=True)
    surface = combined[(combined['type'] == 'call') &
                       (combined['moneyness'] >= 0.8) &
                       (combined['moneyness'] <= 1.2)]
    pivot = surface.pivot_table(index='expiry', columns='strike', values='iv', aggfunc='mean')
    pivot = pivot.dropna(axis=1, thresh=3)
    Z = pivot.values * 100
    X = pivot.columns.values
    Y = list(range(len(pivot.index)))
    fig = go.Figure(data=[go.Surface(
        z=Z, x=X, y=Y,
        colorscale='Viridis',
        colorbar=dict(title='IV %'),
        hovertemplate='Strike: %{x}<br>Expiry idx: %{y}<br>IV: %{z:.1f}%<extra></extra>'
    )])
    fig.update_layout(
        title=f'{ticker} Implied Volatility Surface',
        scene=dict(
            xaxis_title='Strike',
            yaxis_title='Expiry',
            zaxis_title='IV (%)',
            yaxis=dict(tickvals=Y, ticktext=pivot.index.tolist())
        ),
        template='plotly_white',
        height=600
    )
    return fig


if __name__ == '__main__':
    print("Generating IV smile...")
    smile = plot_iv_smile('AAPL')
    smile.show()
    print("Generating IV surface (fetching 6 expiries, takes ~10s)...")
    surface = plot_iv_surface('AAPL')
    surface.show()
