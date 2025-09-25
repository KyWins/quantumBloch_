from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go

# Types
PathType = List[Tuple[float, float, float]]
Renderer = Callable[[PathType], object]


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

def _plotly_renderer(path_xyz: PathType) -> go.Figure:
    u, v = np.mgrid[0 : 2 * np.pi : 60j, 0 : np.pi : 30j]
    xs = np.cos(u) * np.sin(v)
    ys = np.sin(u) * np.sin(v)
    zs = np.cos(v)

    sphere = go.Surface(
        x=xs,
        y=ys,
        z=zs,
        colorscale=[[0.0, "#e6f0ff"], [1.0, "#99c2ff"]],
        opacity=0.28,
        showscale=False,
        hoverinfo="skip",
    )

    axes = _axes_traces()

    traces = [sphere] + axes

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

    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(
            aspectmode="cube",
            xaxis=dict(range=[-1.1, 1.1], title="X", gridcolor="#eee"),
            yaxis=dict(range=[-1.1, 1.1], title="Y", gridcolor="#eee"),
            zaxis=dict(range=[-1.1, 1.1], title="Z", gridcolor="#eee"),
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="Bloch Sphere (Plotly)",
        showlegend=False,
    )
    return fig


def _plotly_anim_renderer(path_xyz: PathType) -> go.Figure:
    # Base sphere and axes
    base = _plotly_renderer([])

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

def make_bloch_figure(path_xyz: PathType, backend: str = "plotly") -> object:
    renderer = get_visualizer(backend)
    return renderer(path_xyz)


# Register built-in Plotly renderer by default
register_visualizer("plotly", _plotly_renderer)
# Register animated variant
register_visualizer("plotly-anim", _plotly_anim_renderer)
