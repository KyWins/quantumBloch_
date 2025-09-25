from __future__ import annotations

from typing import List

import numpy as np
import plotly.graph_objects as go


def unit_sphere_mesh(n: int = 32):
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, np.pi, n)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    return x, y, z


def bloch_figure(xs: List[float], ys: List[float], zs: List[float], show_trail: bool = True) -> go.Figure:
    X, Y, Z = unit_sphere_mesh(40)
    fig = go.Figure(data=[
        go.Surface(x=X, y=Y, z=Z, opacity=0.18, showscale=False, colorscale=[[0.0, "#e6f0ff"], [1.0, "#99c2ff"]], hoverinfo="skip"),
        go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode="lines", line=dict(color="#bbb"), hoverinfo="skip"),
        go.Scatter3d(x=[0, 0], y=[-1, 1], z=[0, 0], mode="lines", line=dict(color="#bbb"), hoverinfo="skip"),
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1, 1], mode="lines", line=dict(color="#bbb"), hoverinfo="skip"),
    ])

    if show_trail and len(xs) > 1:
        fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines+markers", line=dict(color="#d62728", width=6), marker=dict(size=3, color="#d62728")))

    if xs and ys and zs:
        fig.add_trace(go.Scatter3d(x=[xs[-1]], y=[ys[-1]], z=[zs[-1]], mode="markers", marker=dict(size=7, color="#111")))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-1.1, 1.1], title="X", gridcolor="#eee"),
            yaxis=dict(range=[-1.1, 1.1], title="Y", gridcolor="#eee"),
            zaxis=dict(range=[-1.1, 1.1], title="Z", gridcolor="#eee"),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )
    return fig
