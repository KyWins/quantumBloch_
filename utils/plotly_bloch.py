from __future__ import annotations

from typing import List

import numpy as np
import plotly.graph_objects as go
import streamlit as st


def unit_sphere_mesh(n: int = 48):
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, np.pi, n)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    return x, y, z


def bloch_figure(xs: List[float], ys: List[float], zs: List[float], show_trail: bool = True) -> go.Figure:
    X, Y, Z = unit_sphere_mesh()
    fig = go.Figure()
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, opacity=0.16, showscale=False))
    fig.add_trace(go.Scatter3d(x=[0, 1], y=[0, 0], z=[0, 0], mode="lines", name="X"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 1], z=[0, 0], mode="lines", name="Y"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], mode="lines", name="Z"))

    if show_trail and len(xs) > 1:
        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="lines+markers",
                line=dict(width=6, color="#d62728"),
                marker=dict(size=3, opacity=0.65, color="#d62728"),
            )
        )

    if xs and ys and zs:
        fig.add_trace(
            go.Scatter3d(
                x=[xs[-1]],
                y=[ys[-1]],
                z=[zs[-1]],
                mode="markers+text",
                marker=dict(size=9, color="#111"),
                text=["Final"],
                textposition="top center",
                name="final",
            )
        )

    labels = [
        (0, 0, 1, "|0⟩"),
        (0, 0, -1, "|1⟩"),
        (1, 0, 0, "|+⟩"),
        (-1, 0, 0, "|−⟩"),
        (0, 1, 0, "|+i⟩"),
        (0, -1, 0, "|−i⟩"),
    ]
    for x, y, z, t in labels:
        fig.add_trace(
            go.Scatter3d(x=[x], y=[y], z=[z], mode="text", text=[t], showlegend=False)
        )

    try:
        collapsed = st.session_state.get("overlay_point")
        if collapsed:
            cx, cy, cz = collapsed
            fig.add_trace(
                go.Scatter3d(
                    x=[cx],
                    y=[cy],
                    z=[cz],
                    mode="markers+text",
                    marker=dict(size=10, color="#111"),
                    text=["Measured"],
                    textposition="bottom center",
                    name="measured",
                )
            )
    except Exception:
        pass

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-1, 1]),
            yaxis=dict(range=[-1, 1]),
            zaxis=dict(range=[-1, 1]),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        uirevision="bloch",
    )

    if st.button("Reset view", use_container_width=True):
        fig.update_layout(scene_camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)))

    return fig
