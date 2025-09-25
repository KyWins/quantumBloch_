from __future__ import annotations

from typing import List

import streamlit as st
from qiskit import QuantumCircuit
import numpy as np

from utils.gate_utils import apply_gates, sequence_to_bloch_path, statevector_after, bloch_coordinates
from app.components import make_bloch_figure

st.set_page_config(page_title="Bloch Sphere Visualizer", layout="wide")

st.title("Bloch Sphere Visualizer")

st.markdown(
    "Type a comma-separated list of gates. Examples: `H`, `X`, `Rx(pi/2)`, `H, Rz(pi/2), H`."
)

default_sequence = "H, Rz(pi/2), H"
user_input = st.text_input("Gate sequence", default_sequence)
sequence: List[str] = [t.strip() for t in user_input.split(",") if t.strip()]

left, right = st.columns([2.5, 1])

with left:
    try:
        path = sequence_to_bloch_path(sequence)
        fig = make_bloch_figure(path, backend="plotly-anim")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(str(exc))

with right:
    st.subheader("Final State Metrics")
    if sequence:
        qc = apply_gates(QuantumCircuit(1), sequence)
        sv = statevector_after(qc)
        x, y, z = bloch_coordinates(sv)
        theta = float(np.arccos(max(-1.0, min(1.0, z))))
        phi = float(np.arctan2(y, x))
        st.metric("x", f"{x:.3f}")
        st.metric("y", f"{y:.3f}")
        st.metric("z", f"{z:.3f}")
        st.metric("θ (polar)", f"{theta:.3f} rad")
        st.metric("φ (azimuth)", f"{phi:.3f} rad")
        st.caption("θ = arccos(z), φ = atan2(y, x)")
    else:
        st.write("Enter gates to see the state metrics.")
