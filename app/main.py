from __future__ import annotations

from typing import List, Tuple

import streamlit as st

from utils.gate_utils import (
    parse_gate_sequence,
    build_circuit,
    statevector_after,
    state_to_bloch,
    cartesian_to_spherical,
    prepare_initial_state,
)
from utils.plotly_bloch import bloch_figure

st.set_page_config(page_title="Bloch Sphere Visualizer", layout="wide")

st.title("Bloch Sphere Visualizer")

st.markdown(
    "Enter a comma-separated list of gates. Examples: `H`, `X`, `Rx(pi/2)`, `Rz(90deg)`, `H, Rz(π/2), H`."
)

with st.expander("Examples"):
    st.code("H", language="text")
    st.code("H, Rz(pi/2), H", language="text")
    st.code("Rx(pi/2), Ry(pi/3), Rz(-pi/4)", language="text")
    st.caption("Angles accept `pi`, `π`, simple expressions like `pi/2`, and `deg` (e.g., `90deg`).")

preset = st.radio("Initial state preset", ["|0⟩ (default)", "|+⟩", "|i⟩"], horizontal=True, key="preset")


def _initial_preset_key(name: str) -> str:
    if name.startswith("|+⟩"):
        return "|+>"
    if name.startswith("|i⟩"):
        return "|i>"
    return "|0>"


init_key = _initial_preset_key(preset)
user_input = st.text_input("Gate sequence", value="", key="seq")


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

    # Recompute state after each prefix by replaying gates incrementally
    qc_inc = prepare_initial_state(initial)
    for name, ang in gates:
        build_circuit([(name, ang)], base=qc_inc)
        sv = statevector_after(qc_inc)
        coords.append(state_to_bloch(sv))
    return coords


left, right = st.columns([2.5, 1])

with left:
    try:
        coords = trajectory_for(init_key, user_input)
        xs, ys, zs = zip(*coords) if coords else ([], [], [])
        fig = bloch_figure(list(xs), list(ys), list(zs), show_trail=True)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Parsing/Simulation error: {exc}\nTry formats like Rx(pi/2), Rz(90deg), or Ry(-π/3).")

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
        if gates:
            with st.popover("Parsed gates"):
                st.write([f"{n}({ang:.6f})" if ang is not None else n for n, ang in gates])
    except Exception as exc:
        st.error(f"Metric computation error: {exc}")
