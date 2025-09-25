from __future__ import annotations

from typing import List, Tuple

import streamlit as st
import random

from utils.gate_utils import (
    parse_gate_sequence,
    build_circuit,
    statevector_after,
    state_to_bloch,
    cartesian_to_spherical,
    prepare_initial_state,
)
from utils.plotly_bloch import bloch_figure

# Prefer pluggable visualizers; fall back if registry not importable
try:
    from app.components import list_visualizers, make_bloch_figure
except Exception:
    try:
        from components import list_visualizers, make_bloch_figure
    except Exception:
        list_visualizers = lambda: ["plotly", "plotly-anim"]  # type: ignore
        make_bloch_figure = None  # type: ignore

st.set_page_config(page_title="Bloch Sphere Visualizer", layout="wide", initial_sidebar_state="collapsed")

st.title("Bloch Sphere Visualizer")

st.markdown("Enter a comma-separated list of gates. Examples: `H`, `X`, `Rx(pi/2)`, `Rz(90deg)`, `H, Rz(π/2), H`.")

with st.expander("Examples"):
    st.code("H", language="text")
    st.code("H, Rz(pi/2), H", language="text")
    st.code("Rx(pi/2), Ry(pi/3), Rz(-pi/4)", language="text")
    st.caption("Angles accept `pi`, `π`, simple expressions like `pi/2`, and `deg` (e.g., `90deg`).")

# Shareable URL hydration (handle values as strings or lists)
qp = st.query_params

def _qp_get(key: str, default: str) -> str:
    try:
        val = qp.get(key, default)
    except Exception:
        return default
    if isinstance(val, list):
        return val[0] if val else default
    if isinstance(val, str):
        return val if val != "" else default
    return default

qp_preset = _qp_get("preset", "|0⟩")
qp_seq = _qp_get("seq", "")

preset = st.radio(
    "Initial state preset",
    ["|0⟩ (default)", "|+⟩", "|i⟩"],
    horizontal=True,
    key="preset",
    index={"|0⟩": 0, "|+⟩": 1, "|i⟩": 2}.get(qp_preset, 0),
)


def _initial_preset_key(name: str) -> str:
    if name.startswith("|+⟩"):
        return "|+>"
    if name.startswith("|i⟩"):
        return "|i>"
    return "|0>"


init_key = _initial_preset_key(preset)
user_input = st.text_input("Gate sequence", value=qp_seq, key="seq", placeholder="e.g., H, Rz(pi/2), H")

# Persist to URL so users can share the exact setup
try:
    st.query_params.update({"preset": preset.split(" ")[0], "seq": user_input})
except Exception:
    pass

# Backend selector
try:
    backends = list_visualizers()
except Exception:
    backends = ["plotly", "plotly-anim"]
backend = st.selectbox("Visualization backend", options=backends, index=0, help="Choose a rendering engine")


@st.cache_data(show_spinner=False)
def trajectory_for(initial: str, seq_text: str) -> List[Tuple[float, float, float]]:
    """Return Bloch (x,y,z) points including initial state, then after each gate."""
    qc = prepare_initial_state(initial)
    coords: List[Tuple[float, float, float]] = []
    # initial point
    sv0 = statevector_after(qc)
    coords.append(state_to_bloch(sv0))

    gates = parse_gate_sequence(seq_text) if seq_text.strip() else []
    if not gates:
        return coords

    # Replay gates incrementally
    qc_inc = prepare_initial_state(initial)
    for name, ang in gates:
        build_circuit([(name, ang)], base=qc_inc)
        sv = statevector_after(qc_inc)
        coords.append(state_to_bloch(sv))
    return coords


# Three-column layout: Sphere (L), Controls (M), Metrics (R)
left, mid, right = st.columns([2.0, 1.2, 1.2], vertical_alignment="top")

with left:
    try:
        coords = trajectory_for(init_key, user_input)
        # Use pluggable visualizer if available; fallback to plotly helper
        try:
            if make_bloch_figure is not None:
                rendered = make_bloch_figure(coords, backend=backend)
                if hasattr(rendered, "to_plotly_json") or hasattr(rendered, "to_dict"):
                    st.plotly_chart(rendered, use_container_width=True)
                else:
                    st.write(rendered)
            else:
                raise RuntimeError("Visualizer registry unavailable")
        except Exception as be:
            xs, ys, zs = zip(*coords) if coords else ([], [], [])
            fig = bloch_figure(list(xs), list(ys), list(zs), show_trail=True)
            st.info(f"Backend '{backend}' unavailable, falling back to Plotly. ({be})")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Parsing/Simulation error: {exc}\nTry formats like Rx(pi/2), Rz(90deg), or Ry(-π/3).")

with mid:
    st.subheader("Controls")
    st.caption("Apply a measurement to show single-shot collapse.")
    try:
        if st.button("Measure once (simulate 1 shot)", use_container_width=True):
            qc_m = prepare_initial_state(init_key)
            gates = parse_gate_sequence(user_input) if user_input.strip() else []
            if gates:
                build_circuit(gates, base=qc_m)
            sv = statevector_after(qc_m)
            p0 = abs(sv.data[0]) ** 2
            collapsed = (0.0, 0.0, 1.0) if random.random() < p0 else (0.0, 0.0, -1.0)
            st.session_state["overlay_point"] = collapsed
            st.toast(f"Measured {'|0⟩' if collapsed[2] > 0 else '|1⟩'}", icon="✅")
    except Exception as exc:
        st.error(f"Measurement error: {exc}")

with right:
    st.subheader("Final State Metrics")
    try:
        qc = prepare_initial_state(init_key)
        gates = parse_gate_sequence(user_input) if user_input.strip() else []
        if gates:
            build_circuit(gates, base=qc)
        sv = statevector_after(qc)
        x, y, z = state_to_bloch(sv)
        theta, phi = cartesian_to_spherical(x, y, z)
        st.metric("x", f"{x:.3f}")
        st.metric("y", f"{y:.3f}")
        st.metric("z", f"{z:.3f}")
        st.metric("θ (polar)", f"{theta:.3f} rad")
        st.metric("φ (azimuth)", f"{phi:.3f} rad")
        st.caption("θ = arccos(z), φ = atan2(y, x)")
        try:
            amp0 = abs(sv.data[0]) ** 2
            amp1 = abs(sv.data[1]) ** 2
            st.metric("|0⟩ probability", f"{amp0:.3f}")
            st.metric("|1⟩ probability", f"{amp1:.3f}")
        except Exception:
            pass
        if gates:
            with st.popover("Parsed gates (normalized)"):
                st.write([f"{n}({ang:.6f})" if ang is not None else n for n, ang in gates])
    except Exception as exc:
        st.error(f"Metric computation error: {exc}")
