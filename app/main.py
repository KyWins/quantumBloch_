from __future__ import annotations

from typing import List, Tuple

import streamlit as st
from qiskit import QuantumCircuit
import numpy as np

from utils.gate_utils import (
    apply_gates,
    parse_gate_sequence,
    build_circuit,
    statevector_after,
    state_to_bloch,
    cartesian_to_spherical,
)
from utils.plotly_bloch import bloch_figure
from app.components import make_bloch_figure

st.set_page_config(page_title="Bloch Sphere Visualizer", layout="wide")

st.title("Bloch Sphere Visualizer")

st.markdown(
    "Type a comma-separated list of gates. Examples: `H`, `X`, `Rx(pi/2)`, `Rz(90deg)`, `H, Rz(π/2), H`."
)

preset = st.segmented_control("Presets", ["None", "|0⟩", "|+⟩", "|i⟩"], selection_mode="single", key="preset")


def _preset_sequence(name: str) -> str:
    if name == "|0⟩":
        return "I"
    if name == "|+⟩":
        return "H"
    if name == "|i⟩":
        return "H, Rz(π/2)"
    return "H, Rz(pi/2), H"


default_sequence = _preset_sequence(preset)
user_input = st.text_input("Gate sequence", default_sequence, key="seq")


@st.cache_data(show_spinner=False)
def trajectory_for(seq_text: str) -> List[Tuple[float, float, float]]:
    gates = parse_gate_sequence(seq_text)
    coords: List[Tuple[float, float, float]] = []
    qc_inc = build_circuit([])
    for name, ang in gates:
        # Append one gate
        if name == "I":
            qc_inc.i(0)
        elif name == "H":
            qc_inc.h(0)
        elif name == "X":
            qc_inc.x(0)
        elif name == "Y":
            qc_inc.y(0)
        elif name == "Z":
            qc_inc.z(0)
        elif name == "RX":
            qc_inc.rx(float(ang), 0)  # type: ignore[arg-type]
        elif name == "RY":
            qc_inc.ry(float(ang), 0)  # type: ignore[arg-type]
        elif name == "RZ":
            qc_inc.rz(float(ang), 0)  # type: ignore[arg-type]
        sv = statevector_after(qc_inc)
        coords.append(state_to_bloch(sv))
    return coords


sequence: List[str] = [t.strip() for t in user_input.split(",") if t.strip()]
left, right = st.columns([2.5, 1])

with left:
    try:
        coords = trajectory_for(user_input)
        xs, ys, zs = zip(*coords) if coords else ([], [], [])
        fig = bloch_figure(list(xs), list(ys), list(zs), show_trail=True)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(str(exc))

with right:
    st.subheader("Final State Metrics")
    try:
        gates = parse_gate_sequence(user_input)
        qc = build_circuit(gates)
        sv = statevector_after(qc)
        x, y, z = state_to_bloch(sv)
        theta, phi = cartesian_to_spherical(x, y, z)
        st.metric("x", f"{x:.3f}")
        st.metric("y", f"{y:.3f}")
        st.metric("z", f"{z:.3f}")
        st.metric("θ (polar)", f"{theta:.3f} rad")
        st.metric("φ (azimuth)", f"{phi:.3f} rad")
        st.caption("θ = arccos(z), φ = atan2(y, x)")
    except Exception as exc:
        st.error(str(exc))
