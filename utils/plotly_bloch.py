from __future__ import annotations

from typing import List, Optional, Tuple

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


def bloch_figure(
    xs: List[float],
    ys: List[float],
    zs: List[float],
    show_trail: bool = True,
    highlight_point: Optional[Tuple[float, float, float]] = None,
    overlay_point: Optional[Tuple[float, float, float]] = None,
    selected_theta: Optional[float] = None,
    selected_phi: Optional[float] = None,
) -> go.Figure:
    X, Y, Z = unit_sphere_mesh()
    fig = go.Figure()
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, opacity=0.16, showscale=False))
    fig.add_trace(go.Scatter3d(x=[0, 1], y=[0, 0], z=[0, 0], mode="lines", name="X"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 1], z=[0, 0], mode="lines", name="Y"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], mode="lines", name="Z"))

    equator_phi = np.linspace(0, 2 * np.pi, 200)
    fig.add_trace(
        go.Scatter3d(
            x=np.cos(equator_phi),
            y=np.sin(equator_phi),
            z=np.zeros_like(equator_phi),
            mode="lines",
            line=dict(color="#d0d8ff", width=1.5, dash="dot"),
            name="equator",
            hoverinfo="skip",
        )
    )

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

    if highlight_point is not None:
        hx, hy, hz = highlight_point
        if selected_theta is not None and selected_phi is not None:
            theta_vals = np.linspace(0.0, selected_theta, 60)
            meridian_x = np.sin(theta_vals) * np.cos(selected_phi)
            meridian_y = np.sin(theta_vals) * np.sin(selected_phi)
            meridian_z = np.cos(theta_vals)
            fig.add_trace(
                go.Scatter3d(
                    x=meridian_x,
                    y=meridian_y,
                    z=meridian_z,
                    mode="lines",
                    line=dict(color="#ff7c43", width=3),
                    name="θ arc",
                    hoverinfo="skip",
                )
            )

            phi_vals = np.linspace(0.0, selected_phi, 60)
            radius = np.sin(selected_theta)
            equator_arc_x = radius * np.cos(phi_vals)
            equator_arc_y = radius * np.sin(phi_vals)
            equator_arc_z = np.zeros_like(equator_arc_x)
            fig.add_trace(
                go.Scatter3d(
                    x=equator_arc_x,
                    y=equator_arc_y,
                    z=equator_arc_z,
                    mode="lines",
                    line=dict(color="#ffa600", width=3),
                    name="φ arc",
                    hoverinfo="skip",
                )
            )

            proj_x = radius * np.cos(selected_phi)
            proj_y = radius * np.sin(selected_phi)
            proj_z = 0.0
            fig.add_trace(
                go.Scatter3d(
                    x=[proj_x, hx],
                    y=[proj_y, hy],
                    z=[proj_z, hz],
                    mode="lines",
                    line=dict(color="#94caf9", width=2, dash="dash"),
                    name="elevation",
                    hoverinfo="skip",
                )
            )

        fig.add_trace(
            go.Scatter3d(
                x=[hx],
                y=[hy],
                z=[hz],
                mode="markers+text",
                marker=dict(size=10, color="#1f77b4"),
                text=["Selected"],
                textposition="top center",
                name="selected",
            )
        )

    if overlay_point is not None:
        ox, oy, oz = overlay_point
        fig.add_trace(
            go.Scatter3d(
                x=[ox],
                y=[oy],
                z=[oz],
                mode="markers+text",
                marker=dict(size=11, color="#2ca02c"),
                text=["Measured"],
                textposition="bottom center",
                name="measured",
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

    axis_style = dict(
        range=[-1, 1],
        showbackground=True,
        backgroundcolor="#ffffff",
        gridcolor="#dfe4ff",
        zerolinecolor="#9fb0ff",
        title_font=dict(color="#4a5568"),
        tickfont=dict(color="#4a5568"),
    )
    fig.update_layout(
        scene=dict(
            bgcolor="#f4f6ff",
            xaxis=dict(title="X", **axis_style),
            yaxis=dict(title="Y", **axis_style),
            zaxis=dict(title="Z", **axis_style),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.6, y=1.3, z=1.2)),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        uirevision="bloch",
    )

    if st.button("Reset view", use_container_width=True):
        fig.update_layout(scene_camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)))

    return fig
