from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

import numpy as np
import plotly.graph_objects as go

# Types
PathType = List[Tuple[float, float, float]]
RenderContext = Mapping[str, Any]
Renderer = Callable[[PathType, Optional[RenderContext]], object]


# Registry for visualization backends
_VISUALIZERS: Dict[str, Renderer] = {}


def register_visualizer(name: str, renderer: Renderer) -> None:
    _VISUALIZERS[name] = renderer


def list_visualizers() -> List[str]:
    return list(_VISUALIZERS.keys())


def get_visualizer(name: str) -> Renderer:
    if name not in _VISUALIZERS:
        raise KeyError(f"Visualizer '{name}' not registered")
    return _VISUALIZERS[name]


# Default Plotly implementation

def _plotly_renderer(path_xyz: PathType, ctx: Optional[RenderContext] = None) -> go.Figure:
    u, v = np.mgrid[0 : 2 * np.pi : 60j, 0 : np.pi : 30j]
    xs = np.cos(u) * np.sin(v)
    ys = np.sin(u) * np.sin(v)
    zs = np.cos(v)

    sphere = go.Surface(
        x=xs,
        y=ys,
        z=zs,
        colorscale=[[0.0, "#eff4ff"], [1.0, "#b1c8ff"]],
        opacity=0.32,
        showscale=False,
        hoverinfo="skip",
    )

    axes = _axes_traces()

    traces = [sphere] + axes

    overlay = ctx.get("overlay_point") if ctx else None
    selected_index = ctx.get("selected_index") if ctx else None
    selected_point = ctx.get("selected_point") if ctx else None
    selected_theta = ctx.get("selected_theta") if ctx else None
    selected_phi = ctx.get("selected_phi") if ctx else None

    equator_phi = np.linspace(0, 2 * np.pi, 200)
    traces.append(
        go.Scatter3d(
            x=np.cos(equator_phi),
            y=np.sin(equator_phi),
            z=np.zeros_like(equator_phi),
            mode="lines",
            line=dict(color="#d0d8ff", width=1.5, dash="dot"),
            name="equator",
            hoverinfo="skip",
            showlegend=False,
        )
    )

    if path_xyz:
        xs, ys, zs = zip(*path_xyz)
        traces.append(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="lines+markers",
                line=dict(color="#d62728", width=6),
                marker=dict(size=3, color="#d62728"),
                name="trajectory",
            )
        )
        traces.append(
            go.Scatter3d(
                x=[xs[-1]],
                y=[ys[-1]],
                z=[zs[-1]],
                mode="markers",
                marker=dict(size=7, color="#111"),
                name="final",
            )
        )

        if selected_index is not None:
            clamp = max(0, min(len(path_xyz) - 1, int(selected_index)))
            sel_x, sel_y, sel_z = path_xyz[clamp]
            if selected_point is None:
                selected_point = (sel_x, sel_y, sel_z)
            traces.append(
                go.Scatter3d(
                    x=[sel_x],
                    y=[sel_y],
                    z=[sel_z],
                    mode="markers+text",
                    marker=dict(size=10, color="#1f77b4"),
                    text=["Selected"],
                    textposition="top center",
                    name="selected",
                )
            )

    if selected_point and selected_theta is not None and selected_phi is not None:
        theta_vals = np.linspace(0.0, float(selected_theta), 60)
        meridian_x = np.sin(theta_vals) * np.cos(float(selected_phi))
        meridian_y = np.sin(theta_vals) * np.sin(float(selected_phi))
        meridian_z = np.cos(theta_vals)
        traces.append(
            go.Scatter3d(
                x=meridian_x,
                y=meridian_y,
                z=meridian_z,
                mode="lines",
                line=dict(color="#ff7c43", width=3),
                name="θ arc",
                hoverinfo="skip",
                showlegend=False,
            )
        )

        phi_vals = np.linspace(0.0, float(selected_phi), 60)
        radius = np.sin(float(selected_theta))
        equator_arc_x = radius * np.cos(phi_vals)
        equator_arc_y = radius * np.sin(phi_vals)
        equator_arc_z = np.zeros_like(equator_arc_x)
        traces.append(
            go.Scatter3d(
                x=equator_arc_x,
                y=equator_arc_y,
                z=equator_arc_z,
                mode="lines",
                line=dict(color="#ffa600", width=3),
                name="φ arc",
                hoverinfo="skip",
                showlegend=False,
            )
        )

        proj_x = radius * np.cos(float(selected_phi))
        proj_y = radius * np.sin(float(selected_phi))
        proj_z = 0.0
        traces.append(
            go.Scatter3d(
                x=[proj_x, selected_point[0]],
                y=[proj_y, selected_point[1]],
                z=[proj_z, selected_point[2]],
                mode="lines",
                line=dict(color="#94caf9", width=2, dash="dash"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    if overlay:
        ox, oy, oz = overlay
        traces.append(
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

    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(
            aspectmode="cube",
            xaxis=dict(
                range=[-1.1, 1.1],
                title="X",
                gridcolor="#dfe4ff",
                showbackground=True,
                backgroundcolor="#ffffff",
                zerolinecolor="#9fb0ff",
                title_font=dict(color="#4a5568"),
                tickfont=dict(color="#4a5568"),
            ),
            yaxis=dict(
                range=[-1.1, 1.1],
                title="Y",
                gridcolor="#dfe4ff",
                showbackground=True,
                backgroundcolor="#ffffff",
                zerolinecolor="#9fb0ff",
                title_font=dict(color="#4a5568"),
                tickfont=dict(color="#4a5568"),
            ),
            zaxis=dict(
                range=[-1.1, 1.1],
                title="Z",
                gridcolor="#dfe4ff",
                showbackground=True,
                backgroundcolor="#ffffff",
                zerolinecolor="#9fb0ff",
                title_font=dict(color="#4a5568"),
                tickfont=dict(color="#4a5568"),
            ),
            bgcolor="#f4f6ff",
            camera=dict(eye=dict(x=1.6, y=1.3, z=1.2)),
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="Bloch Sphere (Plotly)",
        showlegend=False,
    )
    return fig


def _plotly_anim_renderer(path_xyz: PathType, ctx: Optional[RenderContext] = None) -> go.Figure:
    # Base sphere and axes
    base = _plotly_renderer([], ctx)

    frames = []
    if path_xyz:
        xs, ys, zs = zip(*path_xyz)
        for i in range(1, len(xs) + 1):
            frame_traces = [
                go.Scatter3d(
                    x=xs[:i], y=ys[:i], z=zs[:i],
                    mode="lines+markers",
                    line=dict(color="#d62728", width=6),
                    marker=dict(size=3, color="#d62728"),
                    name="trajectory",
                ),
                go.Scatter3d(
                    x=[xs[i-1]], y=[ys[i-1]], z=[zs[i-1]],
                    mode="markers",
                    marker=dict(size=7, color="#111"),
                    name="current",
                ),
            ]
            frames.append(go.Frame(data=frame_traces, name=str(i)))

        # Add an initial empty trajectory trace so the play button has targets
        base.add_trace(
            go.Scatter3d(x=[], y=[], z=[], mode="lines+markers", line=dict(color="#d62728", width=6), marker=dict(size=3))
        )
        base.add_trace(
            go.Scatter3d(x=[], y=[], z=[], mode="markers", marker=dict(size=7, color="#111"))
        )

    base.update(frames=frames)
    if path_xyz and ctx and "selected_index" in ctx:
        idx = max(0, min(len(path_xyz) - 1, int(ctx["selected_index"])))
        xs, ys, zs = zip(*path_xyz)
        line_idx = len(base.data) - 2
        point_idx = len(base.data) - 1
        base.data[line_idx].x = xs[: idx + 1]
        base.data[line_idx].y = ys[: idx + 1]
        base.data[line_idx].z = zs[: idx + 1]
        base.data[point_idx].x = [xs[idx]]
        base.data[point_idx].y = [ys[idx]]
        base.data[point_idx].z = [zs[idx]]

    base.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[[str(i + 1) for i in range(len(frames))], {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    ),
                    dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
                ],
                x=0.05,
                y=0.02,
                xanchor="left",
                yanchor="bottom",
            )
        ]
    )
    return base


def _axes_traces() -> list:
    ticks = [
        (1, 0, 0, "|+⟩"),
        (-1, 0, 0, "|−⟩"),
        (0, 1, 0, "+i"),
        (0, -1, 0, "−i"),
        (0, 0, 1, "|0⟩"),
        (0, 0, -1, "|1⟩"),
    ]

    traces = []
    traces.append(go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode="lines", line=dict(color="#bbb"), hoverinfo="skip"))
    traces.append(go.Scatter3d(x=[0, 0], y=[-1, 1], z=[0, 0], mode="lines", line=dict(color="#bbb"), hoverinfo="skip"))
    traces.append(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1, 1], mode="lines", line=dict(color="#bbb"), hoverinfo="skip"))

    for x, y, z, label in ticks:
        traces.append(
            go.Scatter3d(
                x=[x], y=[y], z=[z], mode="markers+text", text=[label], textposition="top center", marker=dict(size=2), hoverinfo="skip"
            )
        )
    return traces


# Public API used by app

def make_bloch_figure(path_xyz: PathType, backend: str = "plotly", context: Optional[RenderContext] = None) -> object:
    renderer = get_visualizer(backend)
    return renderer(path_xyz, context)


# Register built-in Plotly renderer by default
register_visualizer("plotly", _plotly_renderer)
# Register animated variant
register_visualizer("plotly-anim", _plotly_anim_renderer)
