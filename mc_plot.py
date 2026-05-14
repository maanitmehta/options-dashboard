import numpy as np
import plotly.graph_objects as go
from mc_pricer import monte_carlo_price
from bs_model import black_scholes


def plot_mc_paths(S, K, T, r, sigma, option_type='call', n_paths=50, n_steps=100):
    rng = np.random.default_rng(42)
    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)
    fig = go.Figure()
    for i in range(n_paths):
        Z = rng.standard_normal(n_steps)
        path = np.zeros(n_steps + 1)
        path[0] = S
        for j in range(1, n_steps + 1):
            path[j] = path[j-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[j-1])
        color = 'rgba(33,150,243,0.3)' if path[-1] >= K else 'rgba(244,67,54,0.3)'
        fig.add_trace(go.Scatter(
            x=t, y=path, mode='lines',
            line=dict(width=0.8, color=color),
            showlegend=False, hoverinfo='skip'
        ))
    fig.add_hline(y=K, line_dash='dash', line_color='gray',
                  annotation_text=f'Strike ${K}', annotation_position='right')
    fig.add_hline(y=S, line_dash='dot', line_color='green',
                  annotation_text=f'Spot ${S}', annotation_position='left')
    fig.update_layout(
        title=f'{n_paths} Simulated GBM Paths — Blue = ITM, Red = OTM',
        xaxis_title='Time (years)', yaxis_title='Stock Price ($)',
        template='plotly_white', height=450
    )
    return fig


def plot_mc_convergence(S, K, T, r, sigma, option_type='call', max_sims=20000):
    rng = np.random.default_rng(42)
    Z = rng.standard_normal(max_sims)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    if option_type == 'call':
        payoffs = np.maximum(S_T - K, 0)
    else:
        payoffs = np.maximum(K - S_T, 0)
    discount = np.exp(-r * T)
    n = np.arange(1, max_sims + 1)
    running_mean = discount * np.cumsum(payoffs) / n
    n_sampled = np.arange(1, max_sims + 1, 100)
    mean_sampled = running_mean[::100]
    running_std = np.array([np.std(payoffs[:i]) for i in n_sampled])
    ci_upper = mean_sampled + 1.96 * discount * running_std / np.sqrt(n_sampled)
    ci_lower = mean_sampled - 1.96 * discount * running_std / np.sqrt(n_sampled)
    bs_price = black_scholes(S, K, T, r, sigma, option_type)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.concatenate([n_sampled, n_sampled[::-1]]),
        y=np.concatenate([ci_upper, ci_lower[::-1]]),
        fill='toself', fillcolor='rgba(156,39,176,0.1)',
        line=dict(color='rgba(0,0,0,0)'),
        name='95% CI', hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=n_sampled, y=mean_sampled,
        mode='lines', name='MC price',
        line=dict(color='#9C27B0', width=2),
        hovertemplate='N: %{x}<br>Price: $%{y:.4f}<extra></extra>'
    ))
    fig.add_hline(y=bs_price, line_dash='dash', line_color='#F44336',
                  annotation_text=f'BS Price ${bs_price}',
                  annotation_position='bottom right')
    fig.update_layout(
        title=f'MC Convergence — {option_type.capitalize()} | BS=${bs_price}',
        xaxis_title='Number of Simulations', yaxis_title='Option Price ($)',
        template='plotly_white', height=450,
        legend=dict(x=0.01, y=0.99)
    )
    return fig
