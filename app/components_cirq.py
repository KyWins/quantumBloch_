from __future__ import annotations

from typing import List, Tuple, Optional, Mapping, Any

try:
    from cirq_web import bloch_sphere as cw_bloch  # type: ignore
except Exception:  # pragma: no cover
    cw_bloch = None  # type: ignore

from app.components import register_visualizer

PathType = List[Tuple[float, float, float]]


def cirq_web_renderer(path_xyz: PathType, ctx: Optional[Mapping[str, Any]] = None) -> object:
    if cw_bloch is None:
        raise ImportError("cirq-web not installed. Please install 'cirq-web' to use this backend.")

    widget = cw_bloch.BlochSphere()
    # cirq-web BlochSphere expects a single state; we will set the last state
    if path_xyz:
        x, y, z = path_xyz[-1]
        widget.set_state(x, y, z)
    return widget


# Register on import if available
try:  # pragma: no cover
    register_visualizer("cirq-web", cirq_web_renderer)
except Exception:
    pass




