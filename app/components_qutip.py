from __future__ import annotations

from typing import List, Tuple, Optional

try:
    import qutip as qt  # type: ignore
except Exception:  # pragma: no cover
    qt = None  # type: ignore

from app.components import register_visualizer

PathType = List[Tuple[float, float, float]]


def qutip_bloch_renderer(path_xyz: PathType, save_path: Optional[str] = None) -> object:
    if qt is None:
        raise ImportError("QuTiP not installed. Please install 'qutip' to use this backend.")

    b = qt.Bloch()
    b.xlabel = ["X", ""]
    b.ylabel = ["Y", ""]
    b.zlabel = ["Z", ""]

    if path_xyz:
        xs, ys, zs = zip(*path_xyz)
        b.add_points([xs, ys, zs], meth="l")
        b.add_points([[xs[-1]], [ys[-1]], [zs[-1]]], meth="p")

    if save_path:
        b.save(save_path)
    else:
        # Return a matplotlib figure for display in notebooks/Streamlit (static image)
        b.render()
    return b.fig


# Register on import if available
try:  # pragma: no cover
    register_visualizer("qutip", lambda path: qutip_bloch_renderer(path))
except Exception:
    pass
