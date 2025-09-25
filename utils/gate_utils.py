from __future__ import annotations

from typing import List, Tuple, Optional

import math
import re
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


SUPPORTED_GATES = {"I", "X", "Y", "Z", "H", "S", "SDG", "T", "TDG", "RX", "RY", "RZ"}


def parse_gate_token(token: str) -> Tuple[str, float | None]:
    """Parse a gate token like 'H', 'X', 'Rx(pi/2)', 'Rz(1.5708)'.

    Returns (UPPERCASE gate_name, angle_radians_or_None).
    """
    token = token.strip()
    if "(" not in token:
        gate = token
        angle = None
    else:
        gate, arg = token.split("(", 1)
        arg = arg.rstrip(")").strip()
        angle = _parse_angle_to_radians(arg)
    gate = gate.strip().upper()
    if gate not in SUPPORTED_GATES:
        raise ValueError(f"Unsupported gate: {gate}")
    if gate in {"RX", "RY", "RZ"} and angle is None:
        raise ValueError(f"Rotation gate {gate} requires an angle, e.g., {gate}(pi/2)")
    return gate, angle


# Enhanced angle parsing -------------------------------------------------------
_PI_ALIASES = {"pi": math.pi, "π": math.pi}
_GATE_RX = re.compile(r"^(rx|ry|rz)\((.+)\)$", re.IGNORECASE)


def _parse_angle_to_radians(expr: str) -> float:
    """Parse expressions like 'pi', 'π/2', '2*pi/3', '1.234', '90deg', '-45deg'."""
    s = expr.strip()
    for name, value in _PI_ALIASES.items():
        s = re.sub(fr"(?i){name}", f"({value})", s)
    s = s.replace(" ", "")
    if s.lower().endswith("deg"):
        core = s[:-3]
        try:
            degrees = float(core)
        except ValueError as exc:
            raise ValueError(f"Invalid degree angle: {expr}") from exc
        return math.radians(degrees)
    try:
        return float(eval(s, {"__builtins__": {}}, {"math": math}))
    except Exception as exc:
        raise ValueError(f"Invalid angle expression: {expr}") from exc


# New parser that accepts a free-form sequence string -------------------------

def parse_gate_sequence(seq: str) -> List[Tuple[str, Optional[float]]]:
    """Parse a comma-separated sequence into normalized (UPPERCASE gate, angle) tuples."""
    tokens = [t.strip() for t in seq.split(",") if t.strip()]
    result: List[Tuple[str, Optional[float]]] = []
    for token in tokens:
        m = _GATE_RX.match(token)
        if m:
            gate = m.group(1).upper()
            angle = _parse_angle_to_radians(m.group(2))
            result.append((gate, float(angle)))
            continue
        up = token.upper()
        if up in {"H", "X", "Y", "Z", "I", "S", "SDG", "T", "TDG"}:
            result.append((up, None))
        else:
            raise ValueError(f"Unrecognized gate token: '{token}'")
    return result


def build_circuit(gates: List[Tuple[str, Optional[float]]], base: QuantumCircuit | None = None) -> QuantumCircuit:
    """Build a single-qubit circuit from parsed gate tuples.

    If base is provided, append to it in-place and return it; otherwise create a new circuit.
    """
    qc = base if base is not None else QuantumCircuit(1)
    for name, angle in gates:
        if name == "I":
            qc.i(0)
        elif name == "H":
            qc.h(0)
        elif name == "X":
            qc.x(0)
        elif name == "Y":
            qc.y(0)
        elif name == "Z":
            qc.z(0)
        elif name == "S":
            qc.s(0)
        elif name == "SDG":
            qc.sdg(0)
        elif name == "T":
            qc.t(0)
        elif name == "TDG":
            qc.tdg(0)
        elif name == "RX":
            qc.rx(float(angle), 0)  # type: ignore[arg-type]
        elif name == "RY":
            qc.ry(float(angle), 0)  # type: ignore[arg-type]
        elif name == "RZ":
            qc.rz(float(angle), 0)  # type: ignore[arg-type]
        else:
            raise ValueError(f"Unsupported gate: {name}")
    return qc


def prepare_initial_state(key: str) -> QuantumCircuit:
    """Return a circuit that prepares a chosen initial state on |0>.

    key in {"|0>", "|+>", "|i>"}
    |0>: default computational basis state
    |+>: H|0>
    |i>: S H |0> (global phase ignored)
    """
    qc = QuantumCircuit(1)
    if key == "|+>":
        qc.h(0)
    elif key == "|i>":
        qc.h(0)
        qc.s(0)
    return qc


# Backwards compatible helpers -------------------------------------------------

def apply_gates(circuit: QuantumCircuit, gates: List[str]) -> QuantumCircuit:
    """Apply a list of gate tokens to a single-qubit circuit in-place and return it."""
    if circuit.num_qubits != 1:
        raise ValueError("apply_gates expects a single-qubit circuit")
    for token in gates:
        name, angle = parse_gate_token(token)
        if name == "I":
            circuit.i(0)
        elif name == "X":
            circuit.x(0)
        elif name == "Y":
            circuit.y(0)
        elif name == "Z":
            circuit.z(0)
        elif name == "H":
            circuit.h(0)
        elif name == "RX":
            circuit.rx(angle, 0)  # type: ignore[arg-type]
        elif name == "RY":
            circuit.ry(angle, 0)  # type: ignore[arg-type]
        elif name == "RZ":
            circuit.rz(angle, 0)  # type: ignore[arg-type]
        elif name == "S":
            circuit.s(0)
        elif name == "SDG":
            circuit.sdg(0)
        elif name == "T":
            circuit.t(0)
        elif name == "TDG":
            circuit.tdg(0)
        else:
            raise ValueError(f"Unsupported gate encountered: {name}")
    return circuit


def statevector_after(circuit: QuantumCircuit) -> Statevector:
    """Return the final statevector for a single-qubit circuit, no simulator backend."""
    if circuit.num_qubits != 1:
        raise ValueError("statevector_after expects a single-qubit circuit")
    return Statevector.from_label("0").evolve(circuit)


def bloch_coordinates(state: Statevector) -> Tuple[float, float, float]:
    """Compute Bloch vector coordinates (x, y, z) from a single-qubit statevector.

    Delegates to state_to_bloch for numerical stability and consistency.
    """
    if state.num_qubits != 1:
        raise ValueError("bloch_coordinates expects a single-qubit statevector")
    return state_to_bloch(state)


def sequence_to_bloch_path(gates: List[str]) -> List[Tuple[float, float, float]]:
    """Return Bloch coordinates after each prefix of the sequence, starting from |0>."""
    circ = QuantumCircuit(1)
    path: List[Tuple[float, float, float]] = []
    for idx in range(len(gates)):
        circ = apply_gates(QuantumCircuit(1), gates[:idx + 1])
        sv = statevector_after(circ)
        path.append(bloch_coordinates(sv))
    return path


# Numerically stable state->Bloch and metrics ---------------------------------

def state_to_bloch(state: np.ndarray | Statevector) -> Tuple[float, float, float]:
    """Convert a statevector (array or Statevector) into (x, y, z) Bloch coords.

    Uses Pauli expectations; clamps tiny numerical drift to [-1, 1].
    """
    if isinstance(state, Statevector):
        sv = state
    else:
        arr = np.asarray(state, dtype=complex)
        if arr.ndim != 1 or arr.size != 2:
            raise ValueError("state_to_bloch expects a size-2 statevector")
        # Normalize defensively
        norm = np.linalg.norm(arr)
        if norm == 0:
            raise ValueError("Zero statevector")
        sv = Statevector(arr / norm)
    rho = np.outer(sv.data, sv.data.conjugate())
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    x = float(np.real(np.trace(rho @ sx)))
    y = float(np.real(np.trace(rho @ sy)))
    z = float(np.real(np.trace(rho @ sz)))
    def clamp(u: float) -> float:
        return max(-1.0, min(1.0, u))
    return clamp(x), clamp(y), clamp(z)


def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float]:
    """Return (theta, phi) for the 3D unit vector.

    theta: polar angle from +Z in [0, pi]; phi: azimuth from +X in (-pi, pi].
    """
    r = max(1e-12, math.sqrt(x * x + y * y + z * z))
    theta = math.acos(max(-1.0, min(1.0, z / r)))
    phi = math.atan2(y, x)
    return theta, phi
