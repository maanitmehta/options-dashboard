import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.stats import norm
from greeks import compute_greeks

pio.renderers.default = "browser"


def plot_greeks_surface(S=100, r=0.05, sigma=0.20, option_type='call'):
    """
    3D surface plots for all 5 Greeks — fully vectorised, no loops.
    """
    K_range = np.linspace(0.7 * S, 1.3 * S, 25)
    T_range = np.linspace(0.05, 2.0, 25)

    K_grid, T_grid = np.meshgrid(K_range, T_range)

    d1 = (np.log(S / K_grid) + (r + 0.5 * sigma**2) * T_grid) / (sigma * np.sqrt(T_grid))
    d2 = d1 - sigma * np.sqrt(T_grid)
    pdf_d1 = norm.pdf(d1)

    if option_type == 'call':
        delta = norm.cdf(d1)
        rho   = K_grid * T_grid * np.exp(-r * T_grid) * norm.cdf(d2) / 100
    else:
        delta = norm.cdf(d1) - 1
        rho   = -K_grid * T_grid * np.exp(-r * T_grid) * norm.cdf(-d2) / 100

    gamma = pdf_d1 / (S * sigma * np.sqrt(T_grid))
    vega  = S * pdf_d1 * np.sqrt(T_grid) / 100
    theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T_grid)) - r * K_grid * np.exp(-r * T_grid) * norm.cdf(d2)) / 365

    surfaces = {
        'delta': delta, 'gamma': gamma,
        'vega': vega, 'theta': theta, 'rho': rho
    }

    colors = {
        'delta': 'Blues', 'gamma': 'Greens',
        'vega': 'Purples', 'theta': 'Reds', 'rho': 'Oranges'
    }

    figs = {}
    for name, Z in surfaces.items():
        fig = go.Figure(data=[go.Surface(
            x=K_range, y=T_range, z=Z,
            colorscale=colors[name],
            colorbar=dict(title=name.capitalize()),
            hovertemplate=f'Strike: %{{x:.1f}}<br>T: %{{y:.2f}}y<br>{name.capitalize()}: %{{z:.4f}}<extra></extra>'
        )])
        fig.update_layout(
            title=f'{name.capitalize()} Surface — {option_type.capitalize()} | S={S}, σ={sigma}, r={r}',
            scene=dict(
                xaxis_title='Strike (K)',
                yaxis_title='Time to Expiry (years)',
                zaxis_title=name.capitalize(),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8))
            ),
            template='plotly_white',
            height=600
        )
        figs[name] = fig

    return figs


def plot_greeks_2d(S=100, r=0.05, sigma=0.20, option_type='call', T=0.25):
    """
    2D line plots of all Greeks vs strike for a fixed expiry.
    """
    K_range = np.linspace(0.6 * S, 1.4 * S, 100)
    greek_names = ['delta', 'gamma', 'vega', 'theta', 'rho']
    values = {g: [] for g in greek_names}

    for K in K_range:
        g = compute_greeks(S, K, T, r, sigma, option_type)
        for name in greek_names:
            values[name].append(g[name] if g[name] is not None else 0.0)

    colors_2d = {
        'delta': '#2196F3',
        'gamma': '#4CAF50',
        'vega':  '#9C27B0',
        'theta': '#F44336',
        'rho':   '#FF9800'
    }

    fig = go.Figure()
    for name in greek_names:
        fig.add_trace(go.Scatter(
            x=K_range, y=values[name],
            mode='lines', name=name.capitalize(),
            line=dict(color=colors_2d[name], width=2),
            hovertemplate=f'Strike: %{{x:.1f}}<br>{name.capitalize()}: %{{y:.4f}}<extra></extra>'
        ))

    fig.add_vline(
        x=S, line_dash='dash', line_color='gray',
        annotation_text=f'Spot ${S}', annotation_position='top right'
    )

    fig.update_layout(
        title=f'Greeks vs Strike — {option_type.capitalize()} | T={T}y, σ={sigma}, r={r}',
        xaxis_title='Strike (K)',
        yaxis_title='Greek Value',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(x=0.01, y=0.99)
    )

    return fig


if __name__ == '__main__':
    print("Generating 2D Greeks chart...")
    fig_2d = plot_greeks_2d(S=100, r=0.05, sigma=0.20, option_type='call', T=0.25)
    fig_2d.show()

    print("Generating 3D Greeks surfaces...")
    figs_3d = plot_greeks_surface(S=100, r=0.05, sigma=0.20, option_type='call')
    for name, fig in figs_3d.items():
        print(f"  Showing {name}...")
        fig.show() 