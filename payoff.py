import numpy as np
import plotly.graph_objects as go
from bs_model import black_scholes


def single_leg(S, K, T, r, sigma, option_type, position='long'):
    """P&L for a single option leg at expiry."""
    premium = black_scholes(S, K, T, r, sigma, option_type)
    S_range = np.linspace(0.5 * S, 1.5 * S, 300)

    if option_type == 'call':
        payoff = np.maximum(S_range - K, 0)
    else:
        payoff = np.maximum(K - S_range, 0)

    if position == 'long':
        pnl = payoff - premium
    else:
        pnl = premium - payoff

    return S_range, pnl, premium


def straddle(S, K, T, r, sigma):
    """Long call + long put at same strike."""
    call_premium = black_scholes(S, K, T, r, sigma, 'call')
    put_premium  = black_scholes(S, K, T, r, sigma, 'put')
    S_range = np.linspace(0.5 * S, 1.5 * S, 300)

    call_payoff = np.maximum(S_range - K, 0)
    put_payoff  = np.maximum(K - S_range, 0)
    pnl = (call_payoff + put_payoff) - (call_premium + put_premium)

    return S_range, pnl, call_premium + put_premium


def strangle(S, K_call, K_put, T, r, sigma):
    """Long OTM call + long OTM put at different strikes."""
    call_premium = black_scholes(S, K_call, T, r, sigma, 'call')
    put_premium  = black_scholes(S, K_put,  T, r, sigma, 'put')
    S_range = np.linspace(0.5 * S, 1.5 * S, 300)

    call_payoff = np.maximum(S_range - K_call, 0)
    put_payoff  = np.maximum(K_put - S_range,  0)
    pnl = (call_payoff + put_payoff) - (call_premium + put_premium)

    return S_range, pnl, call_premium + put_premium


def bull_call_spread(S, K_low, K_high, T, r, sigma):
    """Buy call at K_low, sell call at K_high."""
    buy_premium  = black_scholes(S, K_low,  T, r, sigma, 'call')
    sell_premium = black_scholes(S, K_high, T, r, sigma, 'call')
    S_range = np.linspace(0.5 * S, 1.5 * S, 300)

    buy_payoff  = np.maximum(S_range - K_low,  0)
    sell_payoff = np.maximum(S_range - K_high, 0)
    pnl = (buy_payoff - sell_payoff) - (buy_premium - sell_premium)

    return S_range, pnl, buy_premium - sell_premium


def bear_put_spread(S, K_high, K_low, T, r, sigma):
    """Buy put at K_high, sell put at K_low."""
    buy_premium  = black_scholes(S, K_high, T, r, sigma, 'put')
    sell_premium = black_scholes(S, K_low,  T, r, sigma, 'put')
    S_range = np.linspace(0.5 * S, 1.5 * S, 300)

    buy_payoff  = np.maximum(K_high - S_range, 0)
    sell_payoff = np.maximum(K_low  - S_range, 0)
    pnl = (buy_payoff - sell_payoff) - (buy_premium - sell_premium)

    return S_range, pnl, buy_premium - sell_premium


def build_payoff_chart(S, K, T, r, sigma, option_type, strategy='single'):
    """Build the full payoff chart for a given strategy."""
    fig = go.Figure()

    if strategy == 'single':
        S_range, pnl, premium = single_leg(S, K, T, r, sigma, option_type)
        label = f'Long {option_type.capitalize()} (K={K})'
        color = '#2196F3'

    elif strategy == 'straddle':
        S_range, pnl, premium = straddle(S, K, T, r, sigma)
        label = f'Straddle (K={K})'
        color = '#9C27B0'

    elif strategy == 'strangle':
        K_call = round(K * 1.05)
        K_put  = round(K * 0.95)
        S_range, pnl, premium = strangle(S, K_call, K_put, T, r, sigma)
        label = f'Strangle (K_call={K_call}, K_put={K_put})'
        color = '#FF9800'

    elif strategy == 'bull_spread':
        K_high = round(K * 1.05)
        S_range, pnl, premium = bull_call_spread(S, K, K_high, T, r, sigma)
        label = f'Bull Call Spread (K={K}/{K_high})'
        color = '#4CAF50'

    elif strategy == 'bear_spread':
        K_low = round(K * 0.95)
        S_range, pnl, premium = bear_put_spread(S, K, K_low, T, r, sigma)
        label = f'Bear Put Spread (K={K}/{K_low})'
        color = '#F44336'

    # Fill green above zero, red below
    fig.add_trace(go.Scatter(
        x=S_range, y=np.where(pnl >= 0, pnl, 0),
        fill='tozeroy', mode='none',
        fillcolor='rgba(76,175,80,0.2)', name='Profit zone'
    ))
    fig.add_trace(go.Scatter(
        x=S_range, y=np.where(pnl < 0, pnl, 0),
        fill='tozeroy', mode='none',
        fillcolor='rgba(244,67,54,0.2)', name='Loss zone'
    ))
    fig.add_trace(go.Scatter(
        x=S_range, y=pnl, mode='lines',
        line=dict(color=color, width=2.5), name=label,
        hovertemplate='Spot: $%{x:.1f}<br>P&L: $%{y:.2f}<extra></extra>'
    ))

    fig.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)
    fig.add_vline(x=S, line_dash='dot', line_color='green',
                  annotation_text=f'Spot ${S:.0f}', annotation_position='top left')
    fig.add_vline(x=K, line_dash='dot', line_color='red',
                  annotation_text=f'Strike ${K:.0f}', annotation_position='top right')

    max_profit = round(float(np.max(pnl)), 2)
    max_loss   = round(float(np.min(pnl)), 2)

    fig.update_layout(
        title=f'{label} — Premium: ${round(premium,2)} | Max profit: ${max_profit} | Max loss: ${max_loss}',
        xaxis_title='Spot Price at Expiry',
        yaxis_title='P&L ($)',
        template='plotly_white',
        height=450,
        legend=dict(x=0.01, y=0.99)
    )

    return fig
