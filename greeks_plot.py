import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from greeks import compute_greeks

pio.renderers.default = "browser"

def plot_greeks_surface(S=100, r=0.05, sigma=0.20, option_type='call'):
    """
    3D surface plots for all 5 Greeks across strike and time-to-expiry.
    """
    K_range = np.linspace(0.7 * S, 1.3 * S, 50)
    T_range = np.linspace(0.01, 2.0, 50)

    K_grid, T_grid = np.meshgrid(K_range, T_range)

    greek_names = ['delta', 'gamma', 'vega', 'theta', 'rho']
    surfaces = {g: np.zeros_like(K_grid) for g in greek_names}

    for i in range(T_grid.shape[0]):
        for j in range(K_grid.shape[1]):
            g = compute_greeks(S, K_grid[i,j], T_grid[i,j], r, sigma, option_type)
            for name in greek_names:
                surfaces[name][i,j] = g[name] if g[name] is not None else 0.0

    colors = {
        'delta': 'Blues',
        'gamma': 'Greens',
        'vega':  'Purples',
        'theta': 'Reds',
        'rho':   'Oranges'
    }

    figs = {}
    for name in greek_names:
        fig = go.Figure(data=[go.Surface(
            x=K_range,
            y=T_range,
            z=surfaces[name],
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

    print("Generating 3D Greeks surfaces (5 plots, takes ~5s)...")
    figs_3d = plot_greeks_surface(S=100, r=0.05, sigma=0.20, option_type='call')
    for name, fig in figs_3d.items():
        print(f"  Showing {name}...")
        fig.show()
