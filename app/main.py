from __future__ import annotations

from typing import Optional

import numpy as np
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from utils.gate_utils import (
    GateParseError,
    SimulationResult,
    cartesian_to_spherical,
    simulate_sequence,
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


def _initial_preset_key(name: str) -> str:
    if name.startswith("|+⟩"):
        return "|+>"
    if name.startswith("|i⟩"):
        return "|i>"
    return "|0>"


def _format_gate(gate: tuple[str, Optional[float]]) -> str:
    name, angle = gate
    return f"{name}({angle:.6f})" if angle is not None else name


def _state_probabilities(state: tuple[complex, complex]) -> tuple[float, float]:
    p0 = float(abs(state[0]) ** 2)
    p1 = float(abs(state[1]) ** 2)
    return p0, p1


@st.cache_data(show_spinner=False)
def cached_simulation(initial: str, seq_text: str) -> SimulationResult:
    return simulate_sequence(initial, seq_text)


qp_preset = _qp_get("preset", "|0⟩")
qp_seq = _qp_get("seq", "")

preset = st.radio(
    "Initial state preset",
    ["|0⟩ (default)", "|+⟩", "|i⟩"],
    horizontal=True,
    key="preset",
    index={"|0⟩": 0, "|+⟩": 1, "|i⟩": 2}.get(qp_preset, 0),
)

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

simulation: Optional[SimulationResult] = None
parse_error: Optional[GateParseError] = None
generic_error: Optional[Exception] = None

try:
    simulation = cached_simulation(init_key, user_input)
except GateParseError as err:
    parse_error = err
    simulation = cached_simulation(init_key, "")
except Exception as err:  # pragma: no cover - defensive
    generic_error = err
    simulation = cached_simulation(init_key, "")

if parse_error:
    token_pos = f"token #{parse_error.index + 1}" if parse_error.index is not None else "token"
    st.error(f"{parse_error}\nCheck {token_pos}: `{parse_error.token}`.")
    st.info("Showing the prepared preset until the sequence parses successfully.")

if generic_error:
    st.error(f"Simulation error: {generic_error}")

if simulation is None:
    st.stop()

coords = list(simulation.coordinates)
states = list(simulation.states)
gates = list(simulation.gates)
num_steps = len(coords)

if num_steps == 0:
    st.warning("Unable to prepare the preset state. Please try again.")
    st.stop()

# Reset measurement overlays if the underlying simulation changed
signature = (init_key, user_input.strip())
if st.session_state.get("_simulation_signature") != signature:
    st.session_state["_simulation_signature"] = signature
    st.session_state.pop("measurement_counts", None)
    st.session_state.pop("overlay_point", None)
    st.session_state.pop("overlay_step", None)

# Keep selected step stateful across reruns
if "selected_step" not in st.session_state:
    st.session_state["selected_step"] = num_steps - 1
else:
    st.session_state["selected_step"] = max(0, min(num_steps - 1, st.session_state["selected_step"]))

selected_step = st.session_state["selected_step"]
selected_coord = coords[selected_step]
selected_state = states[selected_step]
selected_theta, selected_phi = cartesian_to_spherical(*selected_coord)
selected_p0, selected_p1 = _state_probabilities(selected_state)

final_coord = coords[-1]
final_state = states[-1]
final_theta, final_phi = cartesian_to_spherical(*final_coord)
final_p0, final_p1 = _state_probabilities(final_state)

snapshot_cols = st.columns(4)
snapshot_cols[0].metric("Selected step", str(selected_step))
snapshot_cols[1].metric("Selected x", f"{selected_coord[0]:.3f}")
snapshot_cols[2].metric("Selected y", f"{selected_coord[1]:.3f}")
snapshot_cols[3].metric("Selected z", f"{selected_coord[2]:.3f}")

final_cols = st.columns(4)
final_cols[0].metric("Final |0⟩", f"{final_p0:.3f}")
final_cols[1].metric("Final |1⟩", f"{final_p1:.3f}")
final_cols[2].metric("θ final (rad)", f"{final_theta:.3f}")
final_cols[3].metric("Total gates", len(gates))

st.divider()

timeline_rows = [
    {
        "Step": 0,
        "Description": "Prepared preset",
        "Gate": "—",
        "Angle (rad)": "",
        "x": coords[0][0],
        "y": coords[0][1],
        "z": coords[0][2],
        "|0⟩": _state_probabilities(states[0])[0],
        "|1⟩": _state_probabilities(states[0])[1],
    }
]
for idx, gate in enumerate(gates, start=1):
    coord = coords[idx]
    probs = _state_probabilities(states[idx])
    angle_rad = gate[1]
    timeline_rows.append(
        {
            "Step": idx,
            "Description": f"After {_format_gate(gate)}",
            "Gate": gate[0],
            "Angle (rad)": f"{angle_rad:.4f}" if angle_rad is not None else "—",
            "x": coord[0],
            "y": coord[1],
            "z": coord[2],
            "|0⟩": probs[0],
            "|1⟩": probs[1],
        }
    )
timeline_df = pd.DataFrame(timeline_rows)

# Two-column layout: visualization + controls
layout_left, layout_right = st.columns([2.2, 1.5], vertical_alignment="top")

with layout_left:
    trajectory_tab, timeline_tab = st.tabs(["Bloch sphere", "Gate timeline"])

    with trajectory_tab:
        overlay_point = None
        overlay_state = st.session_state.get("overlay_point")
        overlay_step = st.session_state.get("overlay_step")
        if overlay_state is not None and overlay_step == selected_step:
            overlay_point = overlay_state

        try:
            if make_bloch_figure is not None:
                rendered = make_bloch_figure(
                    coords,
                    backend=backend,
                    context={
                        "overlay_point": overlay_point,
                        "selected_index": selected_step,
                        "selected_point": selected_coord,
                        "selected_theta": selected_theta,
                        "selected_phi": selected_phi,
                    },
                )
                if hasattr(rendered, "to_plotly_json") or hasattr(rendered, "to_dict"):
                    st.plotly_chart(rendered, use_container_width=True)
                else:
                    st.write(rendered)
            else:
                raise RuntimeError("Visualizer registry unavailable")
        except Exception as be:
            xs, ys, zs = zip(*coords) if coords else ([], [], [])
            highlight = coords[selected_step] if coords else None
            fig = bloch_figure(
                list(xs),
                list(ys),
                list(zs),
                show_trail=True,
                highlight_point=highlight,
                overlay_point=overlay_point,
                selected_theta=selected_theta,
                selected_phi=selected_phi,
            )
            st.info(f"Backend '{backend}' unavailable, falling back to Plotly. ({be})")
            st.plotly_chart(fig, use_container_width=True)

        if num_steps > 1:
            st.slider(
                "Trajectory step",
                min_value=0,
                max_value=num_steps - 1,
                help="0 = prepared preset, subsequent steps follow the gate list.",
                key="selected_step",
            )
        else:
            st.caption("Only the prepared preset is available (no gates applied).")

        step_label = "Initial state"
        if selected_step > 0 and selected_step - 1 < len(gates):
            step_label = f"After {_format_gate(gates[selected_step - 1])}"
        st.caption(f"Viewing: {step_label}")

    with timeline_tab:
        if timeline_df.empty:
            st.info("No data available.")
        else:
            styled = timeline_df.round({"x": 3, "y": 3, "z": 3, "|0⟩": 3, "|1⟩": 3})

            def highlight_row(row: pd.Series) -> list[str]:
                return ["background-color: #f0f4ff" if int(row["Step"]) == selected_step else "" for _ in row]

            st.dataframe(
                styled.style.apply(highlight_row, axis=1),
                use_container_width=True,
            )

with layout_right:
    details_tab, measurements_tab = st.tabs(["State details", "Measurement lab"])

    with details_tab:
        st.markdown("#### Selected step")
        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.metric("x", f"{selected_coord[0]:.3f}")
            st.metric("|0⟩ probability", f"{selected_p0:.3f}")
        with detail_cols[1]:
            st.metric("y", f"{selected_coord[1]:.3f}")
            st.metric("|1⟩ probability", f"{selected_p1:.3f}")
        st.metric("z", f"{selected_coord[2]:.3f}")
        st.caption(f"θ = {selected_theta:.3f} rad, φ = {selected_phi:.3f} rad")

        st.divider()
        st.markdown("#### Final state")
        final_cols_detail = st.columns(2)
        with final_cols_detail[0]:
            st.metric("x", f"{final_coord[0]:.3f}")
            st.metric("|0⟩ probability", f"{final_p0:.3f}")
        with final_cols_detail[1]:
            st.metric("y", f"{final_coord[1]:.3f}")
            st.metric("|1⟩ probability", f"{final_p1:.3f}")
        st.metric("z", f"{final_coord[2]:.3f}")
        st.caption(f"θ = {final_theta:.3f} rad, φ = {final_phi:.3f} rad")

        if gates:
            with st.expander("Parsed gates (normalized)"):
                for idx, gate in enumerate(gates, start=1):
                    st.write(f"{idx}. {_format_gate(gate)}")

    with measurements_tab:
        st.markdown("#### Sampling controls")
        ctrl_cols = st.columns(2)
        single_shot = ctrl_cols[0].button("Sample single shot", use_container_width=True)
        clear_overlay = ctrl_cols[1].button("Clear overlays", use_container_width=True)

        if clear_overlay:
            st.session_state.pop("overlay_point", None)
            st.session_state.pop("overlay_step", None)
            st.session_state.pop("measurement_counts", None)

        shots = st.slider(
            "Multi-shot simulation",
            min_value=1,
            max_value=2048,
            value=256,
            help="Simulate projective measurement counts.",
            key="shots_slider",
        )
        multi_button = st.button("Run multi-shot simulation", use_container_width=True)

        rng = np.random.default_rng()

        if single_shot:
            outcome = "|0⟩" if rng.random() < selected_p0 else "|1⟩"
            collapsed = (0.0, 0.0, 1.0) if outcome == "|0⟩" else (0.0, 0.0, -1.0)
            st.session_state["overlay_point"] = collapsed
            st.session_state["overlay_step"] = selected_step
            st.toast(f"Measured {outcome} at step {selected_step}", icon="✅")

        if multi_button:
            counts = rng.multinomial(shots, [selected_p0, selected_p1])
            st.session_state["measurement_counts"] = {
                "shots": shots,
                "counts": {"|0⟩": int(counts[0]), "|1⟩": int(counts[1])},
                "step": selected_step,
                "probabilities": {"|0⟩": selected_p0, "|1⟩": selected_p1},
            }

        measurement_counts = st.session_state.get("measurement_counts")
        if measurement_counts and measurement_counts.get("step") == selected_step:
            counts = measurement_counts["counts"]
            shots_total = measurement_counts["shots"]
            expected = [shots_total * selected_p0, shots_total * selected_p1]
            fig_counts = go.Figure()
            fig_counts.add_trace(
                go.Bar(
                    name="Measured",
                    x=list(counts.keys()),
                    y=list(counts.values()),
                    marker_color="#2ca02c",
                )
            )
            fig_counts.add_trace(
                go.Bar(
                    name="Expected",
                    x=["|0⟩", "|1⟩"],
                    y=expected,
                    marker_color="#1f77b4",
                    opacity=0.6,
                )
            )
            fig_counts.update_layout(
                barmode="group",
                yaxis_title="Counts",
                legend_orientation="h",
                legend_y=-0.2,
                margin=dict(l=0, r=0, b=0, t=10),
            )
            st.plotly_chart(fig_counts, use_container_width=True)
            count_cols = st.columns(2)
            count_cols[0].metric("|0⟩ counts", counts["|0⟩"])
            count_cols[1].metric("|1⟩ counts", counts["|1⟩"])
            st.caption(f"Step {selected_step}: {counts['|0⟩']}×|0⟩, {counts['|1⟩']}×|1⟩ out of {shots_total} shots.")
        else:
            st.info("Run a multi-shot simulation to see histograms and counts.")
