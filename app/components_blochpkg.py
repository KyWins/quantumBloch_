from __future__ import annotations

from typing import List, Tuple

try:
    from bloch_sphere import BlochSphere  # type: ignore
except Exception:  # pragma: no cover
    BlochSphere = None  # type: ignore

from app.components import register_visualizer

PathType = List[Tuple[float, float, float]]


def blochpkg_renderer(path_xyz: PathType) -> object:
    if BlochSphere is None:
        raise ImportError("bloch-sphere not installed. Please install 'bloch-sphere' to use this backend.")
    sphere = BlochSphere()
    # The package API may vary; we try to set final state
    if path_xyz:
        x, y, z = path_xyz[-1]
        try:
            sphere.set_state(x, y, z)
        except Exception:
            pass
    return sphere


# Register on import if available
try:  # pragma: no cover
    register_visualizer("bloch-sphere", lambda path: blochpkg_renderer(path))
except Exception:
    pass
